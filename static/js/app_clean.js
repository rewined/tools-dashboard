let rowCount = 1;
let productsData = [];

// Load products data on page load
fetch('/products')
    .then(response => response.json())
    .then(data => {
        productsData = data;
    })
    .catch(error => console.log('No products data found'));

function addRow() {
    const grid = document.getElementById('itemsGrid');
    const newRow = document.createElement('div');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <div class="autocomplete-container">
            <input type="text" placeholder="SKU" class="form-control sku-input" data-row="${rowCount}">
            <div class="autocomplete-dropdown" style="display: none;"></div>
        </div>
        <input type="number" placeholder="Price" step="0.01" min="0" class="form-control price-input" data-row="${rowCount}">
        <input type="number" placeholder="QTY" min="1" value="1" class="form-control qty-input" data-row="${rowCount}">
        <button onclick="removeRow(${rowCount})" class="btn-remove">×</button>
    `;
    grid.appendChild(newRow);
    
    // Setup autocomplete for the new SKU input
    setupAutocomplete(newRow.querySelector('.sku-input'));
    
    // Focus on the SKU input of the new row
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
            items.push({ sku, price, quantity });
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
    // Clear all rows except first
    const grid = document.getElementById('itemsGrid');
    grid.innerHTML = `
        <div class="item-row">
            <input type="text" placeholder="SKU" class="form-control sku-input" data-row="0">
            <input type="number" placeholder="Price" step="0.01" min="0" class="form-control price-input" data-row="0">
            <input type="number" placeholder="QTY" min="1" value="1" class="form-control qty-input" data-row="0">
            <button onclick="removeRow(0)" class="btn-remove" style="visibility: hidden;">×</button>
        </div>
    `;
    
    rowCount = 1;
    document.querySelector('.main-section').style.display = 'block';
    document.querySelector('.csv-upload-section').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
}

// CSV Upload handling
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
    
    uploadArea.innerHTML = '<div class="loading"></div> Processing...';
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addCsvDataToRows(data.data);
        } else {
            alert(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during upload');
    })
    .finally(() => {
        uploadArea.innerHTML = '<span class="upload-text">Drop CSV here or click to upload</span>';
    });
}

function addCsvDataToRows(csvData) {
    const grid = document.getElementById('itemsGrid');
    
    // Clear existing rows
    grid.innerHTML = '';
    rowCount = 0;
    
    // Add rows for each CSV item
    csvData.forEach((item, index) => {
        const newRow = document.createElement('div');
        newRow.className = 'item-row';
        newRow.innerHTML = `
            <input type="text" placeholder="SKU" class="form-control sku-input" data-row="${index}" value="${item.sku || ''}">
            <input type="number" placeholder="Price" step="0.01" min="0" class="form-control price-input" data-row="${index}" value="${item.price || ''}">
            <input type="number" placeholder="QTY" min="1" class="form-control qty-input" data-row="${index}" value="${item.quantity || 1}">
            <button onclick="removeRow(${index})" class="btn-remove">×</button>
        `;
        grid.appendChild(newRow);
        rowCount++;
    });
    
    updateRemoveButtons();
}

function setupAutocomplete(input) {
    const container = input.closest('.autocomplete-container');
    const dropdown = container.querySelector('.autocomplete-dropdown');
    
    input.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }
        
        // Filter products by SKU
        const matches = productsData.filter(product => 
            product.sku.toLowerCase().includes(query)
        ).slice(0, 8); // Limit to 8 results
        
        if (matches.length === 0) {
            dropdown.style.display = 'none';
            return;
        }
        
        // Build dropdown HTML
        dropdown.innerHTML = matches.map(product => 
            `<div class="autocomplete-item" data-sku="${product.sku}" data-price="${product.price}">
                <strong>${product.sku}</strong> - $${product.price.toFixed(2)}
            </div>`
        ).join('');
        
        dropdown.style.display = 'block';
    });
    
    // Handle dropdown clicks
    dropdown.addEventListener('click', function(e) {
        const item = e.target.closest('.autocomplete-item');
        if (item) {
            const sku = item.dataset.sku;
            const price = item.dataset.price;
            
            // Fill in the SKU and price
            input.value = sku;
            const row = input.closest('.item-row');
            row.querySelector('.price-input').value = price;
            
            dropdown.style.display = 'none';
            
            // Move to quantity field
            row.querySelector('.qty-input').focus();
        }
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!container.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// Setup autocomplete for initial row
document.addEventListener('DOMContentLoaded', function() {
    const initialSkuInput = document.querySelector('.sku-input');
    if (initialSkuInput) {
        // Wrap initial input in autocomplete container
        const container = document.createElement('div');
        container.className = 'autocomplete-container';
        const dropdown = document.createElement('div');
        dropdown.className = 'autocomplete-dropdown';
        dropdown.style.display = 'none';
        
        initialSkuInput.parentNode.insertBefore(container, initialSkuInput);
        container.appendChild(initialSkuInput);
        container.appendChild(dropdown);
        
        setupAutocomplete(initialSkuInput);
    }
});

// Enter key handling
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.matches('.form-control')) {
        // Hide any open dropdowns
        document.querySelectorAll('.autocomplete-dropdown').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
        
        const currentRow = e.target.closest('.item-row');
        const inputs = currentRow.querySelectorAll('.form-control');
        const currentIndex = Array.from(inputs).indexOf(e.target);
        
        if (currentIndex < inputs.length - 1) {
            // Move to next input in same row
            inputs[currentIndex + 1].focus();
        } else {
            // Last input in row, add new row
            addRow();
        }
    }
    
    // Handle arrow keys in dropdown
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const activeDropdown = document.querySelector('.autocomplete-dropdown[style*="block"]');
        if (activeDropdown) {
            e.preventDefault();
            const items = activeDropdown.querySelectorAll('.autocomplete-item');
            let selected = activeDropdown.querySelector('.autocomplete-item.selected');
            
            if (selected) {
                selected.classList.remove('selected');
                if (e.key === 'ArrowDown') {
                    selected = selected.nextElementSibling || items[0];
                } else {
                    selected = selected.previousElementSibling || items[items.length - 1];
                }
            } else {
                selected = e.key === 'ArrowDown' ? items[0] : items[items.length - 1];
            }
            
            if (selected) {
                selected.classList.add('selected');
            }
        }
    }
});