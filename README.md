# Rule-Based Spellchecker Application
# Rule-Based Spellchecker Web App

This is a web application that allows users to check and correct spelling errors in text using customizable rule-based patterns. Users can input text directly or upload a file, select which spelling rules to apply, and view both the original and corrected text along with detailed error statistics.

## Features
- Rule-based spellchecking
- File upload and text input
- Error highlighting and correction
- Export corrected text

## Setup Instructions

1. **Install Python** (version 3.7 or higher) from [python.org](https://www.python.org/downloads/).

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies from `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the program:**
   ```bash
   python app.py
   ```

6. **To update spelling rules:**  
   Edit the `rules.json` file and restart the application if needed.

---

Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to use the application.