document.addEventListener('DOMContentLoaded', () => {
    // Theme toggling
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    const themeIcon = themeToggle.querySelector('i');

    themeToggle.addEventListener('click', () => {
        if (htmlElement.getAttribute('data-theme') === 'dark') {
            htmlElement.setAttribute('data-theme', 'light');
            themeIcon.classList.remove('ph-sun');
            themeIcon.classList.add('ph-moon');
        } else {
            htmlElement.setAttribute('data-theme', 'dark');
            themeIcon.classList.remove('ph-moon');
            themeIcon.classList.add('ph-sun');
        }
    });

    // File Upload Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const selectedFileName = document.getElementById('selectedFileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadLoader = document.getElementById('uploadLoader');
    let currentFile = null;

    // Drag & Drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (file.type !== 'application/pdf') {
            showStatus('Please select a PDF file.', 'error');
            currentFile = null;
            selectedFileName.textContent = '';
            uploadBtn.classList.add('disabled');
            uploadBtn.disabled = true;
            return;
        }
        currentFile = file;
        selectedFileName.textContent = file.name;
        uploadBtn.classList.remove('disabled');
        uploadBtn.disabled = false;
        uploadStatus.textContent = '';
    }

    uploadBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('file', currentFile);

        uploadBtn.disabled = true;
        uploadBtn.classList.add('disabled');
        uploadLoader.classList.remove('hidden');
        uploadStatus.textContent = '';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                showStatus(`Success! Created ${data.chunks_created} chunks.`, 'success');
            } else {
                showStatus(data.error || 'Upload failed.', 'error');
            }
        } catch (error) {
            showStatus('Network error occurred.', 'error');
        } finally {
            uploadLoader.classList.add('hidden');
            uploadBtn.disabled = false;
            uploadBtn.classList.remove('disabled');
        }
    });

    function showStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = `status-message status-${type}`;
    }

    // QA Elements
    const questionInput = document.getElementById('questionInput');
    const askBtn = document.getElementById('askBtn');
    const askLoader = document.getElementById('askLoader');
    const resultContainer = document.getElementById('resultContainer');
    const verificationBadge = document.getElementById('verificationBadge');
    const answerContent = document.getElementById('answerContent');
    const sourcesList = document.getElementById('sourcesList');

    const steps = ['retrieve', 'research', 'analyze', 'review'];

    function simulateAgentProgress() {
        let currentStep = 0;
        
        // Reset all steps
        steps.forEach(step => {
            const el = document.getElementById(`step-${step}`);
            el.className = 'agent-step';
        });

        const interval = setInterval(() => {
            if (currentStep > 0) {
                document.getElementById(`step-${steps[currentStep - 1]}`).className = 'agent-step done';
            }
            if (currentStep < steps.length) {
                document.getElementById(`step-${steps[currentStep]}`).className = 'agent-step active';
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 3000); // Fake interval for visual feedback, real wait happens in fetch

        return interval;
    }

    askBtn.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        askBtn.disabled = true;
        askLoader.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        
        const progressInterval = simulateAgentProgress();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            
            const data = await response.json();
            clearInterval(progressInterval);

            // Mark all steps done
            steps.forEach(step => {
                document.getElementById(`step-${step}`).className = 'agent-step done';
            });

            setTimeout(() => {
                askLoader.classList.add('hidden');
                displayResult(data);
            }, 500);

        } catch (error) {
            clearInterval(progressInterval);
            askLoader.classList.add('hidden');
            alert('Error asking question. Is backend running?');
        } finally {
            askBtn.disabled = false;
        }
    });

    function displayResult(data) {
        if (data.error) {
            answerContent.innerHTML = `<span style="color: var(--danger)">Error: ${data.error}</span>`;
            sourcesList.innerHTML = '';
            verificationBadge.style.display = 'none';
        } else {
            answerContent.textContent = data.final_answer;
            
            // Set verification badge
            const badgeIcon = verificationBadge.querySelector('i');
            const badgeText = verificationBadge.querySelector('span');
            
            verificationBadge.style.display = 'flex';
            if (data.verification_status.toUpperCase() === 'PASS') {
                verificationBadge.className = 'verification-badge badge-pass';
                badgeIcon.className = 'ph ph-seal-check';
                badgeText.textContent = 'Verification: PASS';
            } else {
                verificationBadge.className = 'verification-badge badge-revision';
                badgeIcon.className = 'ph ph-warning-circle';
                badgeText.textContent = 'Verification: NEEDS REVISION';
            }

            // Set sources
            sourcesList.innerHTML = '';
            if (data.sources && data.sources.length > 0) {
                data.sources.forEach(source => {
                    const li = document.createElement('li');
                    li.textContent = source;
                    sourcesList.appendChild(li);
                });
            } else {
                sourcesList.innerHTML = '<li>No specific sources cited from uploaded documents.</li>';
            }
        }
        
        resultContainer.classList.remove('hidden');
    }

    // Clear Button Handler
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            questionInput.value = '';
            resultContainer.classList.add('hidden');
            answerContent.innerHTML = '';
            sourcesList.innerHTML = '';
            
            steps.forEach(step => {
                const el = document.getElementById(`step-${step}`);
                if (el) el.className = 'agent-step';
            });
        });
    }
});
