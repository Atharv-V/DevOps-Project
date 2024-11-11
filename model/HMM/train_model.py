from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd
import nltk
import logging

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('treebank')
nltk.download('universal_tagset')

# Load the model
try:
    with open('pos_tagging_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
except FileNotFoundError:
    logger.error("The model file 'pos_tagging_model.pkl' was not found.")
    raise

initial_probs = model_data.get('initial_probs', {})
transition_probs = model_data.get('transition_probs', {})
emission_probs = model_data.get('emission_probs', {})
tags = model_data.get('tags', [])
unique_words = model_data.get('unique_words', [])

# Prepare DataFrame for transition probabilities
tags_df = pd.DataFrame(
    [[transition_probs.get(tag, {}).get(next_tag, 0) for next_tag in tags] for tag in tags],
    columns=tags,
    index=tags
)

# Rule-Based Tagging
patterns = [
    (r'.*ing$', 'VERB'),
    (r'.*ed$', 'VERB'),
    (r'.*es$', 'VERB'),
    (r'.*\'s$', 'NOUN'),
    (r'.*s$', 'NOUN'),
    (r'\*T?\*?-[0-9]+$', 'X'),
    (r'^-?[0-9]+(.[0-9]+)?$', 'NUM'),
    (r'.*', 'NOUN')
]

rule_based_tagger = nltk.RegexpTagger(patterns)

def Viterbi(words):
    states = []
    T = tags
    for key, word in enumerate(words):
        p = []
        for tag in T:
            transition_p = tags_df.loc[states[-1], tag] if key > 0 else tags_df.loc['.', tag]
            emission_p = emission_probs.get(tag, {}).get(word, 0)
            state_probability = emission_p * transition_p
            p.append(state_probability)
        pmax = max(p)
        state_max = T[p.index(pmax)]
        states.append(state_max)
    return list(zip(words, states))

def Viterbi_rule_based(words):
    states = []
    T = tags
    for key, word in enumerate(words):
        p = []
        for tag in T:
            transition_p = tags_df.loc[states[-1], tag] if key > 0 else tags_df.loc['.', tag]
            emission_p = emission_probs.get(tag, {}).get(word, 0)
            state_probability = emission_p * transition_p
            p.append(state_probability)
        pmax = max(p)
        state_max = rule_based_tagger.tag([word])[0][1] if pmax == 0 else T[p.index(pmax)]
        states.append(state_max)
    return list(zip(words, states))

# API Endpoint for standard tagging
@app.route('/tag', methods=['POST'])
def tag_sentence():
    try:
        data = request.json
        if not data or 'sentence' not in data:
            return jsonify({'error': 'No sentence provided'}), 400

        sentence = data['sentence']
        if not isinstance(sentence, str):
            return jsonify({'error': 'Invalid sentence format. Must be a string.'}), 400

        words = [word.lower() for word in sentence.split()]
        pos_tags = Viterbi(words)
        tagged_sentence = list(zip(words, pos_tags))

        return jsonify({'tagged_sentence': tagged_sentence})

    except Exception as e:
        logger.error(f"Error processing sentence: {e}")
        return jsonify({'error': 'An error occurred while processing the sentence'}), 500

# API Endpoint for rule-based tagging
@app.route('/tag_rule_based', methods=['POST'])
def tag_sentence_rule_based():
    try:
        data = request.json
        if not data or 'sentence' not in data:
            return jsonify({'error': 'No sentence provided'}), 400

        sentence = data['sentence']
        if not isinstance(sentence, str):
            return jsonify({'error': 'Invalid sentence format. Must be a string.'}), 400

        words = [word.lower() for word in sentence.split()]
        pos_tags = Viterbi_rule_based(words)
        tagged_sentence = list(zip(words, pos_tags))

        return jsonify({'tagged_sentence': tagged_sentence})

    except Exception as e:
        logger.error(f"Error processing sentence with rule-based tagging: {e}")
        return jsonify({'error': 'An error occurred while processing the sentence'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=7080)
