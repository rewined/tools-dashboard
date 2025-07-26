"""
Machine Learning trainer for wick prediction model
Uses XGBoost for gradient boosted trees with mixed categorical/numeric features
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
from collections import Counter

class WickMLTrainer:
    """Trains and maintains ML models for wick prediction"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.model = None
        self.feature_names = [
            'volume_ml', 'diameter_mm', 'height_mm', 'double_wick',
            'heat_dissipation_factor', 'melt_point_celsius', 'viscosity_index',
            'flash_point_celsius', 'heat_index', 'fragrance_load_percentage',
            'vessel_shape_encoded', 'vessel_material_encoded',
            'wax_base_type_encoded', 'fragrance_category_encoded'
        ]
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Fetch and prepare training data from database"""
        
        # Get successful assemblies with all their test results
        query = """
        SELECT 
            a.id as assembly_id,
            a.wick_id_1,
            a.fragrance_load_percentage,
            v.volume_ml,
            v.diameter_mm,
            v.height_mm,
            v.shape as vessel_shape,
            v.material as vessel_material,
            v.double_wick,
            v.heat_dissipation_factor,
            w.melt_point_celsius,
            w.viscosity_index,
            w.base_type as wax_base_type,
            f.flash_point_celsius,
            f.heat_index,
            f.fragrance_category,
            f.density_rating
        FROM assemblies a
        JOIN vessels v ON a.vessel_id = v.id
        JOIN wax_types w ON a.wax_type_id = w.id
        JOIN fragrance_oils f ON a.fragrance_oil_id = f.id
        WHERE a.approved_date IS NOT NULL
        AND a.wick_id_1 IS NOT NULL
        """
        
        # Execute query
        result = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if not result.data:
            raise ValueError("No training data available")
        
        # Convert to DataFrame
        df = pd.DataFrame(result.data)
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Encode categorical variables
        categorical_cols = ['vessel_shape', 'vessel_material', 'wax_base_type', 'fragrance_category']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].fillna('unknown'))
                self.label_encoders[col] = le
        
        # Convert boolean to numeric
        df['double_wick'] = df['double_wick'].astype(int)
        
        # Prepare features and target
        feature_cols = [
            'volume_ml', 'diameter_mm', 'height_mm', 'double_wick',
            'heat_dissipation_factor', 'melt_point_celsius', 'viscosity_index',
            'flash_point_celsius', 'heat_index', 'fragrance_load_percentage',
            'vessel_shape_encoded', 'vessel_material_encoded',
            'wax_base_type_encoded', 'fragrance_category_encoded'
        ]
        
        X = df[feature_cols]
        y = df['wick_id_1']
        
        return X, y
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with domain-specific logic"""
        
        # Numeric columns: fill with median
        numeric_cols = [
            'volume_ml', 'diameter_mm', 'height_mm', 'heat_dissipation_factor',
            'melt_point_celsius', 'viscosity_index', 'flash_point_celsius',
            'heat_index', 'fragrance_load_percentage'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Categorical columns: fill with mode or 'unknown'
        categorical_cols = ['vessel_shape', 'vessel_material', 'wax_base_type', 'fragrance_category']
        for col in categorical_cols:
            if col in df.columns:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
                df[col] = df[col].fillna(mode_val)
        
        # Boolean columns
        if 'double_wick' in df.columns:
            df['double_wick'] = df['double_wick'].fillna(False)
        
        return df
    
    def train_model(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Train XGBoost model with cross-validation"""
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Encode target labels
        le_target = LabelEncoder()
        y_encoded = le_target.fit_transform(y)
        self.label_encoders['target'] = le_target
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train XGBoost model
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective='multi:softprob',
            random_state=42,
            use_label_encoder=False
        )
        
        # Fit model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=10,
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_scaled, y_encoded, cv=5)
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Sort by importance
        feature_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        metrics = {
            'accuracy': float(accuracy),
            'cv_score_mean': float(cv_scores.mean()),
            'cv_score_std': float(cv_scores.std()),
            'sample_size': len(X),
            'n_classes': len(np.unique(y_encoded)),
            'feature_importance': feature_importance,
            'top_features': list(feature_importance.keys())[:5]
        }
        
        return metrics
    
    def save_model(self, metrics: Dict) -> str:
        """Save trained model and metadata"""
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Generate version string
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_path = os.path.join('models', f'wick_predictor_{version}.pkl')
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'metrics': metrics,
            'version': version
        }, model_path)
        
        # Also save as latest
        latest_path = os.path.join('models', 'wick_predictor_latest.pkl')
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'metrics': metrics,
            'version': version
        }, latest_path)
        
        return version
    
    def train_and_save_model(self) -> Dict:
        """Complete training pipeline"""
        
        try:
            # Prepare data
            X, y = self.prepare_training_data()
            
            # Train model
            metrics = self.train_model(X, y)
            
            # Save model
            version = self.save_model(metrics)
            metrics['version'] = version
            
            # Log training run
            self.supabase.table('ml_training_runs').insert({
                'model_type': 'wick_predictor',
                'version': version,
                'accuracy': metrics['accuracy'],
                'cv_score': metrics['cv_score_mean'],
                'sample_size': metrics['sample_size'],
                'metrics': metrics,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Training failed: {str(e)}")
    
    def analyze_prediction_errors(self) -> Dict:
        """Analyze where the model makes mistakes"""
        
        # Get predictions vs actual
        query = """
        SELECT 
            p.predicted_wick_id,
            p.actual_wick_id,
            p.confidence_score,
            a.vessel_id,
            a.wax_type_id,
            a.fragrance_oil_id,
            v.name as vessel_name,
            w.name as wax_name,
            f.name as fragrance_name
        FROM wick_predictions p
        JOIN assemblies a ON p.assembly_id = a.id
        JOIN vessels v ON a.vessel_id = v.id
        JOIN wax_types w ON a.wax_type_id = w.id
        JOIN fragrance_oils f ON a.fragrance_oil_id = f.id
        WHERE p.verified = true
        AND p.actual_wick_id IS NOT NULL
        AND p.predicted_wick_id != p.actual_wick_id
        """
        
        errors = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if not errors.data:
            return {'error_count': 0, 'patterns': []}
        
        # Analyze error patterns
        df = pd.DataFrame(errors.data)
        
        patterns = []
        
        # Most common vessel errors
        vessel_errors = df['vessel_name'].value_counts().head()
        patterns.append({
            'type': 'vessel',
            'description': 'Vessels with most prediction errors',
            'data': vessel_errors.to_dict()
        })
        
        # Most common wax errors
        wax_errors = df['wax_name'].value_counts().head()
        patterns.append({
            'type': 'wax',
            'description': 'Wax types with most prediction errors',
            'data': wax_errors.to_dict()
        })
        
        # Low confidence predictions that were wrong
        low_conf_errors = df[df['confidence_score'] < 0.5]
        patterns.append({
            'type': 'confidence',
            'description': 'Errors in low confidence predictions',
            'count': len(low_conf_errors),
            'percentage': len(low_conf_errors) / len(df) * 100
        })
        
        return {
            'error_count': len(df),
            'total_predictions': len(df),
            'patterns': patterns
        }
    
    def get_learning_curves(self) -> Dict:
        """Get model performance over time"""
        
        query = """
        SELECT 
            version,
            accuracy,
            cv_score,
            sample_size,
            created_at
        FROM ml_training_runs
        WHERE model_type = 'wick_predictor'
        ORDER BY created_at DESC
        LIMIT 20
        """
        
        runs = self.supabase.rpc('execute_sql', {'query': query}).execute()
        
        if not runs.data:
            return {'runs': []}
        
        return {
            'runs': runs.data,
            'current_accuracy': runs.data[0]['accuracy'] if runs.data else 0,
            'improvement': (runs.data[0]['accuracy'] - runs.data[-1]['accuracy']) if len(runs.data) > 1 else 0
        }