# Deploy Team Toolkit to Railway

## Quick Deploy Steps

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and Deploy**
   ```bash
   railway up
   ```

4. **Get your URL**
   Railway will give you a URL like: `https://your-app.railway.app`

## What's Deployed

✅ **Main Dashboard** (`/`) - Shows all available tools
✅ **Label Printer** (`/labels`) - Your current tool with autocomplete
✅ **Coming Soon Tools** - Placeholders for future tools
✅ **API Endpoints** - All routes properly configured

## Team Access

- Share the Railway URL with your team
- No login required - direct access
- Mobile-friendly interface
- Works on all devices

## Future Tools

Ready to add:
- **Inventory Scanner** (`/inventory`)
- **Report Generator** (`/reports`)  
- **Price Updater** (`/pricing`)

## Adding New Tools

1. Add route in `app_toolkit.py`
2. Create template in `templates/tools/`
3. Add to dashboard tools list
4. Deploy with `railway up`

## Local Development

```bash
python app_toolkit.py
# Access at http://localhost:5000
```

## Environment

- Python 3.12+
- Flask web framework
- No database needed (CSV files)
- Serverless deployment