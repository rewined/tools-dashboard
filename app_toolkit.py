# Version: 2025-07-06-17:00 - Flexible database configuration
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for, Blueprint
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
from datetime import datetime

# Import existing label printer functionality
from src.csv_parser import CSVParser
from src.pdf_generator_barcode import PDFGeneratorBarcode
from src.label_formats import LABEL_FORMATS

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Database configuration - can be Supabase or any other database
DATABASE_URL = os.environ.get('DATABASE_URL')
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://ounsopanyjrjqmhbmxej.supabase.co")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91bnNvcGFueWpyanFtaGJteGVqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTg0MjM5OCwiZXhwIjoyMDY3NDE4Mzk4fQ.IesrOV1H-jGmKx2FtBLbtFvmXH8JA2ArMIjyvGO6aUU")

# Initialize database client if available
supabase_client = None
try:
    from supabase import create_client, Client
    if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://ounsopanyjrjqmhbmxej.supabase.co":
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        print("Supabase credentials not configured - using CSV/sample data")
except ImportError:
    print("Supabase client not available - falling back to CSV/sample data")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase_client = None

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

# Sample products as fallback (expanded set)
SAMPLE_PRODUCTS = [
    {'sku': 'CF20101001', 'price': 78.00, 'id': '61220', 'description': 'Candlefish No. 1 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101002', 'price': 78.00, 'id': '104526', 'description': 'Candlefish No. 2 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101003', 'price': 78.00, 'id': '104527', 'description': 'Candlefish No. 3 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101004', 'price': 78.00, 'id': '61234', 'description': 'Candlefish No. 4 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101005', 'price': 78.00, 'id': '104528', 'description': 'Candlefish No. 5 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101006', 'price': 78.00, 'id': '104529', 'description': 'Candlefish No. 6 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101007', 'price': 78.00, 'id': '104530', 'description': 'Candlefish No. 7 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101008', 'price': 78.00, 'id': '61206', 'description': 'Candlefish No. 8 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101009', 'price': 78.00, 'id': '61196', 'description': 'Candlefish No. 9 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101010', 'price': 78.00, 'id': '104531', 'description': 'Candlefish No. 10 2.5 oz Tin-CASE(12)', 'case_qty': 12},
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_products_from_database():
    """Try to get products from database (Supabase or PostgreSQL)"""
    products = []
    
    if supabase_client:
        try:
            result = supabase_client.table('products').select('*').execute()
            if result.data:
                for row in result.data:
                    products.append({
                        'sku': row.get('name', ''),
                        'price': float(row.get('unit_price', 0)),
                        'id': str(row.get('internal_id', '')),
                        'description': row.get('description', ''),
                        'case_qty': int(row.get('case_qty', 1))
                    })
                return products
        except Exception as e:
            print(f"Supabase error: {e}")
    
    return None

# ==========================================
# MAIN DASHBOARD ROUTES
# ==========================================

@app.route('/test-ol1000wx')
def test_ol1000wx():
    """Direct test endpoint for OL1000WX"""
    return jsonify({
        'ol1000wx_exists': 'ol1000wx' in LABEL_FORMATS,
        'all_formats': list(LABEL_FORMATS.keys()),
        'total_formats': len(LABEL_FORMATS),
        'deployment_time': datetime.now().isoformat()
    })

@app.route('/')
def dashboard():
    """Main dashboard showing all available tools"""
    tools = [
        {
            'name': 'Label Printer',
            'description': 'Generate barcode price stickers from SKU data',
            'icon': '🏷️',
            'url': '/labels',
            'status': 'active'
        },
        {
            'name': 'Inventory Scanner',
            'description': 'Scan and update inventory counts',
            'icon': '📊',
            'url': '/inventory',
            'status': 'coming-soon'
        },
        {
            'name': 'Report Generator',
            'description': 'Generate custom business reports',
            'icon': '📈',
            'url': '/reports',
            'status': 'coming-soon'
        },
        {
            'name': 'Data Analyzer',
            'description': 'Analyze sales and product data',
            'icon': '🔍',
            'url': '/analyzer',
            'status': 'coming-soon'
        }
    ]
    return render_template('dashboard.html', tools=tools)

# ==========================================
# DEBUG ROUTES
# ==========================================

@app.route('/debug/files')
def debug_files():
    """Debug endpoint to check file system and database connections"""
    debug_info = {
        'cwd': os.getcwd(),
        'data_exists': os.path.exists('data'),
        'products_exists': os.path.exists('data/products.csv'),
        'deployment_version': '2025-07-06-17:00-flexible-db',
        'database_configured': False,
        'supabase_available': supabase_client is not None
    }
    
    # Test database connection
    if supabase_client:
        try:
            result = supabase_client.table('products').select('id').limit(1).execute()
            debug_info['database_configured'] = True
            debug_info['products_in_db'] = len(result.data) if result.data else 0
        except Exception as e:
            debug_info['database_error'] = str(e)
    
    if os.path.exists('data'):
        try:
            debug_info['data_files'] = os.listdir('data')
        except:
            debug_info['data_files'] = 'Cannot list files'
    
    return jsonify(debug_info)

@app.route('/version')
def version():
    """Version info endpoint"""
    import subprocess
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()[:8]
    except:
        git_hash = 'unknown'
    
    return jsonify({
        'version': '1.0.3',
        'git_commit': git_hash,
        'formats_count': len(LABEL_FORMATS),
        'has_ol1000wx': 'ol1000wx' in LABEL_FORMATS,
        'format_names': list(LABEL_FORMATS.keys()),
        'ol1000wx_details': LABEL_FORMATS.get('ol1000wx').name if 'ol1000wx' in LABEL_FORMATS else None,
        'deploy_timestamp': os.environ.get('FORCE_DEPLOY', 'not set')
    })

# ==========================================
# LABEL PRINTER ROUTES
# ==========================================

@app.route('/labels')
def labels():
    """Label printer main page"""
    return render_template('tools/labels.html', formats=LABEL_FORMATS)

@app.route('/labels/products')
def labels_get_products():
    """Return product data for autocomplete - try database first, then CSV, then samples"""
    try:
        # Try database first
        products = get_products_from_database()
        if products:
            return jsonify(products)
        
        # Try CSV fallback
        products_file = os.path.join('data', 'products.csv')
        if os.path.exists(products_file):
            parser = CSVParser(products_file)
            data = parser.parse()
            
            products = []
            for row in data:
                products.append({
                    'sku': row.get('Name', ''),
                    'price': float(row.get('Unit Price', 0)),
                    'id': row.get('Internal ID', ''),
                    'description': row.get('Description', ''),
                    'case_qty': int(row.get('Case Qty', 1))
                })
            
            return jsonify(products)
        
        # Final fallback to sample products
        return jsonify(SAMPLE_PRODUCTS)
            
    except Exception as e:
        # If everything fails, return sample products
        print(f"Error getting products: {e}")
        return jsonify(SAMPLE_PRODUCTS)

@app.route('/labels/upload', methods=['POST'])
def labels_upload():
    """Handle CSV upload for label printer"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            unique_filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            parser = CSVParser(filepath)
            data = parser.parse()
            
            # Smart column mapping
            mapped_data = []
            for row in data:
                mapped_row = {}
                columns = list(row.keys())
                
                # Find SKU column
                for col in columns:
                    if any(keyword in col.lower() for keyword in ['sku', 'name', 'product', 'item']):
                        mapped_row['sku'] = row.get(col, '')
                        break
                
                # Find price column
                for col in columns:
                    if any(keyword in col.lower() for keyword in ['price', 'cost', 'amount']):
                        mapped_row['price'] = float(row.get(col, 0))
                        break
                
                # Find quantity column
                for col in columns:
                    if any(keyword in col.lower() for keyword in ['qty', 'quantity', 'qnty']):
                        mapped_row['quantity'] = int(row.get(col, 1))
                        break
                
                # Find description column
                for col in columns:
                    if 'description' in col.lower():
                        mapped_row['description'] = row.get(col, '')
                        break
                
                # Find case quantity column
                for col in columns:
                    if any(keyword in col.lower() for keyword in ['case qty', 'case_qty', 'case quantity']):
                        mapped_row['case_qty'] = int(row.get(col, 1))
                        break
                
                # Set defaults for missing fields
                if 'sku' not in mapped_row:
                    mapped_row['sku'] = row.get('sku', '')
                if 'price' not in mapped_row:
                    mapped_row['price'] = row.get('price', 0)
                if 'quantity' not in mapped_row:
                    mapped_row['quantity'] = row.get('quantity', 1)
                if 'description' not in mapped_row:
                    mapped_row['description'] = row.get('description', '')
                if 'case_qty' not in mapped_row:
                    mapped_row['case_qty'] = row.get('case_qty', 1)
                
                mapped_data.append(mapped_row)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'data': mapped_data,
                'row_count': len(mapped_data)
            })
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

@app.route('/labels/generate', methods=['POST'])
def labels_generate():
    """Generate labels PDF"""
    try:
        data = request.json
        label_format = data.get('format', 'avery_5160')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided'}), 400
        
        output_filename = f"labels_{uuid.uuid4().hex[:8]}.pdf"
        generator = PDFGeneratorBarcode(app.config['OUTPUT_FOLDER'])
        
        output_path = generator.generate_labels(
            items,
            LABEL_FORMATS[label_format],
            output_filename
        )
        
        total_labels = sum(int(item.get('quantity', 1)) for item in items)
        
        return jsonify({
            'success': True,
            'download_url': f'/labels/download/{output_filename}',
            'label_count': total_labels
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/labels/download/<filename>')
def labels_download(filename):
    """Download generated labels"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, as_attachment=False, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@app.route('/labels/debug-formats')
def debug_formats():
    """Debug endpoint to check available label formats"""
    formats_list = {key: format.name for key, format in LABEL_FORMATS.items()}
    return jsonify(formats_list)

# ==========================================
# COMING SOON ROUTES
# ==========================================

@app.route('/inventory')
@app.route('/reports')
@app.route('/analyzer')
def coming_soon():
    """Placeholder for future tools"""
    return render_template('tools/coming_soon.html')

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)