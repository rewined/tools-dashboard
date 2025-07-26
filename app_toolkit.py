# Version: 2025-07-06-17:00 - Flexible database configuration
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for, Blueprint
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
from datetime import datetime
import qrcode
import io
import base64
import json

# Import existing label printer functionality
from src.csv_parser import CSVParser
from src.pdf_generator_barcode import PDFGeneratorBarcode
from src.pdf_generator_candle import PDFGeneratorCandle
from src.label_formats import LABEL_FORMATS
from src.models import db, CandleTest, CandleTrial, CandleEvaluation, Product
from src.netsuite_client import NetSuiteClient

# Import wick-onomics functionality
try:
    from src.wick_api import wick_api
    from src.wick_predictor import WickPredictor
    wick_api_available = True
except ImportError:
    wick_api_available = False
    print("Wick-onomics modules not available")
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Database configuration
# Force SQLite for local candle testing database (not Supabase)
if os.environ.get('DATABASE_URL', '').startswith('postgresql://'):
    # Railway may set DATABASE_URL to Supabase, but we want SQLite for candle testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candle_testing.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///candle_testing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Database configuration - can be Supabase or any other database
DATABASE_URL = os.environ.get('DATABASE_URL')
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://ounsopanyjrjqmhbmxej.supabase.co")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91bnNvcGFueWpyanFtaGJteGVqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTg0MjM5OCwiZXhwIjoyMDY3NDE4Mzk4fQ.IesrOV1H-jGmKx2FtBLbtFvmXH8JA2ArMIjyvGO6aUU")

# Initialize database client if available
supabase_client = None
try:
    from supabase import create_client, Client
    # Always use the Supabase client with the provided URL and key
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase client initialized")
    else:
        print("Supabase credentials not configured - using CSV/sample data")
except ImportError:
    print("Supabase client not available - falling back to CSV/sample data")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase_client = None

# Register wick API blueprint if available
if wick_api_available and supabase_client:
    # Initialize predictor with supabase client
    app.register_blueprint(wick_api)
    print("✅ Wick-onomics API registered at /api/wick")
