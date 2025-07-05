from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
import uuid
from datetime import datetime
from src.csv_parser import CSVParser
from src.pdf_generator import PDFGenerator
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
    return render_template('index.html', formats=LABEL_FORMATS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            parser = CSVParser(filepath)
            data = parser.parse()
            columns = parser.get_columns()
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'columns': columns,
                'preview': data[:5],  # First 5 rows for preview
                'total_rows': len(data)
            })
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

@app.route('/generate', methods=['POST'])
def generate_labels():
    try:
        data = request.json
        filename = data.get('filename')
        format_key = data.get('format', 'avery_5160')
        field_mapping = {
            'product': data.get('product_field'),
            'price': data.get('price_field'),
            'sku': data.get('sku_field')
        }
        
        if not filename:
            return jsonify({'error': 'No file specified'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Parse the CSV again with the field mapping
        parser = CSVParser(filepath)
        csv_data = parser.parse()
        
        # Generate unique output filename
        output_filename = f"labels_{uuid.uuid4().hex[:8]}.pdf"
        
        # Generate PDF
        generator = PDFGenerator(app.config['OUTPUT_FOLDER'])
        output_path = generator.generate_labels(
            csv_data,
            LABEL_FORMATS[format_key],
            output_filename,
            field_mapping
        )
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'filename': output_filename,
            'total_labels': len(csv_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True, download_name=f'price_labels_{datetime.now().strftime("%Y%m%d")}.pdf')
        return "File not found", 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)