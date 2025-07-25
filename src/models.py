from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class CandleTest(db.Model):
    """Main candle test record"""
    __tablename__ = 'candle_tests'
    
    id = db.Column(db.String(50), primary_key=True)
    vessel = db.Column(db.String(200), nullable=False)
    wax = db.Column(db.String(200), nullable=False)
    fragrance = db.Column(db.String(200), nullable=False)
    blend_percentage = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    trials = db.relationship('CandleTrial', backref='test', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'vessel': self.vessel,
            'wax': self.wax,
            'fragrance': self.fragrance,
            'blend_percentage': self.blend_percentage,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'trials': [trial.to_dict() for trial in self.trials]
        }


class CandleTrial(db.Model):
    """Individual trial within a test (different wick)"""
    __tablename__ = 'candle_trials'
    
    id = db.Column(db.String(50), primary_key=True)
    test_id = db.Column(db.String(50), db.ForeignKey('candle_tests.id'), nullable=False)
    trial_number = db.Column(db.Integer, nullable=False)
    wick = db.Column(db.String(200), nullable=False)
    
    # Relationships
    evaluations = db.relationship('CandleEvaluation', backref='trial', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'trial_number': self.trial_number,
            'wick': self.wick
        }
    
    def get_evaluations_dict(self):
        """Get evaluations as a dictionary organized by hour"""
        eval_dict = {}
        for eval in self.evaluations:
            if eval.evaluation_type == 'post_extinguish':
                eval_dict['post_extinguish'] = {
                    'after_glow': eval.after_glow,
                    'after_smoke': eval.after_smoke,
                    'timestamp': eval.created_at.isoformat()
                }
            else:
                eval_dict[eval.evaluation_type] = {
                    'full_melt_pool': eval.full_melt_pool,
                    'melt_pool_depth': eval.melt_pool_depth,
                    'external_temp': eval.external_temp,
                    'flame_height': eval.flame_height,
                    'timestamp': eval.created_at.isoformat()
                }
        return eval_dict


class CandleEvaluation(db.Model):
    """Evaluation data for a trial at specific time intervals"""
    __tablename__ = 'candle_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    trial_id = db.Column(db.String(50), db.ForeignKey('candle_trials.id'), nullable=False)
    evaluation_type = db.Column(db.String(20), nullable=False)  # '1hr', '2hr', '4hr', 'post_extinguish'
    
    # Time-based measurements
    full_melt_pool = db.Column(db.Boolean, nullable=True)
    melt_pool_depth = db.Column(db.Float, nullable=True)  # in inches
    external_temp = db.Column(db.Float, nullable=True)  # in Fahrenheit
    flame_height = db.Column(db.Float, nullable=True)  # in inches
    
    # Post-extinguish measurements
    after_glow = db.Column(db.Integer, nullable=True)  # in seconds
    after_smoke = db.Column(db.Integer, nullable=True)  # in seconds
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate evaluations
    __table_args__ = (db.UniqueConstraint('trial_id', 'evaluation_type'),)


class Product(db.Model):
    """Cache for NetSuite product data"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False)
    product_type = db.Column(db.String(20), nullable=False)  # 'vessel', 'wax', 'fragrance', 'wick'
    name = db.Column(db.String(200), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.product_id,
            'name': self.name
        }