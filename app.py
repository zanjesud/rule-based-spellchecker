from flask import Flask, render_template, request, jsonify
import json
import re
import os
import difflib

from spellchecker import SpellChecker

app = Flask(__name__)

# Load spelling rules from JSON file
def load_rules():
    with open('rules.json', 'r') as f:
        return json.load(f)['rules']

rules = load_rules()

spell_checker = SpellChecker(dictionary_file='big.txt')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_rules')
def get_rules():
    return jsonify([{"name": r["name"]} for r in rules])

def most_similar(word, candidates):
    # Use difflib to get the most similar word from candidates
    if not candidates:
        return word
    return max(candidates, key=lambda c: difflib.SequenceMatcher(None, word, c).ratio())

# def apply_rules(text, selected_rules):
#     errors = []
#     applied_rules = [r for r in rules if r["name"] in selected_rules]
    
#     # Create corrected text and identify errors
#     corrected_text = text
#     for rule in applied_rules:
#         pattern = re.compile(re.escape(rule['pattern']))
#         for match in pattern.finditer(text):
#             errors.append({
#                 "word": match.group(),
#                 "correction": rule['correction'],
#                 "start": match.start(),
#                 "end": match.end(),
#                 "rule": rule['name']
#             })
#             corrected_text = corrected_text.replace(match.group(), rule['correction'], 1)
    
#     return corrected_text, errors

def apply_rules(text, selected_rules):
    errors = []
    applied_rules = [r for r in rules if r["name"] in selected_rules]
    corrected_text = text
    matched_words = set()  # Track words already matched and replaced

    for rule in applied_rules:
        pattern = re.compile(rule['pattern'])
        corrections = rule.get('corrections', [])
        matches = list(pattern.finditer(corrected_text))
        for match in matches:
            matched_word = match.group()
            # Only replace if the whole word matches (not just a substring)
            if matched_word in matched_words:
                continue
            # Check if the match is a whole word in the text
            if re.fullmatch(r'\b\w+\b', matched_word):
                best_correction = most_similar(matched_word, corrections)
                errors.append({
                    "word": matched_word,
                    "corrections": corrections,  # List of suggestions
                    "suggested": best_correction,
                    "start": match.start(),
                    "end": match.end(),
                    "rule": rule['name']
                })
                if best_correction:
                    corrected_text = (
                        corrected_text[:match.start()] +
                        best_correction +
                        corrected_text[match.end():]
                    )
                    matched_words.add(matched_word)

    return corrected_text, errors

def spellcheck_text(text):
    tokens = list(re.finditer(r'\b\w+\b', text))
    errors = []
    corrections = []
    
    for match in tokens:
        word = match.group()
        if not spell_checker.is_valid_word(word):
            candidates = spell_checker.get_candidates(word)
            if candidates:
                top_candidate = candidates[0][0]
                # Preserve case
                if word.isupper():
                    top_candidate = top_candidate.upper()
                elif word[0].isupper():
                    top_candidate = top_candidate.capitalize()
                    
                errors.append({
                    "word": word,
                    "correction": top_candidate,
                    "start": match.start(),
                    "end": match.end(),
                    "rule": "dictionary"
                })
                corrections.append((match.start(), match.end(), top_candidate))
    
    # Apply corrections from end to start
    corrections.sort(reverse=True)
    corrected_text = text
    for start, end, correction in corrections:
        corrected_text = corrected_text[:start] + correction + corrected_text[end:]
        
    return corrected_text, errors

@app.route('/check', methods=['POST'])
def check_spelling():
    data = request.json
    text = data.get('text', '')
    selected_rules = data.get('rules', [])
    
    # Separate out the dictionary rule
    use_dictionary = "dictionary" in selected_rules
    non_dict_rules = [r for r in selected_rules if r != "dictionary"]

    # Apply only non-dictionary rules
    corrected_text, rule_errors = apply_rules(text, non_dict_rules)

    spell_errors = []
    if use_dictionary:
        corrected_text, spell_errors = spellcheck_text(corrected_text)

    errors = rule_errors + spell_errors

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