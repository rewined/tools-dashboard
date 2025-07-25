#!/usr/bin/env python3
"""
Deploy specific commit to Railway
"""

import requests
import json

# Configuration
API_TOKEN = "b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
ENVIRONMENT_ID = "95702724-51d3-4bde-b23e-cf27c0ebd13d"  # production
SERVICE_ID = "fda9fdad-3f6b-484b-8163-00e3ed4c70d8"
PROJECT_ID = "0c0d7d31-f7d5-4466-9317-b85c480a0d1b"
GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

# Latest commit info
COMMIT_SHA = "54ed643"
COMMIT_MESSAGE = "Add version endpoint to verify deployment"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Try to create a deployment with specific commit
deployment_mutation = """
mutation CreateDeployment {
  deploymentCreate(
    input: {
      environmentId: "%s"
      serviceId: "%s"
      meta: {
        commitHash: "%s"
        commitMessage: "%s"
      }
    }
  ) {
    id
    status
  }
}
""" % (ENVIRONMENT_ID, SERVICE_ID, COMMIT_SHA, COMMIT_MESSAGE)

print("🚀 Creating deployment for specific commit...")
print(f"Commit: {COMMIT_SHA}")
print(f"Message: {COMMIT_MESSAGE}")

response = requests.post(
    GRAPHQL_URL,
    json={"query": deployment_mutation},
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    if 'data' in data:
        print("✅ Deployment created successfully!")
        print(json.dumps(data, indent=2))
    else:
        print("❌ Deployment failed:")
        print(json.dumps(data, indent=2))
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)

# Alternative: Try deployment trigger mutation
trigger_mutation = """
mutation TriggerDeployment {
  deploymentTrigger(
    input: {
      environmentId: "%s"
      serviceId: "%s"
      commitHash: "%s"
    }
  )
}
""" % (ENVIRONMENT_ID, SERVICE_ID, COMMIT_SHA)

print("\n🔄 Trying alternative deployment trigger...")
response2 = requests.post(
    GRAPHQL_URL,
    json={"query": trigger_mutation},
    headers=headers
)

if response2.status_code == 200:
    data2 = response2.json()
    print(json.dumps(data2, indent=2))