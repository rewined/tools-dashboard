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
- **Latest Commit**: Auto-updates with GitHub MCP changes
- **Deployment Method**: Railway connected to GitHub for auto-deployment
- **Local Repository**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/` (CORRECT - Original project directory)

## IMPORTANT REMINDERS FOR FUTURE CLAUDE SESSIONS

### 🚨 CRITICAL WORKFLOW RULES 🚨

#### GitHub File Management Protocol
**ALWAYS USE GITHUB MCP TOOLS** - Never ask user to run git commands manually
- Use `mcp__github__create_or_update_file` to update files in GitHub
- Use `mcp__github__get_file_contents` to read GitHub files  
- Use `mcp__github__push_files` for multiple file updates
- GitHub auto-syncs with Railway for deployment

#### Working Directory Protocol
**ORIGINAL PROJECT DIRECTORY** = `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/`
- This is the user's actual project with all source files
- Do NOT create copies in `/home/adamfetsch/` directories
- All file operations should reference the original directory
- Use GitHub MCP to sync changes between local and GitHub

#### Repository Synchronization Status
- **GitHub repo**: Contains working deployment files
- **Local directory**: Contains user's original source files
- **Workflow**: Read local files → Update GitHub via MCP → Railway auto-deploys
- **Method**: Use GitHub MCP tools exclusively for GitHub updates

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

### File Update Process
1. **Read Local File**: Use `Read` tool to get local file content
2. **Update GitHub**: Use `mcp__github__create_or_update_file` to push changes
3. **Auto-Deploy**: Railway automatically deploys from GitHub
4. **Verify**: Check deployed application

### Testing Workflow
1. **Local Testing**: User tests changes locally if desired
2. **GitHub MCP Update**: Claude updates GitHub with verified changes
3. **Live Deployment**: Railway auto-deploys updated files
4. **Verification**: Check live application matches expectations

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

### Styling Discrepancies
- **Issue**: Deployed version doesn't exactly match local screenshot
- **Root Cause**: Minor differences in CSS interpretation or missing styles
- **Solution**: Use GitHub MCP to update GitHub with exact local files
- **Status**: 🔄 Ready for further refinement using GitHub MCP workflow

### Repository Synchronization
- **Issue**: GitHub repository created separately from original project
- **Solution**: Use GitHub MCP tools to sync files (never manual git commands)
- **Status**: ✅ Workflow established using GitHub MCP tools

## Troubleshooting Guide

### Common Issues
1. **Local server won't start**: Help user with virtual environment in original directory
2. **Styling issues**: Read local CSS → Update GitHub via MCP → Verify deployment
3. **Railway deployment fails**: Check GitHub repo connection in Railway dashboard
4. **File sync issues**: Use GitHub MCP tools to update repository

### Emergency Procedures
1. **Rollback Deployment**: Use GitHub MCP to revert files to previous versions
2. **Railway Issues**: Use Railway dashboard manual deployment
3. **GitHub Access**: Verify GitHub MCP token is still valid

## Key File Locations
- **Project Root**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/`
- **Documentation**: `/mnt/c/Users/adamf/OneDrive/Desktop/Documents/ClaudeCode/price-sticker-printer/CLAUDE.md`
- **Live Application**: Railway-generated domain
- **Repository**: https://github.com/rewined/tools-dashboard

---

*Last Updated: 2025-07-05 - Added critical workflow reminders and GitHub MCP protocol*
*Next Update: After implementing GitHub MCP-based file synchronization*