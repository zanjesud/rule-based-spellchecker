import re
import string
from collections import Counter
import difflib
from typing import List, Tuple, Dict, Set


class SpellChecker:
    def __init__ (self, dictionary_file: str = None):
        """Initialize the SpellChecker with a dictionary file."""
        self.dictionary = set()
        self.word_frequency = Counter()

        if dictionary_file:
            self.load_dictionary(dictionary_file)
            print(f'File Loaded {dictionary_file}')
        else:
            # Default small dictionary for demonstration
            #pass
            self.load_default_dictionary()

    def load_dictionary(self, file_path: str):
        """Load dictionary from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read all lines, split by whitespace to support both space and newline separated words
                text = f.read()
                words = text.split()
                self.dictionary = set(word.strip().lower() for word in words if word.strip())
                # Simple frequency model (all words have equal weight)
                self.word_frequency = Counter({word: 1 for word in self.dictionary})
        except FileNotFoundError:
            print(f"Dictionary file not found: {file_path}")
            self.load_default_dictionary()

    def load_default_dictionary(self):
        """Load a basic dictionary if file not present."""
        words = ['technology', 'computer', 'software', 'hardware', 'internet', 'network', 'server', 'client',
        'database', 'cloud', 'storage', 'security', 'encryption', 'firewall', 'protocol', 'router',
        'switch', 'modem', 'bandwidth', 'latency', 'ethernet', 'wireless', 'bluetooth', 'wifi',
        'browser', 'website', 'web', 'application', 'app', 'mobile', 'desktop', 'laptop', 'tablet',
        'device', 'gadget', 'smartphone', 'android', 'ios', 'windows', 'linux', 'macos', 'unix',
        'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'csharp', 'ruby', 'perl', 'php',
        'swift', 'kotlin', 'go', 'rust', 'scala', 'matlab', 'r', 'sql', 'html', 'css', 'json', 'xml',
        'variable', 'function', 'method', 'class', 'object', 'inheritance', 'polymorphism', 'encapsulation',
        'abstraction', 'interface', 'module', 'package', 'library', 'framework', 'api', 'sdk', 'repository',
        'git', 'github', 'bitbucket', 'commit', 'push', 'pull', 'branch', 'merge', 'clone', 'fork',
        'algorithm', 'data', 'structure', 'array', 'list', 'tuple', 'set', 'dictionary', 'hashmap',
        'queue', 'stack', 'tree', 'graph', 'node', 'edge', 'vertex', 'search', 'sort', 'binary', 'recursion',
        'iteration', 'loop', 'condition', 'if', 'else', 'elif', 'for', 'while', 'break', 'continue', 'return',
        'error', 'exception', 'try', 'except', 'finally', 'debug', 'trace', 'log', 'warning', 'info', 'fatal',
        'compile', 'execute', 'run', 'build', 'deploy', 'test', 'unit', 'integration', 'system', 'acceptance',
        'automation', 'script', 'shell', 'command', 'terminal', 'console', 'prompt', 'argument', 'parameter',
        'option', 'flag', 'environment', 'variable', 'config', 'configuration', 'setting', 'preference',
        'the', 'and', 'or', 'not', 'in', 'is', 'this', 'that', 'these', 'those', 'a', 'an', 'to', 'of', 'for',
        'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up',
        'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        ]
        self.dictionary = set(words)
        self.word_frequency = Counter({word: 1 for word in words})

    def is_valid_word(self, word: str) -> bool:
        """Check if a word exists in the dictionary."""
        return word.lower() in self.dictionary

    def extract_words(self, text: str) -> List[str]:
        """Extract words from text, removing punctuation."""
        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words

    def edit_distance_1(self, word: str) -> Set[str]:
        """Generate all possible words with edit distance of 1."""
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]

        # Deletions
        deletes = [L + R[1:] for L, R in splits if R]

        # Transpositions
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]

        # Replacements
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]

        # Insertions
        inserts = [L + c + R for L, R in splits for c in letters]

        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word: str) -> Set[str]:
        """Generate all possible words with edit distance of 2."""
        return set(e2 for e1 in self.edit_distance_1(word)
                   for e2 in self.edit_distance_1(e1))
    
    def get_candidates(self, word: str, max_distance: int = 2) -> List[Tuple[str, float]]:
        if self.is_valid_word(word):
            return [(word, 1.0)]
        candidates = []
        edit1_candidates = self.edit_distance_1(word)
        valid_edit1 = [w for w in edit1_candidates if self.is_valid_word(w)]
        if valid_edit1:
            for candidate in valid_edit1:
                score = self.calculate_score(word, candidate, edit_distance=1)
                candidates.append((candidate, score))
        if not candidates and max_distance >= 2:
            edit2_candidates = self.edit_distance_2(word)
            valid_edit2 = [w for w in edit2_candidates if self.is_valid_word(w)]
            for candidate in valid_edit2:
                score = self.calculate_score(word, candidate, edit_distance=2)
                candidates.append((candidate, score))
        substring_candidates = self.get_substring_candidates(word)
        candidates.extend(substring_candidates)
        # Remove duplicates and sort by score
        unique_candidates = {}
        for candidate, score in candidates:
            if candidate not in unique_candidates or score > unique_candidates[candidate]:
                unique_candidates[candidate] = score
        # Filter out low similarity candidates
        result = [(w, s) for w, s in unique_candidates.items() if s > 0.59]
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:10]
    
    def calculate_score(self, original: str, candidate: str, edit_distance: int) -> float:
        # Use difflib similarity as a main factor
        seq_ratio = difflib.SequenceMatcher(None, original, candidate).ratio()
        # Base score inversely related to edit distance
        base_score = 1.0 / (edit_distance + 1)
        # Frequency bonus
        freq_score = self.word_frequency.get(candidate, 1) / 100.0
        # Length similarity bonus
        len_diff = abs(len(original) - len(candidate))
        len_score = 1.0 / (len_diff + 1)
        # Character overlap bonus
        overlap = len(set(original) & set(candidate))
        overlap_score = overlap / max(len(set(original)), len(set(candidate)))
        # Weighted sum, with more weight on sequence ratio
        return seq_ratio * 0.4 + base_score * 0.1 + freq_score * 0.1 + len_score * 0.1 + overlap_score * 0.3


    # def get_substring_candidates(self, word: str) -> List[Tuple[str, float]]:
    #     """Get candidates based on substring matching."""
    #     candidates = []
    #     for dict_word in self.dictionary:
    #         if word in dict_word:
    #             score = self.calculate_score(word, dict_word, edit_distance=0)
    #             candidates.append((dict_word, score))
    #     return candidates


    def get_substring_candidates(self, word: str) -> List[Tuple[str, float]]:
        """Get candidates based on substring matching."""
        candidates = []

        # Find words that contain the input as substring or vice versa
        for dict_word in self.dictionary:
            if word in dict_word or dict_word in word:
                # Calculate similarity score
                similarity = difflib.SequenceMatcher(None, word, dict_word).ratio()
                if similarity > 0.6: # Threshold for substring candidates
                    score = similarity * 0.3 # Lower score for substring matches
                    candidates.append((dict_word, score))

        return candidates
    
    def check_text(self, text: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Check entire text and return corrections for misspelled words.
        Returns:
        Dictionary mapping misspelled words to their correction candidates
        """
        words = self.extract_words (text)
        misspelled = {}

        for word in set(words): # Use set to avoid checking duplicates
            if not self.is_valid_word(word):
                candidates = self.get_candidates(word)
                if candidates:
                    misspelled[word] = candidates

        return misspelled
    
    def correct_text(self, text: str, auto_correct: bool = False) -> str:
        """
        Correct text by replacing misspelled words.

        Args:
        text: Input text to correct
        auto_correct: If True, automatically use the best candidate

        Returns:
        Corrected text
        """
        corrections = self.check_text(text)
        corrected_text = text

        for misspelled_word, candidates in corrections.items():
            if candidates:
                if auto_correct:
                    # Use the best candidate
                    best_candidate = candidates[0][0]
                    corrected_text = re.sub(r'\b' + re.escape(misspelled_word) + r'\b',
                    best_candidate, corrected_text, flags=re. IGNORECASE)
                else:
                    print(f"Misspelled: '{misspelled_word}'")
                    print("Suggestions:")
                    for i, (candidate, score) in enumerate(candidates[:5], 1):
                        print(f" {i}. {candidate} (confidence: {score:.3f})")
                    print()

        return corrected_text


