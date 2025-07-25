#!/usr/bin/env python3
"""
Manually trigger a Railway redeploy
"""

import requests
import json

# Configuration
API_TOKEN = "b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
ENVIRONMENT_ID = "95702724-51d3-4bde-b23e-cf27c0ebd13d"  # production
SERVICE_ID = "fda9fdad-3f6b-484b-8163-00e3ed4c70d8"
GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

redeploy_mutation = """
mutation ServiceInstanceRedeploy {
  serviceInstanceRedeploy(
    environmentId: "%s"
    serviceId: "%s"
  )
}
""" % (ENVIRONMENT_ID, SERVICE_ID)

print("🚀 Triggering Railway Redeploy...")
print(f"Service ID: {SERVICE_ID}")
print(f"Environment: production")

response = requests.post(
    GRAPHQL_URL,
    json={"query": redeploy_mutation},
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    if 'data' in data:
        print("✅ Redeploy triggered successfully!")
        print("Check Railway dashboard for deployment progress")
    else:
        print("❌ Redeploy failed:")
        print(json.dumps(data, indent=2))
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)