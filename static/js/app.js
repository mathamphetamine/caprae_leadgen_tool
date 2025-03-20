/**
 * LeadGen Tool - Application JavaScript
 * 
 * This file contains additional functionality to enhance the user experience
 * beyond what's provided in the inline scripts.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Add form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Enhanced table functionality
    function setupAdvancedTableFeatures() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            if (table.classList.contains('advanced-table-initialized')) {
                return;
            }

            // Add sorting functionality
            const headers = table.querySelectorAll('thead th');
            headers.forEach(header => {
                if (header.classList.contains('no-sort')) {
                    return;
                }

                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    const index = Array.from(header.parentNode.children).indexOf(header);
                    sortTable(table, index);
                });

                // Add sort indicator
                const indicator = document.createElement('span');
                indicator.classList.add('sort-indicator', 'ms-1');
                indicator.innerHTML = '⇵';
                header.appendChild(indicator);
            });

            // Mark as initialized
            table.classList.add('advanced-table-initialized');
        });
    }

    // Table sorting function
    function sortTable(table, column) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const headers = table.querySelectorAll('thead th');
        const header = headers[column];
        
        // Determine sort direction
        const currentDirection = header.getAttribute('data-sort') || 'asc';
        const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
        
        // Update sort indicators on all headers
        headers.forEach(h => {
            h.setAttribute('data-sort', '');
            h.querySelector('.sort-indicator').innerHTML = '⇵';
        });
        
        // Set direction on current header
        header.setAttribute('data-sort', newDirection);
        header.querySelector('.sort-indicator').innerHTML = newDirection === 'asc' ? '↑' : '↓';
        
        // Sort the rows
        rows.sort((a, b) => {
            const cellA = a.querySelector(`td:nth-child(${column + 1})`).textContent;
            const cellB = b.querySelector(`td:nth-child(${column + 1})`).textContent;
            
            // Check if values are numbers
            const numA = parseFloat(cellA);
            const numB = parseFloat(cellB);
            
            if (!isNaN(numA) && !isNaN(numB)) {
                return newDirection === 'asc' ? numA - numB : numB - numA;
            }
            
            // Otherwise sort as strings
            return newDirection === 'asc' 
                ? cellA.localeCompare(cellB) 
                : cellB.localeCompare(cellA);
        });
        
        // Reattach rows in new order
        rows.forEach(row => tbody.appendChild(row));
    }

    // Watch for dynamic content changes to apply advanced features
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setupAdvancedTableFeatures();
            }
        });
    });

    // Start observing for changes in the main container
    observer.observe(document.getElementById('main-container'), {
        childList: true,
        subtree: true
    });

    // Add CSV/Excel export format toggle
    const exportFormatRadios = document.querySelectorAll('input[name="export-format"]');
    if (exportFormatRadios.length) {
        exportFormatRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                localStorage.setItem('preferred-export-format', this.value);
            });
        });

        // Set from saved preference if available
        const savedFormat = localStorage.getItem('preferred-export-format');
        if (savedFormat) {
            document.querySelector(`input[name="export-format"][value="${savedFormat}"]`).checked = true;
        }
    }

    // Save form input values to localStorage
    const formInputs = document.querySelectorAll('input[type="text"], input[type="url"], input[type="number"], textarea');
    formInputs.forEach(input => {
        // Load saved value if exists
        const savedValue = localStorage.getItem(`form-${input.id}`);
        if (savedValue) {
            input.value = savedValue;
        }

        // Save on change
        input.addEventListener('change', function() {
            localStorage.setItem(`form-${this.id}`, this.value);
        });
    });

    // Clear form button functionality
    const clearButtons = document.querySelectorAll('.btn-clear-form');
    clearButtons.forEach(button => {
        button.addEventListener('click', function() {
            const formId = this.getAttribute('data-form-id');
            const form = document.getElementById(formId);
            
            if (form) {
                form.reset();
                
                // Also clear from localStorage
                form.querySelectorAll('input, textarea').forEach(input => {
                    localStorage.removeItem(`form-${input.id}`);
                });
            }
        });
    });

    // Initialize on page load
    setupAdvancedTableFeatures();
}); 