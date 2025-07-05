let uploadedFilename = null;
let csvColumns = [];

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

function handleFileUpload(file) {
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading state
    uploadArea.innerHTML = '<div class="loading"></div><p>Uploading and parsing CSV...</p>';
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            uploadedFilename = data.filename;
            csvColumns = data.columns;
            displayPreview(data);
            populateFieldSelectors(data.columns);
            document.getElementById('configSection').style.display = 'block';
            document.querySelector('.upload-section').style.display = 'none';
        } else {
            alert(data.error || 'Upload failed');
            resetUploadArea();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during upload');
        resetUploadArea();
    });
}

function displayPreview(data) {
    document.getElementById('rowCount').textContent = `${data.total_rows}`;
    
    const table = document.getElementById('previewTable');
    table.innerHTML = '';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    data.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body with preview data
    const tbody = document.createElement('tbody');
    data.preview.forEach(row => {
        const tr = document.createElement('tr');
        data.columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
}

function populateFieldSelectors(columns) {
    const productField = document.getElementById('productField');
    const priceField = document.getElementById('priceField');
    const skuField = document.getElementById('skuField');
    
    // Clear existing options
    [productField, priceField, skuField].forEach(select => {
        select.innerHTML = '';
    });
    
    // Add 'None' option for SKU field
    skuField.innerHTML = '<option value="">-- None --</option>';
    
    // Populate all selectors
    columns.forEach(col => {
        [productField, priceField, skuField].forEach(select => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
    });
    
    // Auto-select common field names
    autoSelectFields(columns);
}

function autoSelectFields(columns) {
    const productField = document.getElementById('productField');
    const priceField = document.getElementById('priceField');
    const skuField = document.getElementById('skuField');
    
    columns.forEach(col => {
        const colLower = col.toLowerCase();
        
        // Auto-select product field
        if (colLower.includes('product') || colLower.includes('name') || colLower.includes('title')) {
            productField.value = col;
        }
        
        // Auto-select price field
        if (colLower.includes('price') || colLower.includes('cost') || colLower.includes('amount')) {
            priceField.value = col;
        }
        
        // Auto-select SKU field
        if (colLower.includes('sku') || colLower.includes('code') || colLower.includes('id')) {
            skuField.value = col;
        }
    });
}

// Form submission
document.getElementById('generateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        filename: uploadedFilename,
        format: document.getElementById('formatSelect').value,
        product_field: document.getElementById('productField').value,
        price_field: document.getElementById('priceField').value,
        sku_field: document.getElementById('skuField').value
    };
    
    // Validate required fields
    if (!formData.product_field || !formData.price_field) {
        alert('Please select both product and price fields');
        return;
    }
    
    // Show loading state
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResults(data);
        } else {
            alert(data.error || 'Generation failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during generation');
    })
    .finally(() => {
        generateBtn.textContent = 'Generate Labels';
        generateBtn.disabled = false;
    });
});

function showResults(data) {
    document.getElementById('configSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
    
    document.getElementById('resultMessage').textContent = 
        `Generated ${data.total_labels} labels successfully!`;
    
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.href = data.download_url;
    downloadBtn.download = data.filename;
}

function resetForm() {
    uploadedFilename = null;
    csvColumns = [];
    
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('configSection').style.display = 'none';
    document.querySelector('.upload-section').style.display = 'block';
    
    resetUploadArea();
}

function resetUploadArea() {
    uploadArea.innerHTML = `
        <svg class="upload-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <p class="upload-text">Drag and drop your CSV file here, or click to browse</p>
        <p class="upload-hint">Maximum file size: 16MB</p>
        <input type="file" id="fileInput" accept=".csv" hidden>
    `;
    
    // Re-attach event listeners
    const newFileInput = document.getElementById('fileInput');
    newFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}