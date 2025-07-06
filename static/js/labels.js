let rowCount = 1;
let productsData = [];

// Fallback product data in case backend is unavailable
const FALLBACK_PRODUCTS = [
    {'sku': 'CF20101001', 'price': 78.00, 'id': '61220', 'description': 'Candlefish No. 1 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101002', 'price': 78.00, 'id': '104526', 'description': 'Candlefish No. 2 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101003', 'price': 78.00, 'id': '104527', 'description': 'Candlefish No. 3 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101004', 'price': 78.00, 'id': '61234', 'description': 'Candlefish No. 4 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101005', 'price': 78.00, 'id': '104528', 'description': 'Candlefish No. 5 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101006', 'price': 78.00, 'id': '104529', 'description': 'Candlefish No. 6 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101007', 'price': 78.00, 'id': '104530', 'description': 'Candlefish No. 7 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101008', 'price': 78.00, 'id': '61206', 'description': 'Candlefish No. 8 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101009', 'price': 78.00, 'id': '61196', 'description': 'Candlefish No. 9 2.5 oz Tin-CASE(12)', 'case_qty': 12},
    {'sku': 'CF20101010', 'price': 78.00, 'id': '104531', 'description': 'Candlefish No. 10 2.5 oz Tin-CASE(12)', 'case_qty': 12}
];

// Load products data on page load
fetch('/labels/products')
    .then(response => response.json())
    .then(data => {
        if (data && data.length > 0) {
            productsData = data;
        } else {
            // Use fallback data if backend returns empty array
            productsData = FALLBACK_PRODUCTS;
        }
    })
    .catch(error => {
        console.log('Backend unavailable, using fallback products');
        productsData = FALLBACK_PRODUCTS;
    });

