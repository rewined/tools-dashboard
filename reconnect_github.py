#!/usr/bin/env python3
"""
Reconnect GitHub repository to Railway service
"""

import requests
import json

# Configuration
API_TOKEN = "b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
SERVICE_ID = "fda9fdad-3f6b-484b-8163-00e3ed4c70d8"
PROJECT_ID = "0c0d7d31-f7d5-4466-9317-b85c480a0d1b"
GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Update service source to force reconnection
update_source_mutation = """
mutation UpdateServiceSource {
  serviceUpdate(
    id: "%s"
    input: {
      source: {
        repo: "rewined/tools-dashboard"
        branch: "main"
      }
    }
  ) {
    id
    name
    source
  }
}
""" % SERVICE_ID

print("🔄 Updating service source configuration...")
response = requests.post(
    GRAPHQL_URL,
    json={"query": update_source_mutation},
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    if 'data' in data:
        print("✅ Service source updated!")
        print(json.dumps(data, indent=2))
    else:
        print("❌ Update failed:")
        print(json.dumps(data, indent=2))
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)

# Force a new deployment after reconnection
print("\n🚀 Triggering new deployment...")
redeploy_mutation = """
mutation ServiceInstanceRedeploy {
  serviceInstanceRedeploy(
    environmentId: "95702724-51d3-4bde-b23e-cf27c0ebd13d"
    serviceId: "%s"
  )
}
""" % SERVICE_ID

response2 = requests.post(
    GRAPHQL_URL,
    json={"query": redeploy_mutation},
    headers=headers
)

if response2.status_code == 200:
    data2 = response2.json()
    if 'data' in data2:
        print("✅ Redeploy triggered!")
        print("Check Railway dashboard for deployment progress")
    else:
        print("❌ Redeploy failed:")
        print(json.dumps(data2, indent=2))