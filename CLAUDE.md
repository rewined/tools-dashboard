# Claude Code Configuration & Tools Dashboard Project

## Project Overview
This document tracks the Tools Dashboard project - a Flask-based web application with multiple business tools, currently featuring a Label Printer tool for generating barcode price stickers.

**Current Status**: ✅ Successfully deployed to Railway with ongoing styling refinements

## MCP Servers Configuration

### Railway MCP
- **Status**: ✅ Configured and operational
- **Command**: `railway-mcp`
- **Tools Available**: 112 Railway infrastructure management tools
- **Configuration**: Added via `claude mcp add railway railway-mcp`
- **Location**: Local config in `.claude.json`
- **API Token**: `b36a5011-b1d9-49a5-87db-c8a2a27b62f4`

### GitHub MCP  
- **Status**: ✅ Configured and operational
- **Configuration**: GitHub Personal Access Token configured
- **Repository**: `rewined/tools-dashboard`
- **Access**: Full read/write access for repository management

## Current Deployment Configuration

### Railway Project Details
- **Project Name**: `tools-project-fresh`
- **Project ID**: `0c0d7d31-f7d5-4466-9317-b85c480a0d1b`
- **Service Name**: `service-1751757808943`
- **Service ID**: `fda9fdad-3f6b-484b-8163-00e3ed4c70d8`
- **Status**: ✅ Active deployment
- **Connected Repository**: `rewined/tools-dashboard`
- **Branch**: `main`
- **Auto-Deploy**: ✅ Enabled from GitHub pushes

### GitHub Repository Details
- **Repository**: `rewined/tools-dashboard`
- **Primary Branch**: `main`
- **Latest Commit**: `dfe02952` (Updated style.css with correct button styling)
- **Deployment Method**: Railway connected to GitHub for auto-deployment
- **Local Repository**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/` (CORRECT - Original project directory)

## Project Structure and Key Files

### Application Files
- **Main Application**: `app_toolkit.py` - Flask application with dashboard and label printer
- **Entry Point**: Procfile specifies `web: gunicorn app_toolkit:app`
- **Dependencies**: `requirements.txt` with Flask, ReportLab, pandas, etc.

### Templates Structure
```
templates/
├── dashboard.html              # Main dashboard page
├── toolkit_base.html          # Base template with navigation
└── tools/
    ├── labels.html            # Label printer interface
    └── coming_soon.html       # Placeholder for future tools
```

### Static Assets
```
static/
├── css/
│   ├── style.css             # Main stylesheet (11,951 bytes)
│   └── toolkit.css           # Imports style.css + toolkit-specific styles
├── js/
│   └── labels.js             # Label printer functionality (325 lines)
└── uploads/                  # File upload directory
└── output/                   # Generated PDF output directory
```

### Source Code Structure
```
src/
├── csv_parser.py             # CSV file parsing functionality
├── pdf_generator_barcode.py  # Barcode PDF generation
└── label_formats.py          # Label format definitions (Avery templates)
```

## Development Workflow

### Local Development Setup
1. **Navigate to Project**: `cd "/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/"`
2. **Virtual Environment**: `python3 -m venv venv`
3. **Activation**: `source venv/bin/activate` 
4. **Dependencies**: `pip install -r requirements.txt`
5. **Local Server**: `python app_toolkit.py` (runs on http://localhost:5000)

### Version Control Workflow
1. **Local Testing**: Test changes on localhost:5000
2. **Git Commands**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. **Auto-Deployment**: Railway automatically deploys from GitHub pushes
4. **Live URL**: Generated Railway domain serves the application

### Key Git Commits History
- `ee1cc1b`: Added exact local template and CSS files
- `dfe02952`: Updated style.css with correct button styling

## Application Features

### Label Printer Tool (/labels)
- **Manual Entry**: Add individual items with SKU, Price, Quantity
- **CSV Upload**: Bulk import from CSV files with smart column mapping
- **Barcode Generation**: Uses PDFGeneratorBarcode class
- **Label Formats**: Multiple Avery label templates supported
- **Autocomplete**: SKU suggestions from products.csv (if available)
- **Dynamic Interface**: Add/remove items, real-time validation

### Dashboard (/)
- **Tool Grid**: Visual cards for each available tool
- **Status Indicators**: Active vs Coming Soon tools
- **Navigation**: Clean interface with toolkit branding

## Technical Implementation

### Flask Application Structure
- **Routes**: Organized by feature (dashboard, labels, future tools)
- **Error Handling**: Try/catch blocks with JSON error responses
- **File Management**: Secure file uploads with timestamp naming
- **PDF Generation**: Custom barcode generator with multiple format support

### Frontend Technologies
- **HTML Templates**: Jinja2 templating with inheritance
- **CSS Framework**: Custom gradient-based design system
- **JavaScript**: Vanilla JS for dynamic interactions
- **Responsive Design**: Mobile-friendly grid layouts

### Backend Dependencies
- **Flask 3.0.0**: Web framework
- **ReportLab 4.0.7**: PDF generation
- **Pandas 2.1.4**: CSV processing
- **Gunicorn 21.2.0**: Production WSGI server
- **python-barcode 0.15.1**: Barcode generation

## Current Issues and Solutions

### Repository Synchronization
- **Issue**: GitHub repository was created from copied files instead of original project
- **Root Cause**: Development started in wrong directory (/home/adamfetsch/tools-project/)
- **Solution**: Reconnecting GitHub to original project directory
- **Status**: 🔄 In progress - updating GitHub with original files

### Styling Discrepancies
- **Issue**: Deployed version doesn't exactly match local screenshot
- **Root Cause**: CSS differences between local and GitHub versions
- **Solution**: Updated GitHub with exact local style.css file
- **Status**: 🔄 Partially resolved, minor differences remain

### Railway API Connectivity
- **Issue**: Intermittent Railway MCP API responses
- **Workaround**: Manual deployment via Railway dashboard when MCP fails
- **Monitoring**: Check Railway API status when automation fails

## Troubleshooting Guide

### Common Issues
1. **Local server won't start**: Ensure virtual environment is activated in correct directory
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Railway deployment fails**: Check GitHub repo connection in Railway dashboard
4. **Styling issues**: Verify style.css is properly imported by toolkit.css

### Emergency Procedures
1. **Rollback Deployment**: Revert to previous commit via git reset
2. **Railway Issues**: Use Railway dashboard manual deployment
3. **GitHub Access**: Verify GitHub MCP token is still valid
4. **Local Development**: Always test locally before pushing to GitHub

## Key File Locations
- **Project Root**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/`
- **Documentation**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/CLAUDE.md`
- **Live Application**: Railway-generated domain
- **Repository**: https://github.com/rewined/tools-dashboard

---

*Last Updated: 2025-07-05 - Corrected repository synchronization*
*Next Update: After completing GitHub reconnection*