#!/usr/bin/env python3
"""
Add version endpoint to check deployment
"""

# Add this to app_toolkit.py to verify deployment version

@app.route('/version')
def version():
    """Check deployment version"""
    return jsonify({
        'version': '1.1.0',
        'features': {
            'candle_testing': True,
            'thermal_printer_labels': True,
            'one_label_per_page': True,
            'netsuite_integration': True
        },
        'label_format': 'Each label on separate 1x4 inch page',
        'last_update': '2025-07-25 - Thermal printer support'
    })

# Also add this debug info to the label generation
@app.route('/candle-testing/label-info/<test_id>')
def candle_label_info(test_id):
    """Debug endpoint to check label generation"""
    test = db.session.get(CandleTest, test_id)
    if not test:
        return jsonify({'error': 'Test not found'}), 404
    
    return jsonify({
        'test_id': test_id,
        'trial_count': len(test.trials),
        'expected_pages': len(test.trials),
        'page_size': '1x4 inches',
        'format': 'One label per page for thermal printer'
    })