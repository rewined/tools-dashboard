# Wick-onomics System Documentation

## Overview
The Wick-onomics system is an AI-powered wick prediction and recommendation engine designed to streamline the candle testing process during wax changeovers. It combines historical data analysis, machine learning, and domain-specific heuristics to predict optimal wick sizes for candle assemblies.

## Key Features

### 1. **Intelligent Wick Prediction**
- **Majority Vote Baseline**: Leverages historical data to find the most commonly successful wick for vessel/wax combinations
- **Wax Conversion Heuristics**: Learns wick size deltas when converting between wax types
- **Fragrance Heat Index**: Calculates and applies fragrance-specific burn characteristics
- **ML-Powered Predictions**: XGBoost model trained on successful candle assemblies

### 2. **Active Learning & Test Prioritization**
- Identifies assemblies with the highest uncertainty
- Calculates information gain to minimize total tests needed
- Priority queue system for efficient lab testing

### 3. **Analytics Dashboard**
- Real-time model performance metrics
- Wax conversion progress tracking
- Heat index visualization
- Test priority management

### 4. **API Endpoints**
- `/api/wick/predict` - Get wick recommendations
- `/api/wick/test-priorities` - Get prioritized test queue
- `/api/wick/log-test` - Record test results
- `/api/wick/analytics/*` - Various analytics endpoints
- `/api/wick/retrain` - Trigger model retraining

## System Architecture

### Data Model
```
vessels -> assemblies <- wax_types
              |
         fragrances <- heat_index
              |
           wicks <- predictions
              |
        test_results
```

### Prediction Flow
1. Check majority vote baseline
2. Apply wax conversion delta (if applicable)
3. Get ML predictions
4. Adjust for fragrance heat index
5. Return ranked recommendations with confidence scores

## Implementation Details

### Database Schema
- **Enhanced tables**: vessels, wax_types, fragrance_oils, wicks, assemblies
- **New tables**: test_results, wax_conversion_deltas, wick_predictions, test_priority_queue
- **Materialized views**: wick_majority_baseline
- **Functions**: calculate_fragrance_heat_index(), get_wax_conversion_delta()

### Machine Learning
- **Algorithm**: XGBoost (gradient boosted trees)
- **Features**: 14 engineered features including vessel dimensions, wax properties, fragrance characteristics
- **Training**: Automated retraining with version control
- **Evaluation**: Cross-validation with accuracy tracking

### Heat Index Calculation
```
heat_index = zscore(flame_height_mm - melt_pool_mm_at_2h)
```
Categories:
- **Cool** (< -0.5σ): Needs larger wick
- **Neutral** (-0.5σ to +0.5σ): Use baseline
- **Hot** (> +0.5σ): Consider smaller wick

## Usage Guide

### For Lab Technicians

#### Quick Wick Check
1. Navigate to Wick Analytics dashboard
2. Click "Quick Check"
3. Enter vessel, wax, fragrance, and proposed wick
4. Get instant validation with recommendations

#### Log Test Results
```python
POST /api/wick/log-test
{
    "assembly_id": "123",
    "wick_tested": "ECO-10",
    "flame_height_mm": 35,
    "melt_pool_mm_2h": 45,
    "pass": true,
    "notes": "Good burn, slight mushrooming"
}
```

### For Product Managers

#### View Test Priorities
1. Access dashboard at `/wick-analytics`
2. Review "Test Priority Queue"
3. Focus testing on high-information-gain assemblies

#### Track Conversion Progress
- Monitor real-time progress bar
- View wax conversion patterns
- Export analytics data

### For Developers

#### Get Predictions Programmatically
```python
from src.wick_predictor import WickPredictor

predictor = WickPredictor(supabase_client)
recommendations = predictor.get_comprehensive_recommendations(
    vessel_id="v123",
    wax_type_id="w456",
    fragrance_id="f789",
    fragrance_load=8.5
)
```

#### Integrate with Existing Systems
```javascript
// Frontend integration
fetch('/api/wick/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        vessel_id: vesselId,
        wax_type_id: waxId,
        fragrance_id: fragranceId,
        fragrance_load: 8.5
    })
})
.then(response => response.json())
.then(data => {
    // Display recommendations
    console.log(data.recommendations);
});
```

## Configuration

### Environment Variables
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
NETSUITE_ACCOUNT_ID=your_account_id
# ... other NetSuite credentials
```

### Database Setup
1. Run `wick_onomics_schema.sql` in Supabase
2. Configure NetSuite sync for product data
3. Initialize with historical test data

### Model Training
```bash
# Manual training trigger
curl -X POST http://localhost:5000/api/wick/retrain

# Scheduled training (add to cron)
0 2 * * * python -c "from src.wick_ml_trainer import WickMLTrainer; trainer = WickMLTrainer(supabase); trainer.train_and_save_model()"
```

## Performance Metrics

### Current System Performance
- **Prediction Accuracy**: Target >85% for high-confidence predictions
- **Test Reduction**: Expected 60-80% reduction in required burn tests
- **Response Time**: <200ms for predictions, <2s for analytics

### ROI Calculation
```
Cost per test: $X (labor + materials)
Tests without system: 250 SKUs × Y tests/SKU
Tests with system: 250 SKUs × (Y × 0.3) tests/SKU
Savings: 250 × Y × 0.7 × $X
```

## Troubleshooting

### Common Issues

1. **"No predictions available"**
   - Check Supabase connection
   - Verify product data is synced
   - Ensure model file exists in `/models`

2. **Low confidence predictions**
   - Review training data quality
   - Check for sufficient historical data
   - Consider manual test for edge cases

3. **Heat index not updating**
   - Verify test results are being logged
   - Check trigger functions in database
   - Manual recalculation: `SELECT calculate_fragrance_heat_index('fragrance_id')`

## Future Enhancements

1. **Multi-wick support**: Extend predictions for double-wick candles
2. **Seasonal adjustments**: Factor in ambient temperature variations
3. **Cost optimization**: Include wick pricing in recommendations
4. **Mobile app**: Native app for lab technicians
5. **Integration with production**: Auto-update BOMs after approval

## Support

For issues or questions:
1. Check error logs in Supabase
2. Review API response messages
3. Contact the development team

---

*Version 1.0 - Wax Changeover Edition*
*Last Updated: [Current Date]*