#!/usr/bin/env python3
"""
Simple demo server to show the web interface without external dependencies.
Note: This won't generate actual PDFs without the required libraries.
"""

import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

PORT = 8000

demo_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Price Sticker Printer - Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2563eb; }
        .info-box { background: #e0e7ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .step { margin: 15px 0; padding: 15px; background: #f9fafb; border-radius: 5px; }
        .step h3 { margin-top: 0; color: #374151; }
        code { background: #e5e7eb; padding: 2px 6px; border-radius: 3px; font-size: 14px; }
        .demo-note { color: #dc2626; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Sticker Printer Web App</h1>
        
        <div class="info-box">
            <p class="demo-note">⚠️ Demo Mode: This is showing what the interface looks like.</p>
            <p>To run the full application with PDF generation, you need to install the dependencies.</p>
        </div>
        
        <h2>Features:</h2>
        <ul>
            <li>📤 Drag-and-drop CSV file upload</li>
            <li>👀 Live preview of your data</li>
            <li>🏷️ Multiple label formats (Avery compatible)</li>
            <li>🎯 Auto-detection of CSV columns</li>
            <li>📄 Instant PDF generation and download</li>
            <li>📱 Responsive design for all devices</li>
        </ul>
        
        <h2>Setup Instructions:</h2>
        
        <div class="step">
            <h3>Step 1: Install Dependencies</h3>
            <p>First, install pip if you haven't already:</p>
            <code>sudo apt-get install python3-pip python3-venv</code>
        </div>
        
        <div class="step">
            <h3>Step 2: Create Virtual Environment</h3>
            <code>cd price-sticker-printer</code><br>
            <code>python3 -m venv venv</code><br>
            <code>source venv/bin/activate</code> (Linux/Mac)<br>
            <code>venv\\Scripts\\activate</code> (Windows)
        </div>
        
        <div class="step">
            <h3>Step 3: Install Requirements</h3>
            <code>pip install -r requirements.txt</code>
        </div>
        
        <div class="step">
            <h3>Step 4: Run the App</h3>
            <code>python app.py</code><br>
            <p>Then open: <strong>http://localhost:5000</strong></p>
        </div>
        
        <h2>Label Formats Available:</h2>
        <ul>
            <li><strong>Avery 5160</strong> - 1" x 2-5/8" (30 labels/page)</li>
            <li><strong>Avery 5163</strong> - 2" x 4" (10 labels/page)</li>
            <li><strong>Avery 5167</strong> - 1/2" x 1-3/4" (80 labels/page)</li>
            <li><strong>Avery 8163</strong> - 2" x 4" (10 labels/page)</li>
            <li><strong>Custom Square</strong> - 2" x 2" (20 labels/page)</li>
        </ul>
    </div>
</body>
</html>
"""

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(demo_html.encode())

print(f"Starting demo server on http://localhost:{PORT}")
print("This is a demo to show what the interface looks like.")
print("For full functionality, please install the dependencies as shown.")
print("\nPress Ctrl+C to stop the server.")

with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
    httpd.serve_forever()