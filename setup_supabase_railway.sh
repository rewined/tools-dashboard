#!/bin/bash

# Setup script to connect Supabase to Railway

echo "🔗 Connecting Candle Testing to Supabase Database"
echo "================================================"
echo ""
echo "Your Supabase project: ounsopanyjrjqmhbmxej"
echo ""
echo "To complete setup, you need your Supabase database password."
echo "Find it in Supabase: Settings → Database → Database Password"
echo ""
read -p "Enter your Supabase database password: " SUPABASE_PASSWORD
echo ""

# Construct the database URL
DATABASE_URL="postgresql://postgres:${SUPABASE_PASSWORD}@db.ounsopanyjrjqmhbmxej.supabase.co:5432/postgres"

echo "Setting DATABASE_URL in Railway..."

# Set the environment variable using Railway CLI
export RAILWAY_TOKEN="b36a5011-b1d9-49a5-87db-c8a2a27b62f4"
railway variables --set "DATABASE_URL=${DATABASE_URL}" --service fda9fdad-3f6b-484b-8163-00e3ed4c70d8 --environment production

if [ $? -eq 0 ]; then
    echo "✅ Database URL set successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run the SQL schema in Supabase SQL editor"
    echo "2. Railway will automatically redeploy with the new database"
    echo ""
    echo "Your candle test data will now be stored permanently in Supabase!"
else
    echo "❌ Failed to set environment variable"
    echo "You can set it manually in Railway dashboard:"
    echo "DATABASE_URL=${DATABASE_URL}"
fi