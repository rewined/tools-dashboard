"""
Wick-onomics API endpoints for Flask application
Provides REST API for wick predictions, test management, and analytics
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import os
from supabase import create_client, Client
from .wick_predictor import WickPredictor
from .wick_ml_trainer import WickMLTrainer

# Create blueprint
wick_api = Blueprint('wick_api', __name__, url_prefix='/api/wick')

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url else None

# Initialize predictor
predictor = WickPredictor(supabase) if supabase else None

@wick_api.route('/predict', methods=['POST'])
def predict_wick():
    """
    Predict optimal wick for given parameters
    
    Request body:
    {
        "vessel_id": "123",
        "wax_type_id": "456", 
        "fragrance_id": "789",
        "fragrance_load": 8.5,
        "old_wax_id": "111" (optional),
        "current_wick_id": "222" (optional)
    }
    """
    try:
        if not predictor:
            return jsonify({'error': 'Prediction service not available'}), 503
        
        data = request.get_json()
        
        # Validate required fields
        required = ['vessel_id', 'wax_type_id', 'fragrance_id', 'fragrance_load']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get recommendations
        recommendations = predictor.get_comprehensive_recommendations(
            vessel_id=data['vessel_id'],
            wax_type_id=data['wax_type_id'],
            fragrance_id=data['fragrance_id'],
            fragrance_load=float(data['fragrance_load']),
            old_wax_id=data.get('old_wax_id'),
            current_wick_id=data.get('current_wick_id')
        )
        
        # Store prediction for tracking
        if recommendations:
            top_rec = recommendations[0]
            supabase.table('wick_predictions').insert({
                'vessel_id': data['vessel_id'],
                'wax_type_id': data['wax_type_id'],
                'fragrance_id': data['fragrance_id'],
                'fragrance_load_percentage': data['fragrance_load'],
                'predicted_wick_id': top_rec.wick_id,
                'confidence_score': top_rec.confidence,
                'model_version': predictor.model_version or 'heuristic_v1'
            }).execute()
        
        # Format response
        return jsonify({
            'success': True,
            'recommendations': [
                {
                    'wick_id': rec.wick_id,
                    'wick_name': rec.wick_name,
                    'confidence': round(rec.confidence, 3),
                    'reasoning': rec.reasoning,
                    'rank': rec.rank
                }
                for rec in recommendations
            ],
            'needs_testing': recommendations[0].confidence < 0.6 if recommendations else True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/test-priorities', methods=['GET'])
def get_test_priorities():
    """Get prioritized list of assemblies that need testing"""
    try:
        if not predictor:
            return jsonify({'error': 'Prediction service not available'}), 503
        
        limit = request.args.get('limit', 20, type=int)
        priorities = predictor.get_test_priorities(limit)
        
        return jsonify({
            'success': True,
            'count': len(priorities),
            'priorities': [
                {
                    'assembly_id': p.assembly_id,
                    'assembly_name': p.assembly_name,
                    'uncertainty_score': round(p.uncertainty_score, 3),
                    'information_gain': round(p.information_gain, 3),
                    'reason': p.reason
                }
                for p in priorities
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/log-test', methods=['POST'])
def log_test_result():
    """
    Log a test result and update predictions
    
    Request body:
    {
        "assembly_id": "123",
        "wick_tested": "ECO-10",
        "flame_height_mm": 35,
        "melt_pool_mm_2h": 45,
        "pass": true,
        "notes": "Good burn, slight mushrooming",
        "tested_by": "lab_tech_1"
    }
    """
    try:
        if not predictor:
            return jsonify({'error': 'Prediction service not available'}), 503
        
        data = request.get_json()
        
        # Validate required fields
        required = ['assembly_id', 'wick_tested', 'pass']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get wick ID from name
        wick_result = supabase.table('wicks') \
            .select('id') \
            .eq('name', data['wick_tested']) \
            .single() \
            .execute()
        
        if not wick_result.data:
            return jsonify({'error': f'Unknown wick: {data["wick_tested"]}'}), 400
        
        wick_id = wick_result.data['id']
        
        # Record test result
        test_data = {
            'flame_height_mm': data.get('flame_height_mm'),
            'melt_pool_mm_at_2h': data.get('melt_pool_mm_2h'),
            'notes': data.get('notes'),
            'tested_by': data.get('tested_by'),
            'test_type': data.get('test_type', 'quality_check')
        }
        
        predictor.record_test_result(
            assembly_id=data['assembly_id'],
            wick_id_tested=wick_id,
            test_data=test_data,
            passed=data['pass']
        )
        
        return jsonify({
            'success': True,
            'message': 'Test result recorded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/analytics/heat-index/<fragrance_id>', methods=['GET'])
def get_fragrance_heat_index(fragrance_id):
    """Get heat index analytics for a fragrance"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not available'}), 503
        
        # Get fragrance details with heat index
        fragrance = supabase.table('fragrance_oils') \
            .select('*, fragrance_heat_index_history(*)') \
            .eq('id', fragrance_id) \
            .single() \
            .execute()
        
        if not fragrance.data:
            return jsonify({'error': 'Fragrance not found'}), 404
        
        return jsonify({
            'success': True,
            'fragrance': {
                'id': fragrance.data['id'],
                'name': fragrance.data['name'],
                'heat_index': fragrance.data.get('heat_index', 0),
                'density_rating': fragrance.data.get('density_rating'),
                'category': fragrance.data.get('fragrance_category')
            },
            'history': [
                {
                    'date': h['calculation_date'],
                    'value': h['heat_index_value'],
                    'sample_size': h['sample_size']
                }
                for h in fragrance.data.get('fragrance_heat_index_history', [])
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/analytics/wax-conversion', methods=['GET'])
def get_wax_conversion_analytics():
    """Get analytics on wax conversion deltas"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not available'}), 503
        
        vessel_id = request.args.get('vessel_id')
        
        query = supabase.table('wax_conversion_deltas') \
            .select('*, vessels(*), old_wax:wax_types!old_wax_type_id(*), new_wax:wax_types!new_wax_type_id(*)')
        
        if vessel_id:
            query = query.eq('vessel_id', vessel_id)
        
        deltas = query.execute()
        
        return jsonify({
            'success': True,
            'count': len(deltas.data),
            'conversions': [
                {
                    'vessel': d['vessels']['name'],
                    'old_wax': d['old_wax']['name'],
                    'new_wax': d['new_wax']['name'],
                    'wick_size_delta': d['wick_size_delta'],
                    'confidence': d['confidence_score'],
                    'sample_count': d['sample_count']
                }
                for d in deltas.data
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/retrain', methods=['POST'])
def trigger_retrain():
    """Trigger ML model retraining"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not available'}), 503
        
        # Check if user has permission (implement your auth check here)
        # For now, we'll just proceed
        
        trainer = WickMLTrainer(supabase)
        metrics = trainer.train_and_save_model()
        
        # Reload model in predictor
        if predictor:
            predictor._load_latest_model()
        
        return jsonify({
            'success': True,
            'model_version': metrics.get('version'),
            'accuracy': metrics.get('accuracy'),
            'sample_size': metrics.get('sample_size'),
            'feature_importance': metrics.get('feature_importance', {})
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/majority-baseline', methods=['GET'])
def get_majority_baseline():
    """Get majority vote baseline for all vessel/wax combinations"""
    try:
        if not supabase:
            return jsonify({'error': 'Database not available'}), 503
        
        # Refresh materialized view
        supabase.rpc('refresh_materialized_view', {
            'view_name': 'wick_majority_baseline'
        }).execute()
        
        # Get baseline data
        baseline = supabase.table('wick_majority_baseline') \
            .select('*, vessels(*), wax_types(*), wicks:recommended_wick(*)') \
            .execute()
        
        return jsonify({
            'success': True,
            'count': len(baseline.data),
            'baseline': [
                {
                    'vessel': b['vessels']['name'],
                    'wax': b['wax_types']['name'],
                    'recommended_wick': b['wicks']['name'],
                    'sample_size': b['sample_size'],
                    'wick_variety': b['wick_variety']
                }
                for b in baseline.data
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wick_api.route('/quick-check', methods=['POST'])
def quick_wick_check():
    """
    Quick wick validation check for lab use
    
    Request body:
    {
        "vessel": "8oz Tumbler",
        "wax": "Soy C3",
        "fragrance": "Vanilla Bean",
        "wick": "ECO-10"
    }
    """
    try:
        if not supabase:
            return jsonify({'error': 'Database not available'}), 503
        
        data = request.get_json()
        
        # Look up components by name
        vessel = supabase.table('vessels').select('id').eq('name', data['vessel']).single().execute()
        wax = supabase.table('wax_types').select('id').eq('name', data['wax']).single().execute()
        fragrance = supabase.table('fragrance_oils').select('id').eq('name', data['fragrance']).single().execute()
        wick = supabase.table('wicks').select('id').eq('name', data['wick']).single().execute()
        
        if not all([vessel.data, wax.data, fragrance.data, wick.data]):
            return jsonify({'error': 'One or more components not found'}), 404
        
        # Get recommendations
        recommendations = predictor.get_comprehensive_recommendations(
            vessel_id=vessel.data['id'],
            wax_type_id=wax.data['id'],
            fragrance_id=fragrance.data['id'],
            fragrance_load=8.5  # Default assumption
        )
        
        # Check if proposed wick is in recommendations
        proposed_wick_id = wick.data['id']
        match = next((r for r in recommendations if r.wick_id == proposed_wick_id), None)
        
        if match and match.rank <= 3:
            status = 'recommended'
            message = f"Good choice! {match.reasoning}"
        elif match:
            status = 'possible'
            message = f"Possible but not optimal (rank {match.rank}). {match.reasoning}"
        else:
            status = 'not_recommended'
            top_rec = recommendations[0] if recommendations else None
            message = f"Not recommended. Try {top_rec.wick_name} instead." if top_rec else "No recommendations available"
        
        return jsonify({
            'success': True,
            'status': status,
            'message': message,
            'top_recommendations': [
                {'wick': r.wick_name, 'confidence': round(r.confidence, 2)}
                for r in recommendations[:3]
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500