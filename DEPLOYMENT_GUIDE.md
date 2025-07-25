# Candle Testing System Deployment Guide

## Railway Deployment Steps

### 1. Environment Variables
Add these to your Railway project environment variables:

```
NETSUITE_ACCOUNT_ID=3646798
NETSUITE_CONSUMER_KEY=a55f53fd661e09c5f3b0c2e64def2a533f69b04b36801ead8005fa9464aff99e
NETSUITE_CONSUMER_SECRET=ea7f3991084e79ff4b858a3be389c3abbc962eeb5d0b28b20c00e341d14d4b9a
NETSUITE_TOKEN_ID=1e444d7e6a8ac2ad94e526ef0b489cc2a76bc4b465cd07556794fc2922aaa131
NETSUITE_TOKEN_SECRET=d37ec468a32734541d4289a167c64d17ff3dc4cefbf98c3f02bf8fd408213877
```

### 2. Database Configuration
By default, the app uses SQLite. For production, consider using PostgreSQL:
- Railway provides PostgreSQL databases
- Add the `DATABASE_URL` environment variable that Railway provides

### 3. Deploy via GitHub
1. Push changes to your GitHub repository
2. Railway will auto-deploy from the main branch

### 4. Deploy via Railway CLI
```bash
# If not already linked
railway link

# Deploy
railway up
```

## Features Included

### Candle Testing Tool
- **URL**: `/candle-testing`
- **Features**:
  - Create tests with NetSuite inventory items
  - Generate QR code labels (1x4" format)
  - Mobile-friendly evaluation forms
  - Track burn test progress

### Label Printer Tool
- **URL**: `/labels`
- **Features**:
  - Generate barcode labels
  - CSV upload support
  - Multiple label formats

## Post-Deployment

### Verify NetSuite Integration
1. Visit `/candle-testing/create`
2. Check that dropdowns populate with NetSuite items
3. If not, check Railway logs for authentication errors

### Database Migration
The app automatically creates tables on first run. For existing deployments:
```python
from app_toolkit import app, db
with app.app_context():
    db.create_all()
```

## Troubleshooting

### NetSuite 401 Errors
- Verify all 5 environment variables are set correctly
- Check that REST Web Services are enabled in NetSuite
- Ensure token has proper permissions

### Database Issues
- SQLite file permissions
- Consider switching to PostgreSQL for production

### Missing Dependencies
- Check requirements.txt includes all packages
- Railway uses nixpacks which should handle dependencies

## URLs After Deployment
- Main Dashboard: `https://your-app.railway.app/`
- Candle Testing: `https://your-app.railway.app/candle-testing`
- Label Printer: `https://your-app.railway.app/labels`