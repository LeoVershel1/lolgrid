"""
Streamlit app for the League of Legends Grid Game.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from categories import CATEGORY_TYPES, get_all_categories, get_champions_for_category
from grid_generator import GridGenerator, load_champions_data
import urllib.parse

app = Flask(__name__, static_folder='static')
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Access-Control-Allow-Origin"]
    }
})

# Load champion data
CHAMPION_DATA = load_champions_data()

# Load champion icons mapping
with open("champion_icons.json", "r") as f:
    CHAMPION_ICONS = json.load(f)

# Get list of all champion names for autocomplete
CHAMPION_NAMES = sorted([champion["name"] for champion in CHAMPION_DATA])

# Initialize grid generator
grid_generator = GridGenerator(CHAMPION_DATA)

# Store game states for different sessions
game_states = {}

# Store the daily challenge
daily_challenge = None
daily_challenge_date = None

def get_champions_for_categories(category1: str, category2: str) -> List[str]:
    """Get all champions that match both categories."""
    # This function is kept for backward compatibility
    # The actual implementation is now in the GridGenerator class
    difficulty, matching_champions = grid_generator.calculate_pair_difficulty(category1, category2)
    return matching_champions

def generate_valid_grid() -> Tuple[List[str], List[str], List[List[List[str]]]]:
    """Generate a valid 3x3 grid with categories that have at least one solution."""
    # This function is kept for backward compatibility
    # The actual implementation is now in the GridGenerator class
    row_categories, col_categories, solutions, _ = grid_generator.generate_valid_grid()
    return row_categories, col_categories, solutions

def generate_game_state(difficulty: float = 0.5):
    """Generate a game state with the specified difficulty"""
    game_state = grid_generator.generate_game_state(difficulty)
    game_id = str(uuid.uuid4())
    game_states[game_id] = game_state
    game_state['gameId'] = game_id
    return game_state

def generate_daily_challenge():
    """Generate a daily challenge with medium difficulty."""
    global daily_challenge, daily_challenge_date
    
    # Only generate a new challenge if it's a new day or we don't have one
    today = datetime.now().date()
    if daily_challenge_date != today or daily_challenge is None:
        # Generate a grid with medium difficulty (0.5)
        row_categories, col_categories, solutions, _ = grid_generator.generate_valid_grid(0.5)
        
        # Create the daily challenge format
        daily_challenge = {
            'rows': row_categories,
            'cols': col_categories,
            'solutions': solutions
        }
        daily_challenge_date = today
    
    return daily_challenge

@app.route('/api/daily', methods=['GET'])
def get_daily_challenge():
    """Get today's daily challenge."""
    challenge = generate_daily_challenge()
    return jsonify({
        'rows': challenge['rows'],
        'cols': challenge['cols']
    })

@app.route('/api/generate', methods=['POST'])
def generate_new_grid():
    data = request.get_json()
    difficulty = data.get('difficulty', 0.5)  # Default to medium difficulty
    
    # Use the global CHAMPION_DATA
    generator = GridGenerator(CHAMPION_DATA)
    row_categories, col_categories, solutions, _ = generator.generate_valid_grid(target_difficulty=difficulty)
    
    return jsonify({
        'rows': row_categories,
        'cols': col_categories
    })

@app.route('/api/daily/verify', methods=['POST'])
def verify_daily_challenge():
    data = request.get_json()
    row = data.get('row')
    col = data.get('col')
    champion = data.get('champion')
    
    if row is None or col is None or champion is None:
        return jsonify({'error': 'Missing required fields'}), 400
    
    challenge = generate_daily_challenge()
    row_category = challenge['rows'][row]
    col_category = challenge['cols'][col]
    
    # Get champions that match both categories
    row_champions = set(get_champions_for_category(CHAMPION_DATA, row_category))
    col_champions = set(get_champions_for_category(CHAMPION_DATA, col_category))
    valid_champions = row_champions.intersection(col_champions)
    
    is_correct = champion in valid_champions
    
    return jsonify({
        'isCorrect': is_correct
    })

@app.route('/api/game', methods=['GET'])
def get_game():
    # Get difficulty from query parameters, default to 0.5
    difficulty = float(request.args.get('difficulty', 0.5))
    # Clamp difficulty between 0 and 1
    difficulty = max(0.0, min(1.0, difficulty))
    
    return jsonify(generate_game_state(difficulty))

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    row = data.get('row')
    col = data.get('col')
    champion = data.get('champion')
    game_id = data.get('gameId')
    
    if not all(x is not None for x in [row, col, champion, game_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get current game state
    if game_id not in game_states:
        return jsonify({'error': 'Game not found'}), 404
    
    game_state = game_states[game_id]
    
    # Check if the guess is correct
    cell = game_state['grid'][row][col]
    is_correct = champion in cell['correctChampions']
    
    # Update the cell
    cell['guessedChampion'] = champion
    cell['isCorrect'] = is_correct
    
    # Update score and guesses
    if is_correct:
        game_state['score'] += 1
    game_state['guessesRemaining'] -= 1
    
    # Check if game is over
    if game_state['guessesRemaining'] == 0:
        game_state['isGameOver'] = True
    
    return jsonify(game_state)

@app.route('/api/valid-champions', methods=['POST'])
def get_valid_champions():
    data = request.get_json()
    row_category = data.get('rowCategory')
    col_category = data.get('colCategory')
    
    if not row_category or not col_category:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get champions that match both categories
    row_champions = set(get_champions_for_category(CHAMPION_DATA, row_category))
    col_champions = set(get_champions_for_category(CHAMPION_DATA, col_category))
    valid_champions = row_champions.intersection(col_champions)
    
    # Format response with champion icons
    champions = [
        {
            'name': champion,
            'icon': f"/champion_icons/{urllib.parse.quote(champion)}.png"
        }
        for champion in valid_champions
    ]
    
    return jsonify({
        'champions': champions
    })

@app.route('/api/champions', methods=['GET'])
def get_champions():
    return jsonify(CHAMPION_NAMES)

@app.route('/champion_icons/<path:filename>')
def serve_champion_icon(filename):
    # Decode the URL-encoded filename
    decoded_filename = urllib.parse.unquote(filename)
    return send_from_directory('static/champion_icons', decoded_filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001) 