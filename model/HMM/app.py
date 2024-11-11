from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)
from flask_cors import CORS
CORS(app)


# Load the trained model parameters
try:
    with open('pos_tagging_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError("The model file 'pos_tagging_model.pkl' was not found. Please ensure the model is trained and the file is available.")

initial_probs = model_data['initial_probs']
transition_probs = model_data['transition_probs']
emission_probs = model_data['emission_probs']
tags = model_data['tags']
unique_words = model_data['unique_words']

# Viterbi Algorithm
def viterbi_algorithm(sentence, tags, initial_probs, transition_probs, emission_probs):
    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for tag in tags:
        V[0][tag] = initial_probs.get(tag, 0) * emission_probs[tag].get(sentence[0], 0)
        path[tag] = [tag]

    # Run Viterbi for t > 0
    for t in range(1, len(sentence)):
        V.append({})
        new_path = {}

        for tag in tags:
            (prob, state) = max(
                (V[t-1][y0] * transition_probs[y0].get(tag, 0) * emission_probs[tag].get(sentence[t], 0), y0)
                for y0 in tags
            )
            V[t][tag] = prob
            new_path[tag] = path[state] + [tag]

        path = new_path

    # Return the most probable sequence and its probability
    (prob, state) = max((V[t][y], y) for y in tags)
    return path[state]

# API Endpoint to tag a sentence
@app.route('/tag', methods=['POST'])
def tag_sentence():
    try:
        # Parse the incoming JSON request
        data = request.json

        # Check if sentence is provided
        if not data or 'sentence' not in data:
            return jsonify({'error': 'No sentence provided'}), 400

        sentence = data['sentence']

        # Check if the input is a string
        if not isinstance(sentence, str):
            return jsonify({'error': 'Invalid sentence format. Must be a string.'}), 400

        # Process the sentence
        words = [word.lower() for word in sentence.split()]
        pos_tags = viterbi_algorithm(words, tags, initial_probs, transition_probs, emission_probs)
        tagged_sentence = list(zip(words, pos_tags))

        # Return the tagged sentence
        return jsonify({'tagged_sentence': tagged_sentence})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=7080)
