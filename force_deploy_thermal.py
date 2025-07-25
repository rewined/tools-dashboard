#!/usr/bin/env python3
"""
Force deploy with cache clearing
"""

import requests
import json
import time

# Configuration
API_TOKEN = "b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
ENVIRONMENT_ID = "95702724-51d3-4bde-b23e-cf27c0ebd13d"
SERVICE_ID = "fda9fdad-3f6b-484b-8163-00e3ed4c70d8"
GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# First, clear any cache
print("🧹 Clearing deployment cache...")
cache_clear_mutation = """
mutation ClearCache {
  deploymentCachePurge(
    environmentId: "%s"
    serviceId: "%s"
  )
}
""" % (ENVIRONMENT_ID, SERVICE_ID)

response = requests.post(
    GRAPHQL_URL,
    json={"query": cache_clear_mutation},
    headers=headers
)

if response.status_code == 200:
    print("✅ Cache cleared (or no cache to clear)")
else:
    print(f"⚠️  Cache clear attempt: {response.status_code}")

# Wait a moment
time.sleep(2)

# Force a fresh deployment
print("\n🚀 Triggering fresh deployment...")
redeploy_mutation = """
mutation ForceDeploy {
  serviceInstanceRedeploy(
    environmentId: "%s"
    serviceId: "%s"
  )
}
""" % (ENVIRONMENT_ID, SERVICE_ID)

response2 = requests.post(
    GRAPHQL_URL,
    json={"query": redeploy_mutation},
    headers=headers
)

if response2.status_code == 200:
    data = response2.json()
    if 'data' in data and data['data'].get('serviceInstanceRedeploy'):
        print("✅ Fresh deployment triggered!")
        print("   Check Railway dashboard for progress")
        print("   URL: https://railway.app/project/0c0d7d31-f7d5-4466-9317-b85c480a0d1b/service/fda9fdad-3f6b-484b-8163-00e3ed4c70d8/deployments")
    else:
        print("❌ Deployment trigger response:", json.dumps(data, indent=2))
else:
    print(f"❌ Request failed: {response2.status_code}")
    print(response2.text)

# Check deployment status after a moment
print("\n⏳ Waiting 5 seconds to check status...")
time.sleep(5)

# Get latest deployment
status_query = """
query GetLatestDeployment {
  deployments(
    first: 1
    input: {
      projectId: "0c0d7d31-f7d5-4466-9317-b85c480a0d1b"
      serviceId: "%s"
      environmentId: "%s"
    }
  ) {
    edges {
      node {
        id
        status
        createdAt
        meta
      }
    }
  }
}
""" % (SERVICE_ID, ENVIRONMENT_ID)

response3 = requests.post(
    GRAPHQL_URL,
    json={"query": status_query},
    headers=headers
)

if response3.status_code == 200:
    data = response3.json()
    if 'data' in data and data['data']['deployments']['edges']:
        deployment = data['data']['deployments']['edges'][0]['node']
        print(f"\n📊 Latest deployment:")
        print(f"   Status: {deployment['status']}")
        print(f"   Created: {deployment['createdAt']}")
        if deployment.get('meta'):
            meta = json.loads(deployment['meta']) if isinstance(deployment['meta'], str) else deployment['meta']
            print(f"   Commit: {meta.get('commitHash', 'unknown')}")
    else:
        print("\n⚠️  Could not fetch deployment status")
else:
    print(f"\n❌ Status check failed: {response3.status_code}")