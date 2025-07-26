from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
from datetime import datetime
from src.csv_parser import CSVParser
from src.pdf_generator_barcode import PDFGeneratorBarcode
from src.label_formats import LABEL_FORMATS

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index_barcode.html', formats=LABEL_FORMATS)

@app.route('/products')
def get_products():
    """Return product data for autocomplete"""
    try:
        products_file = os.path.join('data', 'products.csv')
        parser = CSVParser(products_file)
        data = parser.parse()
        
        # Transform data for frontend
        products = []
        for row in data:
            products.append({
                'sku': row.get('Name', ''),
                'price': float(row.get('Unit Price', 0)),
                'id': row.get('Internal ID', '')
            })
        
        return jsonify(products)
    except Exception as e:
        return jsonify([])  # Return empty array if file not found

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Parse CSV to get columns
        try:
            parser = CSVParser(filepath)
            data = parser.parse()
            
            # Ensure required columns exist
            required_cols = ['sku', 'price', 'quantity']
            columns = parser.get_columns()
            
            # Try to map columns intelligently
            mapped_data = []
            for row in data:
                mapped_row = {}
                # SKU mapping
                for col in columns:
                    if 'sku' in col.lower() or 'code' in col.lower() or 'id' in col.lower():
                        mapped_row['sku'] = row.get(col, '')
                        break
                # Price mapping
                for col in columns:
                    if 'price' in col.lower() or 'cost' in col.lower():
                        mapped_row['price'] = row.get(col, 0)
                        break
                # Quantity mapping
                for col in columns:
                    if 'qty' in col.lower() or 'quantity' in col.lower() or 'qnty' in col.lower():
                        mapped_row['quantity'] = row.get(col, 1)
                        break
                
                # Fallback to original data
                if 'sku' not in mapped_row:
                    mapped_row['sku'] = row.get('sku', '')
                if 'price' not in mapped_row:
                    mapped_row['price'] = row.get('price', 0)
                if 'quantity' not in mapped_row:
                    mapped_row['quantity'] = row.get('quantity', 1)
                
                mapped_data.append(mapped_row)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'data': mapped_data,
                'row_count': len(mapped_data)
            })
        except Exception as e:
            os.remove(filepath)  # Clean up failed upload
            return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

@app.route('/generate', methods=['POST'])
def generate_labels():
    try:
        data = request.json
        label_format = data.get('format', 'avery_5160')
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided'}), 400
        
        # Generate PDF
        output_filename = f"labels_{uuid.uuid4().hex[:8]}.pdf"
        generator = PDFGeneratorBarcode(app.config['OUTPUT_FOLDER'])
        
        output_path = generator.generate_labels(
            items,
            LABEL_FORMATS[label_format],
            output_filename
        )
        
        # Calculate total labels (sum of quantities)
        total_labels = sum(int(item.get('quantity', 1)) for item in items)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'label_count': total_labels,
            'format_name': LABEL_FORMATS[label_format].name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name=f'labels_{datetime.now().strftime("%Y%m%d")}.pdf')
        return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/formats')
def get_formats():
    formats_list = []
    for key, fmt in LABEL_FORMATS.items():
        formats_list.append({
            'id': key,
            'name': fmt.name,
            'width': fmt.width,
            'height': fmt.height,
            'columns': fmt.columns,
            'rows': fmt.rows,
            'labels_per_page': fmt.columns * fmt.rows
        })
    return jsonify(formats_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)