function addRow() {
    const grid = document.getElementById('itemsGrid');
    const newRow = document.createElement('div');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <div class="autocomplete-container">
            <input type="text" placeholder="SKU or Description" class="form-control sku-input" data-row="${rowCount}">
            <div class="autocomplete-dropdown" style="display: none;"></div>
        </div>
        <input type="number" placeholder="Price" step="0.01" min="0" class="form-control price-input" data-row="${rowCount}">
        <input type="number" placeholder="QTY" min="1" value="1" class="form-control qty-input" data-row="${rowCount}">
        <button onclick="removeRow(${rowCount})" class="btn-remove">×</button>
    `;
    grid.appendChild(newRow);
    
    setupAutocomplete(newRow.querySelector('.sku-input'));
    newRow.querySelector('.sku-input').focus();
    
    rowCount++;
    updateRemoveButtons();
}

function removeRow(index) {
    const rows = document.querySelectorAll('.item-row');
    if (rows.length > 1) {
        const rowToRemove = document.querySelector(`[data-row="${index}"]`).closest('.item-row');
        rowToRemove.remove();
    }
    updateRemoveButtons();
}

function updateRemoveButtons() {
    const rows = document.querySelectorAll('.item-row');
    rows.forEach((row, index) => {
        const removeBtn = row.querySelector('.btn-remove');
        if (rows.length === 1) {
            removeBtn.style.visibility = 'hidden';
        } else {
            removeBtn.style.visibility = 'visible';
        }
    });
}

function collectItems() {
    const items = [];
    const rows = document.querySelectorAll('.item-row');
    
    rows.forEach(row => {
        const sku = row.querySelector('.sku-input').value.trim();
        const price = parseFloat(row.querySelector('.price-input').value);
        const quantity = parseInt(row.querySelector('.qty-input').value);
        
        if (sku && !isNaN(price) && !isNaN(quantity) && quantity > 0) {
            // Find the product to get case quantity
            const product = productsData.find(p => 
                p.sku.toLowerCase() === sku.toLowerCase() || 
                p.description.toLowerCase().includes(sku.toLowerCase())
            );
            
            items.push({
                sku: sku,
                price: price,
                quantity: quantity,
                case_qty: product ? product.case_qty : 1,
                description: product ? product.description : ''
            });
        }
    });
    
    return items;
}

function generateLabels() {
    const items = collectItems();
    
    if (items.length === 0) {
        alert('Please add at least one item with valid SKU, price, and quantity');
        return;
    }
    
    const format = document.getElementById('formatSelect').value;
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<div class="loading"></div> Generating...';
    btn.disabled = true;
    
    fetch('/labels/generate', {
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
                `Generated ${data.label_count} labels`;
            document.getElementById('downloadBtn').href = data.download_url;
            
            document.querySelector('.main-section').style.display = 'none';
            document.querySelector('.csv-upload-section').style.display = 'none';
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
    // Clear all rows except the first one
    const grid = document.getElementById('itemsGrid');
    const rows = grid.querySelectorAll('.item-row');
    for (let i = 1; i < rows.length; i++) {
        rows[i].remove();
    }
    
    // Clear the first row
    const firstRow = grid.querySelector('.item-row');
    firstRow.querySelector('.sku-input').value = '';
    firstRow.querySelector('.price-input').value = '';
    firstRow.querySelector('.qty-input').value = '1';
    
    // Hide result section and show main sections
    document.getElementById('resultSection').style.display = 'none';
    document.querySelector('.main-section').style.display = 'block';
    document.querySelector('.csv-upload-section').style.display = 'block';
    
    updateRemoveButtons();
}

// Initialize the first row with autocomplete
document.addEventListener('DOMContentLoaded', function() {
    const initialSkuInput = document.querySelector('.sku-input');
    if (initialSkuInput) {
        setupAutocomplete(initialSkuInput);
    }
});

function setupAutocomplete(input) {
    const container = input.closest('.autocomplete-container');
    const dropdown = container.querySelector('.autocomplete-dropdown');
    
    input.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }
        
        // Search both SKU and description
        const matches = productsData.filter(product => 
            product.sku.toLowerCase().includes(query) ||
            product.description.toLowerCase().includes(query)
        ).slice(0, 8);
        
        if (matches.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        dropdown.innerHTML = matches.map(product => 
            `<div class="autocomplete-item" data-sku="${product.sku}" data-price="${product.price}" data-case-qty="${product.case_qty}" data-description="${product.description}">
                <strong>${product.sku}</strong> - $${product.price.toFixed(2)}<br>
                <small style="color: #666;">${product.description} (Case: ${product.case_qty})</small>
            </div>`
        ).join('');
        
        dropdown.style.display = 'block';
    });
    
    dropdown.addEventListener('click', function(e) {
        const item = e.target.closest('.autocomplete-item');
        if (item) {
            const sku = item.dataset.sku;
            const price = item.dataset.price;
            const caseQty = item.dataset.caseQty;
            const description = item.dataset.description;
            
            input.value = sku;
            const row = input.closest('.item-row');
            row.querySelector('.price-input').value = price;
            
            dropdown.style.display = 'none';
            row.querySelector('.qty-input').focus();
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!container.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
    
    input.addEventListener('keydown', function(e) {
        const items = dropdown.querySelectorAll('.autocomplete-item');
        let selectedIndex = Array.from(items).findIndex(item => item.classList.contains('selected'));
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (selectedIndex < items.length - 1) {
                if (selectedIndex >= 0) items[selectedIndex].classList.remove('selected');
                items[selectedIndex + 1].classList.add('selected');
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (selectedIndex > 0) {
                items[selectedIndex].classList.remove('selected');
                items[selectedIndex - 1].classList.add('selected');
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0) {
                items[selectedIndex].click();
            }
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
}

// File upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadFile(this.files[0]);
        }
    });
});

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadArea = document.getElementById('uploadArea');
    const originalText = uploadArea.innerHTML;
    uploadArea.innerHTML = '<div class="loading"></div> Processing...';
    
    fetch('/labels/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            populateFromCSV(data.data);
            alert(`Loaded ${data.row_count} items from CSV`);
        } else {
            alert(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during upload');
    })
    .finally(() => {
        uploadArea.innerHTML = originalText;
        document.getElementById('fileInput').value = '';
    });
}

function populateFromCSV(data) {
    const grid = document.getElementById('itemsGrid');
    
    // Clear existing rows
    grid.innerHTML = '';
    rowCount = 0;
    
    // Add rows for each item
    data.forEach((item, index) => {
        const newRow = document.createElement('div');
        newRow.className = 'item-row';
        newRow.innerHTML = `
            <div class="autocomplete-container">
                <input type="text" placeholder="SKU or Description" class="form-control sku-input" data-row="${rowCount}" value="${item.sku || ''}">
                <div class="autocomplete-dropdown" style="display: none;"></div>
            </div>
            <input type="number" placeholder="Price" step="0.01" min="0" class="form-control price-input" data-row="${rowCount}" value="${item.price || ''}">
            <input type="number" placeholder="QTY" min="1" value="${item.quantity || 1}" class="form-control qty-input" data-row="${rowCount}">
            <button onclick="removeRow(${rowCount})" class="btn-remove">×</button>
        `;
        grid.appendChild(newRow);
        
        setupAutocomplete(newRow.querySelector('.sku-input'));
        rowCount++;
    });
    
    // Add one empty row at the end
    addRow();
    updateRemoveButtons();
}