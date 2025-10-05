// APK Protection Service - Frontend Logic

class APKProtectionApp {
    constructor() {
        this.selectedFile = null;
        this.initElements();
        this.attachEventListeners();
    }

    initElements() {
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.selectBtn = document.getElementById('selectBtn');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.removeBtn = document.getElementById('removeBtn');

        // Options elements
        this.optionsSection = document.getElementById('optionsSection');
        this.optRemovePermissions = document.getElementById('optRemovePermissions');
        this.optUpdateSdk = document.getElementById('optUpdateSdk');
        this.optObfuscateCode = document.getElementById('optObfuscateCode');
        this.optObfuscateManifest = document.getElementById('optObfuscateManifest');
        this.processBtn = document.getElementById('processBtn');

        // Progress elements
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressStatus = document.getElementById('progressStatus');

        // Result elements
        this.resultSection = document.getElementById('resultSection');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newFileBtn = document.getElementById('newFileBtn');

        // Error elements
        this.errorSection = document.getElementById('errorSection');
        this.errorMessage = document.getElementById('errorMessage');
        this.retryBtn = document.getElementById('retryBtn');
    }

    attachEventListeners() {
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.selectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Remove file button
        this.removeBtn.addEventListener('click', () => this.removeFile());

        // Process button
        this.processBtn.addEventListener('click', () => this.processAPK());

        // New file button
        this.newFileBtn.addEventListener('click', () => this.reset());

        // Retry button
        this.retryBtn.addEventListener('click', () => this.reset());
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFile(file) {
        // Validate file type
        if (!file.name.endsWith('.apk')) {
            this.showError('Пожалуйста, выберите файл с расширением .apk');
            return;
        }

        // Validate file size (150 MB max)
        const maxSize = 150 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('Файл слишком большой. Максимальный размер: 150 МБ');
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
    }

    displayFileInfo(file) {
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);

        this.uploadArea.style.display = 'none';
        this.fileInfo.style.display = 'flex';
        this.optionsSection.style.display = 'block';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    removeFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.uploadArea.style.display = 'block';
        this.fileInfo.style.display = 'none';
        this.optionsSection.style.display = 'none';
    }

    async processAPK() {
        if (!this.selectedFile) {
            this.showError('Файл не выбран');
            return;
        }

        // Hide options and show progress
        this.optionsSection.style.display = 'none';
        this.progressSection.style.display = 'block';

        // Prepare form data
        const formData = new FormData();
        formData.append('file', this.selectedFile);

        // Prepare options
        const options = {
            remove_sensitive_permissions: this.optRemovePermissions.checked,
            update_target_sdk: this.optUpdateSdk.checked,
            obfuscate_code: this.optObfuscateCode.checked,
            obfuscate_manifest: this.optObfuscateManifest.checked
        };
        formData.append('options', JSON.stringify(options));

        try {
            // Start progress animation
            this.animateProgress();

            // Send request
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка обработки APK');
            }

            // Get the file blob
            const blob = await response.blob();
            
            // Create download URL
            this.downloadUrl = window.URL.createObjectURL(blob);
            
            // Show success
            this.showSuccess();

        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message || 'Произошла ошибка при обработке APK');
        }
    }

    animateProgress() {
        const steps = [
            { id: 'step1', label: 'Анализ APK', duration: 2000 },
            { id: 'step2', label: 'Декомпиляция', duration: 5000 },
            { id: 'step3', label: 'Модификация манифеста', duration: 3000 },
            { id: 'step4', label: 'Обфускация кода', duration: 8000 },
            { id: 'step5', label: 'Пересборка APK', duration: 6000 },
            { id: 'step6', label: 'Подпись APK', duration: 3000 }
        ];

        let currentStep = 0;
        let totalDuration = steps.reduce((sum, step) => sum + step.duration, 0);
        let elapsed = 0;

        const interval = setInterval(() => {
            elapsed += 100;
            const progress = Math.min((elapsed / totalDuration) * 100, 100);
            this.progressFill.style.width = progress + '%';

            // Update current step
            let stepElapsed = 0;
            for (let i = 0; i < steps.length; i++) {
                stepElapsed += steps[i].duration;
                if (elapsed < stepElapsed) {
                    if (currentStep !== i) {
                        currentStep = i;
                        this.updateStep(steps[i].id, 'active');
                        this.progressStatus.textContent = steps[i].label;
                        
                        // Mark previous steps as completed
                        for (let j = 0; j < i; j++) {
                            this.updateStep(steps[j].id, 'completed');
                        }
                    }
                    break;
                }
            }
        }, 100);

        // Store interval ID to clear it later if needed
        this.progressInterval = interval;
    }

    updateStep(stepId, status) {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('active', 'completed');
            step.classList.add(status);
        }
    }

    showSuccess() {
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        // Complete all steps
        for (let i = 1; i <= 6; i++) {
            this.updateStep(`step${i}`, 'completed');
        }
        this.progressFill.style.width = '100%';

        // Wait a bit then show result
        setTimeout(() => {
            this.progressSection.style.display = 'none';
            this.resultSection.style.display = 'block';

            // Attach download handler
            this.downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = this.downloadUrl;
                a.download = `protected_${this.selectedFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };
        }, 1000);
    }

    showError(message) {
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        this.progressSection.style.display = 'none';
        this.optionsSection.style.display = 'none';
        this.errorSection.style.display = 'block';
        this.errorMessage.textContent = message;
    }

    reset() {
        // Hide all sections
        this.progressSection.style.display = 'none';
        this.resultSection.style.display = 'none';
        this.errorSection.style.display = 'none';

        // Reset file
        this.removeFile();

        // Reset progress
        this.progressFill.style.width = '0%';
        for (let i = 1; i <= 6; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.classList.remove('active', 'completed');
            }
        }

        // Clear download URL
        if (this.downloadUrl) {
            window.URL.revokeObjectURL(this.downloadUrl);
            this.downloadUrl = null;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new APKProtectionApp();
});
