document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('input-text');
    const checkBtn = document.getElementById('check-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const exportBtn = document.getElementById('export-btn');
    const ruleContainer = document.getElementById('rule-container');
    const originalTextDisplay = document.getElementById('original-text');
    const correctedTextDisplay = document.getElementById('corrected-text');
    const errorCount = document.getElementById('error-count');
    const errorTypes = document.getElementById('error-types');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const fileUpload = document.getElementById('file-upload');
    const filenm = document.getElementById('filenm');
    const fileError = document.getElementById('file-error');
    const modeTextBtn = document.getElementById('mode-text');
    const modeFileBtn = document.getElementById('mode-file');
    const textSection = document.getElementById('text-section');
    const fileSection = document.getElementById('file-section');

    modeTextBtn.addEventListener('click', () => {
        modeTextBtn.classList.add('selected');
        modeFileBtn.classList.remove('selected');
        textSection.style.display = '';
        fileSection.style.display = 'none';
    });
    modeFileBtn.addEventListener('click', () => {
        modeFileBtn.classList.add('selected');
        modeTextBtn.classList.remove('selected');
        textSection.style.display = 'none';
        fileSection.style.display = '';
    });
    
    let currentResults = null;
    let rules = [];
    let selectedRules = new Set();

    // Fetch available rules
    fetch('/get_rules')
        .then(response => response.json())
        .then(data => {
            rules = data;
            renderRules();
        });
    function renderRules() {
        ruleContainer.innerHTML = '';
        rules.forEach(rule => {
            const ruleElement = document.createElement('div');
            ruleElement.className = 'rule';
            ruleElement.textContent = rule.name;
            ruleElement.dataset.name = rule.name;

            if (selectedRules.has(rule.name)) {
                ruleElement.classList.add('selected');
            }

            ruleElement.onclick = () => {
                if (selectedRules.has(rule.name)) {
                    selectedRules.delete(rule.name);
                } else {
                    selectedRules.add(rule.name);
                }
                console.log('Selected Rules:', Array.from(selectedRules));
                renderRules();
            };

            ruleContainer.appendChild(ruleElement);
        });
    }

    // Button event handlers
    checkBtn.addEventListener('click', processText);
    uploadBtn.addEventListener('click', processFile);
    exportBtn.addEventListener('click', exportText);
    
    selectAllBtn.addEventListener('click', () => {
        selectedRules = new Set(rules.map(r => r.name));
        console.log('Select All:', Array.from(selectedRules));
        renderRules();
    });
    deselectAllBtn.addEventListener('click', () => {
        selectedRules = new Set();
        console.log('Deselect All:', Array.from(selectedRules));
        renderRules();
    });

    function selectAll(select) {
        selectedRules = select ? new Set(rules.map(r => r.name)) : new Set();
        renderRules();
    }

    function processText() {
        const text = inputText.value.trim();
        if (!text) return;
        
        fetch('/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: text, 
                rules: Array.from(selectedRules) 
            })
        })
        .then(response => response.json())
        .then(displayResults)
        .catch(console.error);
    }

    function processFile() {
        if (!fileUpload.files.length){
            fileError.textContent = "Please select a file to upload.";
            fileError.style.display = "inline";
            return;

        }else {
            fileError.style.display = "none";
        }    
        filenm.textContent = fileUpload.files[0].name;
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);
        Array.from(selectedRules).forEach(rule => {
            formData.append('rules', rule);
        });
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Update the input text area with file content
           // inputText.value = data.original_text;
            
            // Display results in the output panels
            displayResults({
                ...data,
                stats: {
                    total_errors: data.errors.length,
                    error_types: data.stats.error_types
                }
            });
        })
        .catch(console.error);        
    }

    function displayResults(data) {
        currentResults = data;
        
        // Update stats
        errorCount.textContent = data.stats.total_errors;
        
        // Display error types
        if (Object.keys(data.stats.error_types).length > 0) {
            errorTypes.innerHTML = '<h4>Error Types:</h4>';
            for (const [type, count] of Object.entries(data.stats.error_types)) {
                errorTypes.innerHTML += `<p>${type}: ${count}</p>`;
            }
        } else {
            errorTypes.innerHTML = '';
        }
        
        // Highlight errors in original text
        let originalHTML = data.original_text;
        data.errors.forEach(error => {
            const escapedWord = escapeHTML(error.word);
            originalHTML = originalHTML.replace(
                new RegExp(escapeRegExp(error.word), 'g'),
                `<span class="error-highlight" data-correction="${error.correction}">${escapedWord}</span>`
            );
        });
        originalTextDisplay.innerHTML = originalHTML;
        
        // Display corrected text
        correctedTextDisplay.textContent = data.corrected_text;
    }

    function exportText() {
        if (!currentResults) return;
        
        const blob = new Blob([currentResults.corrected_text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'corrected_text.txt';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }

    // Helper functions
    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function escapeRegExp(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
});