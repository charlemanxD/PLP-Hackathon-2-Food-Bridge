/**
 * Dashboard JavaScript functionality
 * Handles section switching, form validation, and modal interactions
 */

// Section switching functionality
function showSection(section) {
    const createSection = document.getElementById('createSection');
    const currentSection = document.getElementById('currentSection');
    const createBtn = document.getElementById('createListingBtn');
    const currentBtn = document.getElementById('currentListingsBtn');
    
    if (section === 'create') {
        // Show create section
        createSection.style.display = 'block';
        currentSection.style.display = 'none';
        
        // Update button states
        createBtn.classList.add('active');
        currentBtn.classList.remove('active');
        
        // Focus on first form field
        setTimeout(() => {
            document.getElementById('itemName').focus();
        }, 100);
        
    } else if (section === 'current') {
        // Show current listings section
        createSection.style.display = 'none';
        currentSection.style.display = 'block';
        
        // Update button states
        createBtn.classList.remove('active');
        currentBtn.classList.add('active');
    }
}

// Form validation for creating listings
document.addEventListener('DOMContentLoaded', function() {
    const createForm = document.getElementById('createListingForm');
    
    if (createForm) {
        createForm.addEventListener('submit', function(e) {
            const itemName = document.getElementById('itemName').value.trim();
            const quantity = document.getElementById('quantity').value.trim();
            const contact = document.getElementById('contact').value.trim();
            
            // Basic validation
            if (!itemName || !quantity || !contact) {
                e.preventDefault();
                showAlert('Please fill in all required fields.', 'error');
                return false;
            }
            
            // Disable submit button to prevent double submission
            const submitBtn = createForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating...';
        });
    }
});

// Edit listing functionality
function editListing(listingId, itemName, quantity, contact, isAvailable, price, currency) {
    // Populate the edit form
    document.getElementById('editItemName').value = itemName;
    document.getElementById('editQuantity').value = quantity;
    document.getElementById('editContact').value = contact;
    document.getElementById('editIsAvailable').checked = isAvailable;
    
    // Handle price and currency
    if (price !== undefined && price !== null && price !== '') {
        document.getElementById('editPrice').value = price;
    } else {
        document.getElementById('editPrice').value = '';
    }
    
    if (currency !== undefined && currency !== null && currency !== '') {
        document.getElementById('editCurrency').value = currency;
    } else {
        document.getElementById('editCurrency').value = 'USD';
    }
    
    // Set the form action URL
    const editForm = document.getElementById('editListingForm');
    editForm.action = `/update_listing/${listingId}`;
    
    // Show the modal
    const editModal = new bootstrap.Modal(document.getElementById('editListingModal'));
    editModal.show();
}

// Delete listing functionality
function deleteListing(listingId, itemName) {
    // Set the item name in the confirmation modal
    document.getElementById('deleteItemName').textContent = itemName;
    
    // Set the form action URL
    const deleteForm = document.getElementById('deleteListingForm');
    deleteForm.action = `/delete_listing/${listingId}`;
    
    // Show the confirmation modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    deleteModal.show();
}

// Show alert messages
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    const firstChild = container.firstElementChild;
    container.insertBefore(alertDiv, firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Handle edit form submission
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('editListingForm');
    
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const submitBtn = editForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        });
    }
});

// Handle delete form submission
document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.getElementById('deleteListingForm');
    
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            const submitBtn = deleteForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Deleting...';
        });
    }
});

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // ESC key closes modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
    
    // Ctrl+N or Cmd+N for new listing (if not in input field)
    if ((e.ctrlKey || e.metaKey) && e.key === 'n' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        showSection('create');
    }
    
    // Ctrl+L or Cmd+L for listings view (if not in input field)
    if ((e.ctrlKey || e.metaKey) && e.key === 'l' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        showSection('current');
    }
});

// Auto-save form data to localStorage (for create form)
document.addEventListener('DOMContentLoaded', function() {
    const createForm = document.getElementById('createListingForm');
    
    if (createForm) {
        const formFields = createForm.querySelectorAll('input[type="text"], input[type="email"], textarea');
        
        // Load saved data
        formFields.forEach(field => {
            const savedValue = localStorage.getItem(`foodbridge_${field.name}`);
            if (savedValue && !field.value) {
                field.value = savedValue;
            }
        });
        
        // Save data on input
        formFields.forEach(field => {
            field.addEventListener('input', function() {
                localStorage.setItem(`foodbridge_${field.name}`, field.value);
            });
        });
        
        // Clear saved data on successful submission
        createForm.addEventListener('submit', function() {
            setTimeout(() => {
                formFields.forEach(field => {
                    localStorage.removeItem(`foodbridge_${field.name}`);
                });
            }, 1000);
        });
    }
});

// Responsive behavior for mobile devices
function handleMobileLayout() {
    const isMobile = window.innerWidth < 768;
    const btnGroup = document.querySelector('.btn-group');
    
    if (btnGroup) {
        if (isMobile) {
            btnGroup.classList.remove('w-100');
            btnGroup.classList.add('d-grid', 'gap-2');
        } else {
            btnGroup.classList.add('w-100');
            btnGroup.classList.remove('d-grid', 'gap-2');
        }
    }
}

// Handle window resize
window.addEventListener('resize', handleMobileLayout);
document.addEventListener('DOMContentLoaded', handleMobileLayout);

// Form field character counters (optional enhancement)
function addCharacterCounter(fieldId, maxLength) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    const counter = document.createElement('div');
    counter.className = 'form-text text-muted mt-1';
    counter.innerHTML = `<small>0/${maxLength} characters</small>`;
    
    field.parentNode.appendChild(counter);
    
    field.addEventListener('input', function() {
        const currentLength = field.value.length;
        counter.innerHTML = `<small>${currentLength}/${maxLength} characters</small>`;
        
        if (currentLength > maxLength * 0.9) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.remove('text-warning');
        }
        
        if (currentLength >= maxLength) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-warning');
        } else {
            counter.classList.remove('text-danger');
        }
    });
}

// Initialize character counters
document.addEventListener('DOMContentLoaded', function() {
    addCharacterCounter('itemName', 100);
    addCharacterCounter('quantity', 50);
    addCharacterCounter('contact', 200);
});

// Success message handling
function handleSuccessMessage() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'created') {
        showAlert('Listing created successfully!', 'success');
        // Clear the form
        const createForm = document.getElementById('createListingForm');
        if (createForm) {
            createForm.reset();
        }
    }
}

// Initialize success message handling
document.addEventListener('DOMContentLoaded', handleSuccessMessage);

console.log('Food Bridge Dashboard JS loaded successfully');
