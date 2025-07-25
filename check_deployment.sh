#!/bin/bash

echo "Railway Deployment Check"
echo "======================="
echo ""

# Check if we can find the deployment URL
if [ -z "$1" ]; then
    echo "Please provide your Railway deployment URL as an argument"
    echo "Usage: ./check_deployment.sh https://your-app.railway.app"
    exit 1
fi

URL=$1

echo "Testing deployment at: $URL"
echo ""

# Test main page
echo "1. Testing main dashboard..."
curl -s -o /dev/null -w "   Status: %{http_code}\n" $URL/

# Test candle testing
echo ""
echo "2. Testing candle testing dashboard..."
curl -s -o /dev/null -w "   Status: %{http_code}\n" $URL/candle-testing

# Test create page
echo ""
echo "3. Testing create page..."
curl -s -o /dev/null -w "   Status: %{http_code}\n" $URL/candle-testing/create

# Test products API
echo ""
echo "4. Testing products API..."
response=$(curl -s -w "\n   Status: %{http_code}" $URL/candle-testing/products)
echo "$response" | tail -1

# Parse JSON response
json=$(echo "$response" | head -n -1)
if [ ! -z "$json" ]; then
    echo "   Products found:"
    echo "$json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'   - Vessels: {len(data.get(\"vessels\", []))}')
print(f'   - Waxes: {len(data.get(\"waxes\", []))}')
print(f'   - Fragrances: {len(data.get(\"fragrances\", []))}')
print(f'   - Wicks: {len(data.get(\"wicks\", []))}')
"
fi

echo ""
echo "Deployment check complete!"