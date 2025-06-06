from flask import Flask, render_template, request, jsonify
import json
import re
import os

app = Flask(__name__)

# Load spelling rules from JSON file
def load_rules():
    with open('rules.json', 'r') as f:
        return json.load(f)['rules']

rules = load_rules()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_rules')
def get_rules():
    return jsonify([{"name": r["name"]} for r in rules])

def apply_rules(text, selected_rules):
    errors = []
    applied_rules = [r for r in rules if r["name"] in selected_rules]
    
    # Create corrected text and identify errors
    corrected_text = text
    for rule in applied_rules:
        pattern = re.compile(re.escape(rule['pattern']))
        for match in pattern.finditer(text):
            errors.append({
                "word": match.group(),
                "correction": rule['correction'],
                "start": match.start(),
                "end": match.end(),
                "rule": rule['name']
            })
            corrected_text = corrected_text.replace(match.group(), rule['correction'], 1)
    
    return corrected_text, errors

@app.route('/check', methods=['POST'])
def check_spelling():
    data = request.json
    text = data.get('text', '')
    selected_rules = data.get('rules', [])
    
    corrected_text, errors = apply_rules(text, selected_rules)
    
    return jsonify({
        "original_text": text,
        "corrected_text": corrected_text,
        "errors": errors,
        "stats": {
            "total_errors": len(errors),
            "error_types": {e["rule"]: sum(1 for err in errors if err["rule"] == e["rule"]) for e in errors}
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        text = file.read().decode('utf-8')
        selected_rules = request.form.getlist('rules')
        corrected_text, errors = apply_rules(text, selected_rules)
        
        # Build error types statistics
        error_types = {}
        for error in errors:
            rule = error["rule"]
            error_types[rule] = error_types.get(rule, 0) + 1
        
        return jsonify({
            "original_text": text,
            "corrected_text": corrected_text,
            "errors": errors,
            "stats": {
                "total_errors": len(errors),
                "error_types": error_types
            },
            "filename": file.filename
        })

if __name__ == '__main__':
    app.run(debug=True)