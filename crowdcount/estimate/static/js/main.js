document.addEventListener('DOMContentLoaded', function() {
    // File input handling
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'No file chosen';
            }
        });
    }
    
    // Form submission handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = this.querySelector('input[type="file"]');
            const submitBtn = this.querySelector('.submit-btn');
            const spinner = this.querySelector('.loading-spinner');
            
            if (fileInput.files.length > 0) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass"></i> Processing...';
                spinner.classList.add('active');
            }
        });
    }
    
    // Image preview (optional enhancement)
    const fileInputForPreview = document.getElementById('fileInput');
    if (fileInputForPreview) {
        fileInputForPreview.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file.type.match('image.*')) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                // Could implement image preview here if needed
            };
            reader.readAsDataURL(file);
        });
    }

    // Model selection active state
    const modelButtons = document.querySelectorAll('.btn-check');
    modelButtons.forEach(btn => {
        btn.addEventListener('change', function() {
            const label = document.querySelector(`label[for="${this.id}"]`);
            document.querySelectorAll('.btn-outline-primary').forEach(l => {
                l.classList.remove('active-model');
            });
            label.classList.add('active-model');
        });
    });
});

