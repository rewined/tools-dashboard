#!/usr/bin/env python3
"""
Start the Flask application with environment variables loaded
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and run the app
from app_toolkit import app

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Candle Testing Dashboard")
    print("=" * 60)
    print(f"NetSuite Account: {os.environ.get('NETSUITE_ACCOUNT_ID', 'Not configured')}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print()
    print("Access the application at: http://127.0.0.1:5000")
    print("Candle Testing Tool: http://127.0.0.1:5000/candle-testing")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)