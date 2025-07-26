let manualItems = [];
let csvData = [];

// Mode selection
function showManualEntry() {
    document.querySelector('.mode-selection').style.display = 'none';
    document.getElementById('manualEntrySection').style.display = 'block';
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('configSection').style.display = 'none';
}

function showFileUpload() {
    document.querySelector('.mode-selection').style.display = 'none';
    document.getElementById('manualEntrySection').style.display = 'none';
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('configSection').style.display = 'none';
}

// Manual entry functions
function addItem() {
    const sku = document.getElementById('skuInput').value.trim();
    const price = parseFloat(document.getElementById('priceInput').value);
    const quantity = parseInt(document.getElementById('quantityInput').value);
    
    if (!sku || isNaN(price) || isNaN(quantity) || quantity < 1) {
        alert('Please fill all fields with valid values');
        return;
    }
    
    manualItems.push({ sku, price, quantity });
    
    // Clear inputs
    document.getElementById('skuInput').value = '';
    document.getElementById('priceInput').value = '';
    document.getElementById('quantityInput').value = '1';
    document.getElementById('skuInput').focus();
    
    updateItemsTable();
}

function removeItem(index) {
    manualItems.splice(index, 1);
    updateItemsTable();
}

function updateItemsTable() {
    const tbody = document.getElementById('itemsTableBody');
    tbody.innerHTML = '';
    
    let totalItems = 0;
    let totalLabels = 0;
    
    manualItems.forEach((item, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${item.sku}</td>
            <td>$${item.price.toFixed(2)}</td>
            <td>${item.quantity}</td>
            <td>${item.quantity}</td>
            <td><button onclick="removeItem(${index})" class="btn-small btn-danger">Remove</button></td>
        `;
        totalItems++;
        totalLabels += item.quantity;
    });
    
    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalLabels').textContent = totalLabels;
    
    // Show/hide table
    document.getElementById('itemsTableContainer').style.display = manualItems.length > 0 ? 'block' : 'none';
}

// Generate from manual entry
function generateFromManual() {
    if (manualItems.length === 0) {
        alert('Please add at least one item');
        return;
    }
    
    const format = document.getElementById('formatSelectManual').value;
    generateLabels(manualItems, format);
}

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

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
            csvData = data.data;
            displayCSVPreview(data);
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('configSection').style.display = 'block';
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

function displayCSVPreview(data) {
    document.getElementById('rowCount').textContent = `${data.row_count}`;
    
    const tbody = document.getElementById('csvPreviewBody');
    tbody.innerHTML = '';
    
    // Show first 10 items
    const previewData = data.data.slice(0, 10);
    previewData.forEach(row => {
        const tr = tbody.insertRow();
        tr.innerHTML = `
            <td>${row.sku || ''}</td>
            <td>$${parseFloat(row.price || 0).toFixed(2)}</td>
            <td>${row.quantity || 1}</td>
        `;
    });
    
    if (data.data.length > 10) {
        const tr = tbody.insertRow();
        tr.innerHTML = `<td colspan="3" style="text-align: center;">... and ${data.data.length - 10} more items</td>`;
    }
}

// Generate from CSV
function generateFromCSV() {
    if (csvData.length === 0) {
        alert('No data to generate');
        return;
    }
    
    const format = document.getElementById('formatSelectCSV').value;
    generateLabels(csvData, format);
}

// Common generate function
function generateLabels(items, format) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="loading"></div> Generating...';
    btn.disabled = true;
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: items,
            format: format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('resultMessage').textContent = 
                `Generated ${data.label_count} labels using ${data.format_name} format`;
            document.getElementById('downloadBtn').href = data.download_url;
            
            document.querySelector('.mode-selection').style.display = 'none';
            document.getElementById('manualEntrySection').style.display = 'none';
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('configSection').style.display = 'none';
            document.getElementById('resultSection').style.display = 'block';
        } else {
            alert(data.error || 'Generation failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during generation');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function resetForm() {
    manualItems = [];
    csvData = [];
    document.getElementById('uploadForm').reset();
    document.getElementById('manualEntrySection').style.display = 'none';
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('configSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    document.querySelector('.mode-selection').style.display = 'block';
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
        <p class="upload-hint">Expected columns: SKU, Price, Quantity</p>
        <input type="file" id="fileInput" accept=".csv" hidden>
    `;
}

// Allow Enter key to add items
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['skuInput', 'priceInput', 'quantityInput'];
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    addItem();
                }
            });
        }
    });
});