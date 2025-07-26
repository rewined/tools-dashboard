#!/usr/bin/env python3
"""
Set DATABASE_URL in Railway via API
"""

import requests
import json
import getpass

# Configuration
API_TOKEN = "b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
SERVICE_ID = "fda9fdad-3f6b-484b-8163-00e3ed4c70d8"
ENVIRONMENT_ID = "95702724-51d3-4bde-b23e-cf27c0ebd13d"
GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

# Supabase info
SUPABASE_PROJECT = "ounsopanyjrjqmhbmxej"

print("🔗 Connect Candle Testing to Supabase Database")
print("=" * 50)
print(f"Supabase Project: {SUPABASE_PROJECT}")
print("\nTo find your database password:")
print("1. Go to Supabase Dashboard")
print("2. Navigate to: Settings → Database")
print("3. Look for 'Database Password' section")
print()

# Get password securely
password = getpass.getpass("Enter your Supabase database password: ")

# Construct database URL
database_url = f"postgresql://postgres:{password}@db.{SUPABASE_PROJECT}.supabase.co:5432/postgres"

print("\n📡 Setting DATABASE_URL in Railway...")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# GraphQL mutation to set variable
mutation = """
mutation SetVariable($input: VariableUpsertInput!) {
  variableUpsert(input: $input)
}
"""

variables = {
    "input": {
        "projectId": "0c0d7d31-f7d5-4466-9317-b85c480a0d1b",
        "environmentId": ENVIRONMENT_ID,
        "serviceId": SERVICE_ID,
        "name": "DATABASE_URL",
        "value": database_url
    }
}

response = requests.post(
    GRAPHQL_URL,
    json={"query": mutation, "variables": variables},
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    if 'data' in result:
        print("✅ DATABASE_URL set successfully!")
        print("\n🚀 Railway will automatically redeploy with Supabase database")
        print("\n📝 Next step: Run the SQL schema in Supabase SQL editor")
        print("   File: supabase_schema.sql")
    else:
        print("❌ Failed to set variable:")
        print(json.dumps(result, indent=2))
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)
    print("\nYou can set it manually in Railway dashboard:")
    print(f"DATABASE_URL={database_url}")