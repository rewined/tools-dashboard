"""
Wick Predictor Module - Core logic for wick recommendation system
Implements majority vote, wax conversion heuristics, and ML-based predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import joblib
import os

@dataclass
class WickRecommendation:
    """Data class for wick recommendations"""
    wick_id: str
    wick_name: str
    confidence: float
    reasoning: str
    rank: int

@dataclass
class TestPriority:
    """Data class for test prioritization"""
    assembly_id: str
    assembly_name: str
    uncertainty_score: float
    information_gain: float
    reason: str

class WickPredictor:
    """Main class for wick prediction and recommendation"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.model = None
        self.model_version = None
        self._load_latest_model()
    
    def _load_latest_model(self):
        """Load the latest trained ML model if available"""
        model_path = os.path.join('models', 'wick_predictor_latest.pkl')
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.model_version = datetime.fromfile(model_path).strftime('%Y%m%d_%H%M%S')
            except:
                self.model = None
                self.model_version = None
    
    def get_majority_vote_recommendation(self, vessel_id: str, wax_type_id: str) -> Optional[WickRecommendation]:
        """Get baseline recommendation using majority vote from historical data"""
        try:
            # Query the materialized view
            result = self.supabase.table('wick_majority_baseline') \
                .select('*') \
                .eq('vessel_id', vessel_id) \
                .eq('wax_type_id', wax_type_id) \
                .single() \
                .execute()
            
            if result.data:
                wick_id = result.data['recommended_wick']
                sample_size = result.data['sample_size']
                
                # Get wick details
                wick = self.supabase.table('wicks') \
                    .select('*') \
                    .eq('id', wick_id) \
                    .single() \
                    .execute()
                
                confidence = min(0.95, 0.5 + (sample_size * 0.05))  # Cap at 95%
                
                return WickRecommendation(
                    wick_id=wick_id,
                    wick_name=wick.data['name'],
                    confidence=confidence,
                    reasoning=f"Based on {sample_size} successful historical uses with this vessel and wax combination",
                    rank=1
                )
        except:
            return None
    
    def get_wax_conversion_recommendation(self, vessel_id: str, old_wax_id: str, 
                                        new_wax_id: str, current_wick_id: str) -> Optional[WickRecommendation]:
        """Get recommendation for wax conversion using learned deltas"""
        try:
            # Get the conversion delta
            delta_result = self.supabase.rpc('get_wax_conversion_delta', {
                'p_vessel_id': vessel_id,
                'p_old_wax_id': old_wax_id,
                'p_new_wax_id': new_wax_id
            }).execute()
            
            if delta_result.data and delta_result.data != 0:
                delta = delta_result.data
                
                # Get current wick details
                current_wick = self.supabase.table('wicks') \
                    .select('*') \
                    .eq('id', current_wick_id) \
                    .single() \
                    .execute()
                
                current_size_index = current_wick.data['size_index']
                new_size_index = current_size_index + delta
                
                # Find wick with closest size index in same series
                new_wick = self.supabase.table('wicks') \
                    .select('*') \
                    .eq('series', current_wick.data['series']) \
                    .order('size_index') \
                    .execute()
                
                # Find closest match
                closest_wick = min(new_wick.data, 
                                 key=lambda w: abs(w['size_index'] - new_size_index))
                
                # Get conversion confidence
                conv_data = self.supabase.table('wax_conversion_deltas') \
                    .select('confidence_score, sample_count') \
                    .eq('vessel_id', vessel_id) \
                    .eq('old_wax_type_id', old_wax_id) \
                    .eq('new_wax_type_id', new_wax_id) \
                    .single() \
                    .execute()
                
                return WickRecommendation(
                    wick_id=closest_wick['id'],
                    wick_name=closest_wick['name'],
                    confidence=conv_data.data['confidence_score'],
                    reasoning=f"Wax conversion heuristic: {'+' if delta > 0 else ''}{delta} sizes based on {conv_data.data['sample_count']} tests",
                    rank=1
                )
        except:
            return None
    
    def get_assembly_based_recommendations(self, vessel_id: str, wax_type_id: str, 
                                         fragrance_id: str, netsuite_client = None) -> List[WickRecommendation]:
        """Get recommendations based on existing NetSuite assembly combinations"""
        recommendations = []
        
        if not netsuite_client or not netsuite_client.is_configured:
            return recommendations
        
        try:
            # Get all assembly items that might match our criteria
            assemblies = netsuite_client.get_assembly_items()
            
            if not assemblies:
                return recommendations
            
            # Get vessel, wax, and fragrance names for matching
            vessel_name = self._get_item_name_by_id(vessel_id, 'vessels')
            wax_name = self._get_item_name_by_id(wax_type_id, 'wax_types')  
            fragrance_name = self._get_item_name_by_id(fragrance_id, 'fragrance_oils')
            
            if not all([vessel_name, wax_name, fragrance_name]):
                return recommendations
            
            # Look for assembly combinations and extract wick patterns
            proven_wicks = self._analyze_assembly_combinations(
                assemblies, vessel_name, wax_name, fragrance_name
            )
            
            # Convert proven combinations to recommendations
            for wick_data in proven_wicks:
                # Create high-confidence recommendation for proven combinations
                recommendation = WickRecommendation(
                    wick_id=wick_data['wick_id'],
                    wick_name=wick_data['wick_name'], 
                    confidence=wick_data['confidence'],
                    reasoning=wick_data['reasoning'],
                    rank=len(recommendations) + 1
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"Error in assembly-based recommendations: {e}")
            return recommendations
    
    def _get_item_name_by_id(self, item_id: str, table_name: str) -> Optional[str]:
        """Get item name from Supabase by ID"""
        try:
            result = self.supabase.table(table_name).select('name').eq('id', item_id).single().execute()
            return result.data['name'] if result.data else None
        except:
            return None
    
    def _analyze_assembly_combinations(self, assemblies: List[Dict], vessel_name: str, 
                                     wax_name: str, fragrance_name: str) -> List[Dict]:
        """Analyze assembly items to find proven wick combinations"""
        proven_wicks = []
        
        # Keywords for matching components in assembly names/descriptions
        vessel_keywords = self._extract_keywords(vessel_name)
        fragrance_keywords = self._extract_keywords(fragrance_name)
        
        for assembly in assemblies:
            assembly_name = assembly.get('displayname', '').lower()
            assembly_itemid = assembly.get('itemid', '').lower()
            oz_fill = assembly.get('oz_fill')
            
            # Check if this assembly matches our vessel and fragrance
            vessel_match = any(keyword in assembly_name or keyword in assembly_itemid 
                             for keyword in vessel_keywords)
            fragrance_match = any(keyword in assembly_name or keyword in assembly_itemid 
                                for keyword in fragrance_keywords)
            
            if vessel_match and fragrance_match:
                # This assembly uses our vessel + fragrance combination
                # Extract wick information from the assembly name/ID
                extracted_wicks = self._extract_wick_from_assembly(assembly)
                
                for wick_info in extracted_wicks:
                    # Calculate confidence based on match quality
                    confidence = self._calculate_assembly_confidence(
                        vessel_match, fragrance_match, oz_fill, assembly
                    )
                    
                    proven_wicks.append({
                        'wick_id': wick_info['wick_id'],
                        'wick_name': wick_info['wick_name'],
                        'confidence': confidence,
                        'reasoning': f"Proven combination from assembly {assembly.get('itemid', '')} - same vessel and fragrance"
                    })
        
        # Remove duplicates and sort by confidence
        unique_wicks = []
        seen_wicks = set()
        
        for wick in sorted(proven_wicks, key=lambda x: x['confidence'], reverse=True):
            if wick['wick_id'] not in seen_wicks:
                unique_wicks.append(wick)
                seen_wicks.add(wick['wick_id'])
        
        return unique_wicks[:6]  # Return top 6 proven combinations
    
    def _extract_keywords(self, name: str) -> List[str]:
        """Extract searchable keywords from item names"""
        if not name:
            return []
        
        # Remove common prefixes and clean up
        name = name.lower()
        name = name.replace('ves-', '').replace('oil-', '').replace('fo-', '').replace('frag-', '')
        
        # Split by common separators and filter short words
        keywords = []
        for word in name.replace('-', ' ').replace('_', ' ').split():
            if len(word) >= 3:  # Only words with 3+ characters
                keywords.append(word.strip())
        
        return keywords
    
    def _extract_wick_from_assembly(self, assembly: Dict) -> List[Dict]:
        """Extract wick information from assembly name/ID"""
        # This would need to be enhanced based on your actual assembly naming conventions
        # For now, return a placeholder that would be filled by actual NetSuite BOM analysis
        
        assembly_name = assembly.get('displayname', '').lower()
        assembly_itemid = assembly.get('itemid', '').lower()
        
        # Look for common wick patterns in assembly names
        import re
        wick_patterns = [
            r'cd[-\s]*(\d+)',  # CD-6, CD 6, etc.
            r'eco[-\s]*(\d+)', # ECO-4, ECO 4, etc.
            r'lx[-\s]*(\d+)',  # LX-10, LX 10, etc.
            r'htp[-\s]*(\d+)', # HTP-8, HTP 8, etc.
        ]
        
        extracted_wicks = []
        text_to_search = f"{assembly_name} {assembly_itemid}"
        
        for pattern in wick_patterns:
            matches = re.findall(pattern, text_to_search)
            for match in matches:
                wick_type = pattern.split('(')[0].replace('[-\\s]*', '').upper()
                wick_name = f"{wick_type}-{match}"
                
                extracted_wicks.append({
                    'wick_id': f"wick_{wick_name.lower().replace('-', '_')}",
                    'wick_name': wick_name
                })
        
        # If no specific wick found, this assembly may need BOM analysis
        if not extracted_wicks:
            # Placeholder for BOM-based wick extraction
            pass
        
        return extracted_wicks
    
    def _calculate_assembly_confidence(self, vessel_match: bool, fragrance_match: bool, 
                                     oz_fill: float, assembly: Dict) -> float:
        """Calculate confidence score for assembly-based recommendations"""
        base_confidence = 0.95  # Very high for proven combinations
        
        # Adjust based on match quality
        if vessel_match and fragrance_match:
            confidence = base_confidence
        elif vessel_match or fragrance_match:
            confidence = base_confidence * 0.8
        else:
            confidence = base_confidence * 0.6
        
        # Boost confidence if we have oz_fill data (more precise match)
        if oz_fill:
            confidence = min(0.98, confidence + 0.05)
        
        return confidence
    
    def calculate_heat_index_adjustment(self, fragrance_id: str) -> int:
        """Calculate wick size adjustment based on fragrance heat index"""
        try:
            # Get fragrance heat index
            fragrance = self.supabase.table('fragrance_oils') \
                .select('heat_index, density_rating') \
                .eq('id', fragrance_id) \
                .single() \
                .execute()
            
            if not fragrance.data:
                return 0
            
            heat_index = fragrance.data.get('heat_index', 0)
            density = fragrance.data.get('density_rating', 'medium')
            
            # Categorize heat index
            adjustment = 0
            if heat_index < -0.5:  # Cool burning
                adjustment = 1  # Need larger wick
            elif heat_index > 0.5:  # Hot burning
                adjustment = -1  # Need smaller wick
            
            # Additional adjustment for density
            if density == 'heavy':
                adjustment += 1
            elif density == 'light':
                adjustment -= 0
            
            return adjustment
        except:
            return 0
    
    def get_ml_predictions(self, vessel_id: str, wax_type_id: str, 
                          fragrance_id: str, fragrance_load: float) -> List[WickRecommendation]:
        """Get ML-based predictions if model is available"""
        if not self.model:
            return []
        
        try:
            # Prepare features
            features = self._prepare_features(vessel_id, wax_type_id, fragrance_id, fragrance_load)
            
            # Get predictions with probabilities
            predictions = self.model.predict_proba([features])[0]
            
            # Get top 5 predictions
            top_indices = np.argsort(predictions)[-5:][::-1]
            recommendations = []
            
            for i, idx in enumerate(top_indices):
                if predictions[idx] > 0.1:  # Only include if >10% probability
                    wick_id = self.model.classes_[idx]
                    wick = self.supabase.table('wicks') \
                        .select('name') \
                        .eq('id', wick_id) \
                        .single() \
                        .execute()
                    
                    recommendations.append(WickRecommendation(
                        wick_id=wick_id,
                        wick_name=wick.data['name'],
                        confidence=predictions[idx],
                        reasoning=f"ML model prediction (v{self.model_version})",
                        rank=i + 1
                    ))
            
            return recommendations
        except:
            return []
    
    def _prepare_features(self, vessel_id: str, wax_type_id: str, 
                         fragrance_id: str, fragrance_load: float) -> np.ndarray:
        """Prepare feature vector for ML model"""
        # Get vessel features
        vessel = self.supabase.table('vessels') \
            .select('*') \
            .eq('id', vessel_id) \
            .single() \
            .execute().data
        
        # Get wax features
        wax = self.supabase.table('wax_types') \
            .select('*') \
            .eq('id', wax_type_id) \
            .single() \
            .execute().data
        
        # Get fragrance features
        fragrance = self.supabase.table('fragrance_oils') \
            .select('*') \
            .eq('id', fragrance_id) \
            .single() \
            .execute().data
        
        # Create feature vector
        features = [
            vessel.get('volume_ml', 0),
            vessel.get('diameter_mm', 0),
            vessel.get('height_mm', 0),
            1 if vessel.get('double_wick', False) else 0,
            vessel.get('heat_dissipation_factor', 1.0),
            wax.get('melt_point_celsius', 0),
            wax.get('viscosity_index', 0),
            fragrance.get('flash_point_celsius', 0),
            fragrance.get('heat_index', 0),
            fragrance_load
        ]
        
        return np.array(features)
    
    def get_comprehensive_recommendations(self, vessel_id: str, wax_type_id: str,
                                        fragrance_id: str, fragrance_load: float,
                                        old_wax_id: Optional[str] = None,
                                        current_wick_id: Optional[str] = None,
                                        netsuite_client = None) -> List[WickRecommendation]:
        """Get comprehensive recommendations combining all methods"""
        recommendations = []
        
        # 1. Try assembly-based recommendations (highest priority)
        assembly_recs = self.get_assembly_based_recommendations(
            vessel_id, wax_type_id, fragrance_id, netsuite_client
        )
        recommendations.extend(assembly_recs)
        
        # 2. Try majority vote baseline
        majority_rec = self.get_majority_vote_recommendation(vessel_id, wax_type_id)
        if majority_rec:
            recommendations.append(majority_rec)
        
        # 3. Try wax conversion if applicable
        if old_wax_id and current_wick_id:
            conversion_rec = self.get_wax_conversion_recommendation(
                vessel_id, old_wax_id, wax_type_id, current_wick_id
            )
            if conversion_rec:
                recommendations.append(conversion_rec)
        
        # 4. Get ML predictions
        ml_recs = self.get_ml_predictions(vessel_id, wax_type_id, fragrance_id, fragrance_load)
        recommendations.extend(ml_recs)
        
        # 4. Apply heat index adjustments to all recommendations
        heat_adjustment = self.calculate_heat_index_adjustment(fragrance_id)
        
        if heat_adjustment != 0:
            adjusted_recs = []
            for rec in recommendations:
                # Get wick details
                wick = self.supabase.table('wicks') \
                    .select('*') \
                    .eq('id', rec.wick_id) \
                    .single() \
                    .execute().data
                
                # Find adjusted wick
                target_index = wick['size_index'] + heat_adjustment
                adjusted_wick = self.supabase.table('wicks') \
                    .select('*') \
                    .eq('series', wick['series']) \
                    .order('size_index') \
                    .execute().data
                
                closest = min(adjusted_wick, key=lambda w: abs(w['size_index'] - target_index))
                
                adjusted_recs.append(WickRecommendation(
                    wick_id=closest['id'],
                    wick_name=closest['name'],
                    confidence=rec.confidence * 0.9,  # Slightly lower confidence for adjusted
                    reasoning=f"{rec.reasoning} + heat index adjustment ({'+' if heat_adjustment > 0 else ''}{heat_adjustment})",
                    rank=rec.rank
                ))
            
            recommendations = adjusted_recs
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda r: r.confidence, reverse=True):
            if rec.wick_id not in seen:
                seen.add(rec.wick_id)
                unique_recs.append(rec)
        
        # Re-rank
        for i, rec in enumerate(unique_recs):
            rec.rank = i + 1
        
        return unique_recs[:8]  # Return top 8
    
    def get_test_priorities(self, limit: int = 20) -> List[TestPriority]:
        """Get prioritized list of assemblies to test using active learning"""
        try:
            # Get pending predictions with low confidence
            uncertain = self.supabase.table('wick_predictions') \
                .select('*, assemblies(*)') \
                .eq('verified', False) \
                .lt('confidence_score', 0.6) \
                .order('confidence_score') \
                .limit(limit) \
                .execute()
            
            priorities = []
            for pred in uncertain.data:
                assembly = pred['assemblies']
                
                # Calculate information gain estimate
                # Higher for popular vessels/waxes with little data
                info_gain = self._estimate_information_gain(
                    assembly['vessel_id'],
                    assembly['wax_type_id'],
                    pred['confidence_score']
                )
                
                priorities.append(TestPriority(
                    assembly_id=assembly['id'],
                    assembly_name=assembly['name'],
                    uncertainty_score=1 - pred['confidence_score'],
                    information_gain=info_gain,
                    reason=f"Low confidence ({pred['confidence_score']:.1%}) prediction needs verification"
                ))
            
            # Sort by information gain
            priorities.sort(key=lambda p: p.information_gain, reverse=True)
            
            return priorities
        except:
            return []
    
    def _estimate_information_gain(self, vessel_id: str, wax_type_id: str, 
                                  current_confidence: float) -> float:
        """Estimate information gain from testing this combination"""
        # Count how many other assemblies share this vessel/wax
        similar = self.supabase.table('assemblies') \
            .select('id', count='exact') \
            .eq('vessel_id', vessel_id) \
            .eq('wax_type_id', wax_type_id) \
            .execute()
        
        similar_count = similar.count if similar.count else 1
        
        # Information gain is higher for:
        # - Lower current confidence
        # - More assemblies that would benefit
        info_gain = (1 - current_confidence) * np.log(similar_count + 1)
        
        return info_gain
    
    def record_test_result(self, assembly_id: str, wick_id_tested: str,
                          test_data: Dict, passed: bool) -> None:
        """Record a new test result and update predictions"""
        # Insert test result
        self.supabase.table('test_results').insert({
            'assembly_id': assembly_id,
            'wick_id_tested': wick_id_tested,
            'test_date': datetime.now().isoformat(),
            'test_type': test_data.get('test_type', 'quality_check'),
            'flame_height_mm': test_data.get('flame_height_mm'),
            'melt_pool_mm_at_2h': test_data.get('melt_pool_mm_at_2h'),
            'pass': passed,
            'notes': test_data.get('notes'),
            'tested_by': test_data.get('tested_by')
        }).execute()
        
        # Update any predictions for this assembly
        self.supabase.table('wick_predictions') \
            .update({
                'verified': True,
                'verification_date': datetime.now().isoformat(),
                'actual_wick_id': wick_id_tested if passed else None
            }) \
            .eq('assembly_id', assembly_id) \
            .execute()
        
        # Remove from priority queue
        self.supabase.table('test_priority_queue') \
            .update({
                'completed': True,
                'completed_date': datetime.now().isoformat()
            }) \
            .eq('assembly_id', assembly_id) \
            .execute()