// Main JavaScript file for Equipment Maintenance Logger

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive elements
    initializeSearch();
    initializeImagePreview();
    initializeFormValidation();
    initializeTooltips();
    
    // Add fade-in animation to main content
    document.querySelector('main').classList.add('fade-in');
});

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    
    searchInputs.forEach(input => {
        // Add search icon animation
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('search-focus');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('search-focus');
        });
        
        // Allow Enter key to submit search
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
    });
}

// Image preview functionality
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, input);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function showImagePreview(src, input) {
    // Remove existing preview
    const existingPreview = input.parentElement.querySelector('.image-preview');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    // Create new preview
    const previewContainer = document.createElement('div');
    previewContainer.className = 'image-preview mt-3';
    previewContainer.innerHTML = `
        <div class="d-flex align-items-center">
            <img src="${src}" alt="Preview" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;">
            <div class="ms-3">
                <small class="text-muted">Preview</small>
                <br>
                <button type="button" class="btn btn-sm btn-outline-danger remove-preview">
                    <i data-feather="x"></i> Remove
                </button>
            </div>
        </div>
    `;
    
    // Add remove functionality
    previewContainer.querySelector('.remove-preview').addEventListener('click', function() {
        input.value = '';
        previewContainer.remove();
    });
    
    // Insert preview after the input
    input.parentElement.appendChild(previewContainer);
    
    // Re-initialize feather icons
    feather.replace();
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state to submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
                
                // Re-enable button after a delay (in case form submission fails)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateInput(this);
                }
            });
        });
    });
}

function validateInput(input) {
    const isValid = input.checkValidity();
    
    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Equipment card interactions
function initializeEquipmentCards() {
    const equipmentCards = document.querySelectorAll('.equipment-card, .equipment-select-card');
    
    equipmentCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Category management
function deleteCategory(categoryId, categoryName) {
    if (confirm(`Are you sure you want to delete the category "${categoryName}"?`)) {
        window.location.href = `/delete_category/${categoryId}`;
    }
}

// Search with suggestions (if needed in future)
function initializeSearchSuggestions() {
    const searchInputs = document.querySelectorAll('.search-with-suggestions');
    
    searchInputs.forEach(input => {
        let suggestionTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(suggestionTimeout);
            const query = this.value;
            
            if (query.length > 1) {
                suggestionTimeout = setTimeout(() => {
                    fetchSearchSuggestions(query, this);
                }, 300);
            } else {
                hideSuggestions(this);
            }
        });
    });
}

function fetchSearchSuggestions(query, input) {
    fetch(`/api/equipment/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showSuggestions(data, input);
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
        });
}

function showSuggestions(suggestions, input) {
    hideSuggestions(input);
    
    if (suggestions.length === 0) return;
    
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    suggestionsContainer.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    `;
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.style.cssText = `
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        `;
        item.innerHTML = `
            <strong>${suggestion.name}</strong>
            <small class="text-muted d-block">${suggestion.category}</small>
        `;
        
        item.addEventListener('click', function() {
            input.value = suggestion.name;
            hideSuggestions(input);
            input.closest('form').submit();
        });
        
        suggestionsContainer.appendChild(item);
    });
    
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(suggestionsContainer);
}

function hideSuggestions(input) {
    const suggestions = input.parentElement.querySelector('.search-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
}

// Close suggestions when clicking outside
document.addEventListener('click', function(e) {
    const suggestions = document.querySelectorAll('.search-suggestions');
    suggestions.forEach(suggestion => {
        if (!suggestion.contains(e.target) && !e.target.classList.contains('search-with-suggestions')) {
            suggestion.remove();
        }
    });
});

// Initialize equipment cards when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEquipmentCards();
});