else:
    print("⚠️  Wick-onomics API not available - Supabase required")
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
            'name': 'Candle Testing',
            'description': 'Test and track candle burn performance',
            'icon': '🕯️',
            'url': '/candle-testing',
            'status': 'active'
        },
        {
            'name': 'Wick Analytics',
            'description': 'AI-powered wick predictions and analytics',
            'icon': '🔮',
            'url': '/wick-analytics',
            'status': 'active' if wick_api_available and supabase_client else 'coming-soon'
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

# Version route removed - defined later in the file with full features

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
# CANDLE TESTING ROUTES
# ==========================================

# Database initialization
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        
        # Add default products if none exist
        if Product.query.count() == 0:
            default_products = [
                # Vessels
                {'product_id': 'ves-001', 'product_type': 'vessel', 'name': 'VES-001 - 8oz Clear Glass Jar'},
                {'product_id': 'ves-002', 'product_type': 'vessel', 'name': 'VES-002 - 10oz Frosted Glass'},
                {'product_id': 'ves-003', 'product_type': 'vessel', 'name': 'VES-003 - 12oz Black Ceramic'},
                {'product_id': 'ves-004', 'product_type': 'vessel', 'name': 'VES-004 - 6oz Tin Container'},
                # Waxes
                {'product_id': 'wax-001', 'product_type': 'wax', 'name': 'WAX-001 - Soy Wax 464'},
                {'product_id': 'wax-002', 'product_type': 'wax', 'name': 'WAX-002 - Coconut Soy Blend'},
                {'product_id': 'wax-003', 'product_type': 'wax', 'name': 'WAX-003 - Paraffin Blend'},
                {'product_id': 'wax-004', 'product_type': 'wax', 'name': 'WAX-004 - Beeswax Blend'},
                # Fragrances
                {'product_id': 'oil-001', 'product_type': 'fragrance', 'name': 'OIL-001 - Lavender Fields'},
                {'product_id': 'oil-002', 'product_type': 'fragrance', 'name': 'OIL-002 - Vanilla Bean'},
                {'product_id': 'oil-003', 'product_type': 'fragrance', 'name': 'OIL-003 - Ocean Breeze'},
                {'product_id': 'oil-004', 'product_type': 'fragrance', 'name': 'OIL-004 - Citrus Burst'},
                # Wicks
                {'product_id': 'wick-001', 'product_type': 'wick', 'name': 'Wick.CD4 - Cotton Core 4'},
                {'product_id': 'wick-002', 'product_type': 'wick', 'name': 'Wick.CD6 - Cotton Core 6'},
                {'product_id': 'wick-003', 'product_type': 'wick', 'name': 'Wick.CD8 - Cotton Core 8'},
                {'product_id': 'wick-004', 'product_type': 'wick', 'name': 'Wick.ECO4 - Eco Series 4'},
                {'product_id': 'wick-005', 'product_type': 'wick', 'name': 'Wick.ECO6 - Eco Series 6'},
                {'product_id': 'wick-006', 'product_type': 'wick', 'name': 'Wick.ECO8 - Eco Series 8'},
                {'product_id': 'wick-007', 'product_type': 'wick', 'name': 'Wick.LX10 - LX Series 10'},
                {'product_id': 'wick-008', 'product_type': 'wick', 'name': 'Wick.LX12 - LX Series 12'}
            ]
            
            for product_data in default_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()

# Initialize database on startup
init_db()

# Initialize NetSuite client
netsuite_client = NetSuiteClient()
if netsuite_client.is_configured:
    print(f"✅ NetSuite client configured for account: {netsuite_client.account_id}")
else:
    print("⚠️  NetSuite client not configured - using fallback data")
    print("Set these environment variables for direct NetSuite access:")
    print("  NETSUITE_ACCOUNT_ID, NETSUITE_CONSUMER_KEY, NETSUITE_CONSUMER_SECRET")
    print("  NETSUITE_TOKEN_ID, NETSUITE_TOKEN_SECRET")

@app.route('/version')
def version():
    """Check deployment version"""
    return jsonify({
        'version': '1.1.0',
        'features': {
            'candle_testing': True,
            'thermal_printer_labels': True,
            'one_label_per_page': True,
            'netsuite_integration': True
        },
        'label_format': 'Each label on separate 1x4 inch page',
        'last_update': '2025-07-25 - Thermal printer support',
        'pdf_page_size': '1x4 inches per page'
    })

@app.route('/candle-testing')
def candle_testing_dashboard():
    """Main dashboard for candle testing tool"""
    # Get all tests from database
    tests = CandleTest.query.order_by(CandleTest.created_at.desc()).all()
    
    tests_list = []
    for test in tests:
        test_dict = test.to_dict()
        
        # Calculate progress
        completed_evaluations = 0
        total_trials = len(test.trials)
        
        for trial in test.trials:
            evaluations = trial.get_evaluations_dict()
            if all(hour in evaluations for hour in ['1hr', '2hr', '4hr']):
                completed_evaluations += 1
        
        test_dict['progress'] = f"{completed_evaluations}/{total_trials}"
        test_dict['status'] = 'Completed' if completed_evaluations == total_trials else 'Active'
        tests_list.append(test_dict)
    
    return render_template('tools/candle_testing_dashboard.html', tests=tests_list)

@app.route('/candle-testing/create')
def candle_testing_create():
    """Create new candle test form"""
    return render_template('tools/candle_testing_create.html')

@app.route('/candle-testing/create', methods=['POST'])
def candle_testing_create_post():
    """Handle test creation"""
    try:
        data = request.json
        
        # Generate unique test ID
        test_id = f"CT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create test record
        test = CandleTest(
            id=test_id,
            vessel=data['vessel'],
            wax=data['wax'],
            fragrance=data['fragrance'],
            blend_percentage=data['blend_percentage'],
            created_by=data.get('created_by', 'Unknown')
        )
        db.session.add(test)
        
        # Create trials for each wick
        for i, wick in enumerate(data['wicks']):
            trial_id = f"{test_id}-T{i+1}"
            trial = CandleTrial(
                id=trial_id,
                test_id=test_id,
                trial_number=i + 1,
                wick=wick
            )
            db.session.add(trial)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': 'Test created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/candle-testing/products')
def candle_testing_products():
    """Get product data for dropdowns"""
    
    # Try direct NetSuite connection first
    if netsuite_client.is_configured:
        try:
            print("Fetching products directly from NetSuite...")
            products = netsuite_client.get_candle_products()
            
            # Update local cache with NetSuite data
            if any(products.values()):
                Product.query.delete()
                
                for vessel in products.get('vessels', []):
                    db.session.add(Product(
                        product_id=vessel['id'],
                        product_type='vessel',
                        name=vessel['name']
                    ))
                for wax in products.get('waxes', []):
                    db.session.add(Product(
                        product_id=wax['id'],
                        product_type='wax',
                        name=wax['name']
                    ))
                for fragrance in products.get('fragrances', []):
                    db.session.add(Product(
                        product_id=fragrance['id'],
                        product_type='fragrance',
                        name=fragrance['name']
                    ))
                for wick in products.get('wicks', []):
                    db.session.add(Product(
                        product_id=wick['id'],
                        product_type='wick',
                        name=wick['name']
                    ))
                
                try:
                    db.session.commit()
                    print(f"✅ Cached {sum(len(v) for v in products.values())} products from NetSuite")
                except:
                    db.session.rollback()
                
                return jsonify(products)
                
        except Exception as e:
            print(f"NetSuite direct connection error: {e}")
    
    # Try to get products from Supabase/NetSuite second
    elif supabase_client:
        try:
            # Query for candle-specific products
            result = supabase_client.table('products').select('*').execute()
            
            if result.data:
                vessels = []
                waxes = []
                fragrances = []
                wicks = []
                
                for row in result.data:
                    product_name = row.get('name', '')
                    product_id = str(row.get('internal_id', ''))
                    description = row.get('description', '')
                    
                    # Categorize products based on naming patterns
                    if product_name.lower().startswith('ves-') or 'vessel' in description.lower() or 'jar' in description.lower() or 'container' in description.lower():
                        vessels.append({
                            'id': product_id,
                            'name': f"{product_name} - {description}" if description else product_name
                        })
                    elif product_name.lower().startswith('wax-') or 'wax' in description.lower():
                        waxes.append({
                            'id': product_id,
                            'name': f"{product_name} - {description}" if description else product_name
                        })
                    elif product_name.lower().startswith('oil-') or 'fragrance' in description.lower() or 'scent' in description.lower():
                        fragrances.append({
                            'id': product_id,
                            'name': f"{product_name} - {description}" if description else product_name
                        })
                    elif product_name.lower().startswith('wick') or 'wick' in description.lower():
                        wicks.append({
                            'id': product_id,
                            'name': f"{product_name} - {description}" if description else product_name
                        })
                
                # If we found products in NetSuite, update our local cache
                if vessels or waxes or fragrances or wicks:
                    # Clear existing cached products
                    Product.query.delete()
                    
                    # Add NetSuite products to local cache
                    for vessel in vessels:
                        db.session.add(Product(
                            product_id=vessel['id'],
                            product_type='vessel',
                            name=vessel['name']
                        ))
                    for wax in waxes:
                        db.session.add(Product(
                            product_id=wax['id'],
                            product_type='wax',
                            name=wax['name']
                        ))
                    for fragrance in fragrances:
                        db.session.add(Product(
                            product_id=fragrance['id'],
                            product_type='fragrance',
                            name=fragrance['name']
                        ))
                    for wick in wicks:
                        db.session.add(Product(
                            product_id=wick['id'],
                            product_type='wick',
                            name=wick['name']
                        ))
                    
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                    
                    return jsonify({
                        'vessels': vessels,
                        'waxes': waxes,
                        'fragrances': fragrances,
                        'wicks': wicks
                    })
                
        except Exception as e:
            print(f"Supabase error in candle products: {e}")
    
    # Fall back to local database cache
    products = {
        'vessels': [p.to_dict() for p in Product.query.filter_by(product_type='vessel').all()],
        'waxes': [p.to_dict() for p in Product.query.filter_by(product_type='wax').all()],
        'fragrances': [p.to_dict() for p in Product.query.filter_by(product_type='fragrance').all()],
        'wicks': [p.to_dict() for p in Product.query.filter_by(product_type='wick').all()]
    }
    return jsonify(products)

@app.route('/candle-testing/products/search')
def candle_testing_products_search():
    """Search for specific products by prefix or pattern"""
    query = request.args.get('q', '')
    product_type = request.args.get('type', '')
    
    if supabase_client and query:
        try:
            # Use Supabase's filtering capabilities
            result = supabase_client.table('products').select('*').ilike('name', f'{query}%').execute()
            
            products = []
            for row in result.data:
                products.append({
                    'id': str(row.get('internal_id', '')),
                    'name': f"{row.get('name', '')} - {row.get('description', '')}" if row.get('description') else row.get('name', ''),
                    'sku': row.get('name', ''),
                    'description': row.get('description', '')
                })
            
            return jsonify({'results': products})
            
        except Exception as e:
            print(f"Supabase search error: {e}")
    
    return jsonify({'results': []})

@app.route('/candle-testing/generate-labels/<test_id>', methods=['POST'])
def candle_testing_generate_labels(test_id):
    """Generate labels for a test"""
    try:
        test = CandleTest.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        # Generate unique filename
        output_filename = f"candle_test_{test_id}_{uuid.uuid4().hex[:8]}.pdf"
        
        # Get base URL for QR codes
        base_url = request.url_root.rstrip('/')
        
        # Use specialized candle test PDF generator
        generator = PDFGeneratorCandle(app.config['OUTPUT_FOLDER'])
        
        # Convert trials to dict format expected by PDF generator
        trials_dict = [trial.to_dict() for trial in test.trials]
        
        # Use 1x4" format for candle test labels
        output_path = generator.generate_test_labels(
            test.to_dict(),
            trials_dict,
            LABEL_FORMATS['candle_test_1x4'],
            output_filename,
            base_url
        )
        
        return jsonify({
            'success': True,
            'download_url': f'/labels/download/{output_filename}',
            'label_count': len(test.trials)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/candle-testing/evaluate/<test_id>/<trial_id>')
def candle_testing_evaluate(test_id, trial_id):
    """Evaluation form for a specific trial"""
    test = CandleTest.query.get(test_id)
    if not test:
        return "Test not found", 404
    
    trial = CandleTrial.query.get(trial_id)
    if not trial or trial.test_id != test_id:
        return "Trial not found", 404
    
    # Get existing evaluation data
    evaluation_data = trial.get_evaluations_dict()
    
    return render_template('tools/candle_testing_evaluate.html', 
                         test=test.to_dict(), 
                         trial=trial.to_dict(),
                         evaluation_data=evaluation_data)

@app.route('/candle-testing/api/save-evaluation', methods=['POST'])
def candle_testing_save_evaluation():
    """Save evaluation data"""
    try:
        data = request.json
        trial_id = data['trial_id']
        hour = data['hour']
        
        # Verify trial exists
        trial = CandleTrial.query.get(trial_id)
        if not trial:
            return jsonify({'error': 'Trial not found'}), 404
        
        # Check if evaluation already exists
        existing_eval = CandleEvaluation.query.filter_by(
            trial_id=trial_id,
            evaluation_type=hour
        ).first()
        
        if existing_eval:
            # Update existing evaluation
            if hour == 'post_extinguish':
                existing_eval.after_glow = data.get('after_glow')
                existing_eval.after_smoke = data.get('after_smoke')
            else:
                existing_eval.full_melt_pool = data.get('full_melt_pool')
                existing_eval.melt_pool_depth = data.get('melt_pool_depth')
                existing_eval.external_temp = data.get('external_temp')
                existing_eval.flame_height = data.get('flame_height')
        else:
            # Create new evaluation
            eval = CandleEvaluation(
                trial_id=trial_id,
                evaluation_type=hour
            )
            
            if hour == 'post_extinguish':
                eval.after_glow = data.get('after_glow')
                eval.after_smoke = data.get('after_smoke')
            else:
                eval.full_melt_pool = data.get('full_melt_pool')
                eval.melt_pool_depth = data.get('melt_pool_depth')
                eval.external_temp = data.get('external_temp')
                eval.flame_height = data.get('flame_height')
            
            db.session.add(eval)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Evaluation saved'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/candle-testing/test/<test_id>')
def candle_testing_view_test(test_id):
    """View test details and results"""
    test = CandleTest.query.get(test_id)
    if not test:
        return "Test not found", 404
    
    # Gather evaluation data for all trials
    results = []
    for trial in test.trials:
        trial_data = {
            'trial': trial.to_dict(),
            'evaluations': trial.get_evaluations_dict()
        }
        results.append(trial_data)
    
    return render_template('tools/candle_testing_results.html', 
                         test=test.to_dict(), 
                         results=results)

@app.route('/candle-testing/analyze-assemblies', methods=['POST'])
def analyze_assemblies():
    """Analyze NetSuite assembly items for wick recommendations"""
    try:
        # Initialize NetSuite client
        netsuite = NetSuiteClient()
        
        if not netsuite.is_configured:
            return jsonify({'error': 'NetSuite not configured'}), 400
        
        # Get assembly items with BOM
        assemblies = netsuite.get_assembly_items()
        
        if not assemblies:
            return jsonify({
                'success': False,
                'message': 'No assembly items found with oz fill data'
            })
        
        # Process and categorize assemblies
        analysis_results = []
        
        for assembly in assemblies:
            oz_fill = assembly.get('oz_fill')
            if not oz_fill:
                continue
            
            # Extract components
            components = assembly.get('components', {})
            
            # Create analysis record
            analysis = {
                'assembly_id': assembly.get('id'),
                'assembly_itemid': assembly.get('itemid'),
                'assembly_name': assembly.get('displayname'),
                'oz_fill': oz_fill,
                'vessel': components.get('vessel'),
                'wax': components.get('wax'),
                'fragrance': components.get('fragrance'),
                'wicks': components.get('wicks', [])
            }
            
            analysis_results.append(analysis)
        
        # Store results in session for review
        session['assembly_analysis'] = analysis_results
        
        return jsonify({
            'success': True,
            'count': len(analysis_results),
            'results': analysis_results[:10]  # Return first 10 for preview
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/candle-testing/wick-recommendations/<vessel>')
def get_wick_recommendations(vessel):
    """Get smart wick recommendations based on vessel and other factors"""
    try:
        # Check if we can use the advanced wick-onomics system
        if wick_api_available and supabase_client:
            # Try to get vessel, wax, and fragrance IDs from request
            wax = request.args.get('wax', '')
            fragrance = request.args.get('fragrance', '')
            
            # Look up IDs in database
            try:
                vessel_result = supabase_client.table('vessels').select('id').ilike('name', f'%{vessel}%').limit(1).execute()
                wax_result = supabase_client.table('wax_types').select('id').ilike('name', f'%{wax}%').limit(1).execute() if wax else None
                fragrance_result = supabase_client.table('fragrance_oils').select('id').ilike('name', f'%{fragrance}%').limit(1).execute() if fragrance else None
                
                if vessel_result.data and wax_result and wax_result.data and fragrance_result and fragrance_result.data:
                    # Use the ML-powered predictor
                    predictor = WickPredictor(supabase_client)
                    recommendations = predictor.get_comprehensive_recommendations(
                        vessel_id=vessel_result.data[0]['id'],
                        wax_type_id=wax_result.data[0]['id'],
                        fragrance_id=fragrance_result.data[0]['id'],
                        fragrance_load=8.5  # Default assumption
                    )
                    
                    # Format for UI
                    formatted_recs = []
                    for rec in recommendations[:8]:
                        formatted_recs.append({
                            'wick': rec.wick_name,
                            'probability': rec.confidence,
                            'confidence_class': 'high' if rec.confidence > 0.7 else 'medium' if rec.confidence > 0.4 else 'low',
                            'reason': rec.reasoning
                        })
                    
                    return jsonify({
                        'success': True,
                        'recommendations': formatted_recs,
                        'source': 'ml_prediction'
                    })
            except Exception as e:
                print(f"Error using ML predictor: {e}")
                # Fall through to heuristic method
        
        # Original heuristic-based implementation
        # Parse vessel name to extract size info
        vessel_lower = vessel.lower()
        
        # Try to extract oz from vessel name (multiple patterns)
        import re
        
        # Try different patterns for size extraction
        oz_match = re.search(r'(\d+(?:\.\d+)?)\s*oz', vessel_lower)
        if not oz_match:
            # Try pattern like "8oz" or "8 oz"
            oz_match = re.search(r'(\d+(?:\.\d+)?)\s*oz', vessel_lower)
        if not oz_match:
            # Try pattern with numbers followed by ounce indicators
            oz_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ounce|ounces)', vessel_lower)
        if not oz_match:
            # Try pattern with just numbers (assume common sizes)
            number_match = re.search(r'(\d+(?:\.\d+)?)', vessel_lower)
            if number_match:
                num = float(number_match.group(1))
                # Common candle sizes
                if 4 <= num <= 20:
                    oz_match = number_match
        
        if not oz_match:
            # Default to medium size if we can't determine
            print(f"Could not parse vessel size from: {vessel}, defaulting to 8oz")
            oz_fill = 8.0
        else:
            oz_fill = float(oz_match.group(1))
        
        # Categorize vessel size and estimate diameter
        # Updated based on actual product data - many small candles (2.5oz)
        if oz_fill <= 2.5:
            size_category = 'xs'
            diameter_estimate = (1.5, 2.0)
            base_wicks = ['CD-2', 'CD-3', 'CD-4', 'ECO-1', 'ECO-2']
        elif oz_fill <= 4:
            size_category = 'small'
            diameter_estimate = (2.0, 2.5)
            base_wicks = ['CD-4', 'CD-5', 'CD-6', 'ECO-2', 'ECO-4']
        elif oz_fill <= 8:
            size_category = 'medium'
            diameter_estimate = (2.5, 3.0)
            base_wicks = ['CD-6', 'CD-8', 'CD-10', 'ECO-4', 'ECO-6', 'LX-10']
        elif oz_fill <= 12:
            size_category = 'large'
            diameter_estimate = (3.0, 3.5)
            base_wicks = ['CD-10', 'CD-12', 'CD-14', 'ECO-8', 'ECO-10', 'LX-12', 'HTP-73']
        else:
            size_category = 'xl'
            diameter_estimate = (3.5, 4.0)
            base_wicks = ['CD-14', 'CD-16', 'CD-18', 'ECO-12', 'ECO-14', 'LX-14', 'HTP-93']
        
        # Get wax and fragrance from request args
        wax = request.args.get('wax', '').lower()
        fragrance = request.args.get('fragrance', '').lower()
        
        # Adjust recommendations based on wax type
        wick_adjustment = 0
        if 'soy' in wax:
            wick_adjustment = 0  # Soy tends to be baseline
        elif 'paraffin' in wax:
            wick_adjustment = -1  # Paraffin burns hotter, may need smaller wick
        elif 'coconut' in wax:
            wick_adjustment = 1  # Coconut wax may need larger wick
        elif 'beeswax' in wax:
            wick_adjustment = 1  # Beeswax is dense, needs larger wick
        
        # Adjust for fragrance density (simplified)
        if any(word in fragrance for word in ['vanilla', 'bakery', 'cinnamon', 'spice']):
            wick_adjustment += 1  # Heavy fragrances need larger wicks
        elif any(word in fragrance for word in ['citrus', 'fresh', 'clean', 'light']):
            wick_adjustment -= 0  # Light fragrances burn easier
        
        # Generate recommendations with probability scores
        recommendations = []
        
        # Calculate probabilities for each wick
        for i, base_wick in enumerate(base_wicks):
            # Base probability starts at 85% for primary recommendations
            base_probability = 85 - (i * 5)  # Decrease by 5% for each position
            
            # Extract wick series and size
            parts = base_wick.split('-')
            if len(parts) == 2:
                series = parts[0]
                try:
                    size = int(parts[1])
                    
                    # Primary recommendation
                    prob = base_probability
                    
                    # Adjust probability based on wax type match
                    if series == 'CD' and 'soy' in wax:
                        prob += 5  # CD wicks work well with soy
                    elif series == 'ECO' and ('soy' in wax or 'coconut' in wax):
                        prob += 7  # ECO great for natural waxes
                    elif series == 'LX' and 'paraffin' in wax:
                        prob += 5  # LX good for paraffin
                    elif series == 'HTP' and 'blend' in wax:
                        prob += 5  # HTP good for blends
                    
                    recommendations.append({
                        'wick': f"{series}-{size}",
                        'probability': min(95, prob),  # Cap at 95%
                        'reason': 'Primary size match'
                    })
                    
                    # Size variations based on adjustments
                    if wick_adjustment < 0 and size > 2:
                        # Smaller wick variation
                        var_prob = base_probability - 15
                        recommendations.append({
                            'wick': f"{series}-{size - 2}",
                            'probability': max(40, var_prob),
                            'reason': 'Smaller variant for hot-burning wax'
                        })
                    elif wick_adjustment > 0:
                        # Larger wick variation
                        var_prob = base_probability - 10
                        recommendations.append({
                            'wick': f"{series}-{size + 2}",
                            'probability': max(50, var_prob),
                            'reason': 'Larger variant for dense wax/fragrance'
                        })
                    else:
                        # Both variations for neutral
                        if size > 2:
                            recommendations.append({
                                'wick': f"{series}-{size - 2}",
                                'probability': max(40, base_probability - 20),
                                'reason': 'Alternative smaller size'
                            })
                        recommendations.append({
                            'wick': f"{series}-{size + 2}",
                            'probability': max(40, base_probability - 20),
                            'reason': 'Alternative larger size'
                        })
                    
                except ValueError:
                    recommendations.append({
                        'wick': base_wick,
                        'probability': base_probability,
                        'reason': 'Standard recommendation'
                    })
            else:
                recommendations.append({
                    'wick': base_wick,
                    'probability': base_probability,
                    'reason': 'Standard recommendation'
                })
        
        # Sort by probability and remove duplicates
        seen_wicks = set()
        unique_recommendations = []
        for rec in sorted(recommendations, key=lambda x: x['probability'], reverse=True):
            if rec['wick'] not in seen_wicks:
                seen_wicks.add(rec['wick'])
                unique_recommendations.append(rec)
        
        # Limit to top 8 for better selection
        recommendations = unique_recommendations[:8]
        
        return jsonify({
            'success': True,
            'vessel_size': {
                'oz_fill': oz_fill,
                'category': size_category,
                'diameter_estimate': f"{diameter_estimate[0]}-{diameter_estimate[1]} inches"
            },
            'recommendations': recommendations,
            'factors': {
                'wax_type': wax or 'unknown',
                'fragrance_type': fragrance or 'unknown',
                'adjustment': wick_adjustment
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/candle-testing/admin')
def candle_testing_admin():
    """Admin page for candle testing"""
    return render_template('tools/candle_testing_admin.html')

# ==========================================
# WICK ANALYTICS ROUTE
# ==========================================

@app.route('/wick-analytics')
def wick_analytics():
    """Wick-onomics analytics dashboard"""
    if not wick_api_available or not supabase_client:
        flash('Wick Analytics requires Supabase configuration', 'warning')
        return redirect(url_for('dashboard'))
    return render_template('tools/wick_analytics.html')

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