#!/bin/bash

# Load environment variables
export NETSUITE_ACCOUNT_ID='3646798'
export NETSUITE_CONSUMER_KEY='a55f53fd661e09c5f3b0c2e64def2a533f69b04b36801ead8005fa9464aff99e'
export NETSUITE_CONSUMER_SECRET='ea7f3991084e79ff4b858a3be389c3abbc962eeb5d0b28b20c00e341d14d4b9a'
export NETSUITE_TOKEN_ID='1e444d7e6a8ac2ad94e526ef0b489cc2a76bc4b465cd07556794fc2922aaa131'
export NETSUITE_TOKEN_SECRET='d37ec468a32734541d4289a167c64d17ff3dc4cefbf98c3f02bf8fd408213877'

# Create database if needed
python3 -c "from app_toolkit import app, db; app.app_context().push(); db.create_all()"

# Start the application
python3 -m flask --app app_toolkit run --host 0.0.0.0 --port 5000