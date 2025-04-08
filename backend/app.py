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
import sys
import os
import logging

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import backend modules
from backend.categories import CATEGORY_TYPES, get_all_categories, get_champions_for_category
from backend.grid_generator import GridGenerator, load_champions_data

import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'logs', 'game.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'))
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
logger.info(f"Loaded {len(CHAMPION_DATA)} champions from data file")

# Load champion icons mapping
with open(os.path.join(PROJECT_ROOT, "data", "champion_icons.json"), "r") as f:
    CHAMPION_ICONS = json.load(f)
    logger.info(f"Loaded {len(CHAMPION_ICONS)} champion icons")

# Get list of all champion names for autocomplete
CHAMPION_NAMES = sorted([champion["name"] for champion in CHAMPION_DATA])

# Initialize grid generator
grid_generator = GridGenerator(CHAMPION_DATA)
logger.info("Initialized grid generator")

# Store game states for different sessions
game_states = {}

# Store the daily challenge
daily_challenge = None
daily_challenge_date = None

def validate_game_state(game_state: Dict) -> bool:
    """Validate that a game state has all required fields and correct structure."""
    try:
        # Check required top-level fields
        required_fields = ['grid', 'categories', 'guessesRemaining', 'isGameOver', 'score', 'gameId']
        if not all(field in game_state for field in required_fields):
            logger.error(f"Game state missing required fields: {[f for f in required_fields if f not in game_state]}")
            return False

        # Validate grid structure
        if not isinstance(game_state['grid'], list) or len(game_state['grid']) != 3:
            logger.error("Invalid grid structure: grid must be a 3x3 array")
            return False

        for row in game_state['grid']:
            if not isinstance(row, list) or len(row) != 3:
                logger.error("Invalid grid structure: each row must contain 3 cells")
                return False
            for cell in row:
                if not isinstance(cell, dict):
                    logger.error("Invalid cell structure: each cell must be a dictionary")
                    return False
                required_cell_fields = ['xCategory', 'yCategory', 'correctChampions']
                if not all(field in cell for field in required_cell_fields):
                    logger.error(f"Cell missing required fields: {[f for f in required_cell_fields if f not in cell]}")
                    return False
                if not isinstance(cell['correctChampions'], list):
                    logger.error("Invalid correctChampions field: must be a list")
                    return False

        return True
    except Exception as e:
        logger.error(f"Error validating game state: {str(e)}")
        return False

def get_game_state(game_id: str) -> Optional[Dict]:
    """Safely retrieve a game state, with validation."""
    try:
        if game_id not in game_states:
            logger.error(f"Game state not found for ID: {game_id}")
            return None
        
        game_state = game_states[game_id]
        if not validate_game_state(game_state):
            logger.error(f"Invalid game state found for ID: {game_id}")
            # Remove corrupted game state
            del game_states[game_id]
            return None
        
        return game_state
    except Exception as e:
        logger.error(f"Error retrieving game state: {str(e)}")
        return None

def save_game_state(game_id: str, game_state: Dict) -> bool:
    """Safely save a game state, with validation."""
    try:
        if not validate_game_state(game_state):
            logger.error(f"Attempted to save invalid game state for ID: {game_id}")
            return False
        
        game_states[game_id] = game_state
        logger.info(f"Successfully saved game state for ID: {game_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving game state: {str(e)}")
        return False

def get_champions_for_categories(category1: str, category2: str) -> List[str]:
    """Get all champions that match both categories."""
    # This function is kept for backward compatibility
    # The actual implementation is now in the GridGenerator class
    logger.debug(f"Finding champions matching both categories: '{category1}' and '{category2}'")
    difficulty, matching_champions = grid_generator.calculate_pair_difficulty(category1, category2)
    logger.info(f"Found {len(matching_champions)} champions matching both categories")
    return matching_champions

def generate_valid_grid() -> Tuple[List[str], List[str], List[List[List[str]]]]:
    """Generate a valid 3x3 grid with categories that have at least one solution."""
    # This function is kept for backward compatibility
    # The actual implementation is now in the GridGenerator class
    logger.info("Generating valid grid")
    row_categories, col_categories, solutions, _ = grid_generator.generate_valid_grid()
    logger.info(f"Generated grid with row categories: {row_categories}")
    logger.info(f"Generated grid with column categories: {col_categories}")
    return row_categories, col_categories, solutions

def generate_game_state(difficulty: float = 0.5):
    """Generate a game state with the specified difficulty"""
    try:
        logger.info(f"Generating game state with difficulty: {difficulty}")
        game_state = grid_generator.generate_game_state(difficulty)
        game_id = str(uuid.uuid4())
        game_state['gameId'] = game_id
        
        if not save_game_state(game_id, game_state):
            logger.error("Failed to save initial game state")
            return None
        
        logger.info(f"Generated new game state with ID: {game_id}")
        return game_state
    except Exception as e:
        logger.error(f"Error generating game state: {str(e)}")
        return None

def generate_daily_challenge():
    """Generate a daily challenge with medium difficulty."""
    global daily_challenge, daily_challenge_date
    
    # Only generate a new challenge if it's a new day or we don't have one
    today = datetime.now().date()
    if daily_challenge_date != today or daily_challenge is None:
        logger.info("Generating new daily challenge")
        # Generate a grid with medium difficulty (0.5)
        row_categories, col_categories, solutions, _ = grid_generator.generate_valid_grid(0.5)
        
        # Create the daily challenge format
        daily_challenge = {
            'rows': row_categories,
            'cols': col_categories,
            'solutions': solutions
        }
        daily_challenge_date = today
        logger.info(f"Generated daily challenge with row categories: {row_categories}")
        logger.info(f"Generated daily challenge with column categories: {col_categories}")
    else:
        logger.info("Using existing daily challenge")
    
    return daily_challenge

@app.route('/api/daily', methods=['GET'])
def get_daily_challenge():
    """Get today's daily challenge."""
    logger.info("API request: get_daily_challenge")
    challenge = generate_daily_challenge()
    return jsonify({
        'rows': challenge['rows'],
        'cols': challenge['cols']
    })

@app.route('/api/generate', methods=['POST'])
def generate_new_grid():
    data = request.get_json()
    difficulty = data.get('difficulty', 0.5)  # Default to medium difficulty
    logger.info(f"API request: generate_new_grid with difficulty: {difficulty}")
    
    # Use the global CHAMPION_DATA
    generator = GridGenerator(CHAMPION_DATA)
    row_categories, col_categories, solutions, _ = generator.generate_valid_grid(target_difficulty=difficulty)
    
    logger.info(f"Generated grid with row categories: {row_categories}")
    logger.info(f"Generated grid with column categories: {col_categories}")
    
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
    
    logger.info(f"API request: verify_daily_challenge - row: {row}, col: {col}, champion: {champion}")
    
    if row is None or col is None or champion is None:
        logger.error("Missing required fields in verify_daily_challenge request")
        return jsonify({'error': 'Missing required fields'}), 400
    
    challenge = generate_daily_challenge()
    row_category = challenge['rows'][row]
    col_category = challenge['cols'][col]
    
    logger.debug(f"Verifying champion '{champion}' for cell with categories: '{row_category}' x '{col_category}'")
    
    # Get champions that match both categories
    row_champions = set(get_champions_for_category(CHAMPION_DATA, row_category))
    col_champions = set(get_champions_for_category(CHAMPION_DATA, col_category))
    valid_champions = row_champions.intersection(col_champions)
    
    is_correct = champion in valid_champions
    logger.info(f"Verification result for '{champion}': {'correct' if is_correct else 'incorrect'}")
    
    if not is_correct:
        logger.debug(f"Valid champions for this cell: {', '.join(valid_champions)}")
    
    return jsonify({
        'isCorrect': is_correct
    })

@app.route('/api/game', methods=['GET'])
def get_game():
    try:
        # Get difficulty from query parameters, default to 0.5
        difficulty = float(request.args.get('difficulty', 0.5))
        # Clamp difficulty between 0 and 1
        difficulty = max(0.0, min(1.0, difficulty))
        
        logger.info(f"API request: get_game with difficulty: {difficulty}")
        
        game_state = generate_game_state(difficulty)
        if game_state is None:
            logger.error("Failed to generate game state")
            return jsonify({'error': 'Failed to generate game state'}), 500
        
        return jsonify(game_state)
    except Exception as e:
        logger.error(f"Error in get_game: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/guess', methods=['POST'])
def make_guess():
    try:
        data = request.get_json()
        row = data.get('row')
        col = data.get('col')
        champion = data.get('champion')
        game_id = data.get('gameId')
        
        logger.info(f"API request: make_guess - game: {game_id}, row: {row}, col: {col}, champion: {champion}")
        
        if not all(x is not None for x in [row, col, champion, game_id]):
            logger.error("Missing required fields in make_guess request")
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get current game state
        game_state = get_game_state(game_id)
        if game_state is None:
            logger.error(f"Game state not found for ID: {game_id}")
            return jsonify({'error': 'Game not found or corrupted'}), 404
        
        # Validate row and col indices
        if not (0 <= row < 3 and 0 <= col < 3):
            logger.error(f"Invalid cell coordinates: row={row}, col={col}")
            return jsonify({'error': 'Invalid cell coordinates'}), 400
        
        # Check if the guess is correct
        cell = game_state['grid'][row][col]
        is_correct = champion in cell['correctChampions']
        
        logger.info(f"Guess result for '{champion}' in cell ({row},{col}): {'correct' if is_correct else 'incorrect'}")
        
        if not is_correct:
            logger.debug(f"Correct champions for this cell: {', '.join(cell['correctChampions'])}")
        
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
            logger.info(f"Game completed - ID: {game_id}, Final Score: {game_state['score']}")
        
        # Save the updated game state
        if not save_game_state(game_id, game_state):
            logger.error(f"Failed to save updated game state for ID: {game_id}")
            return jsonify({'error': 'Failed to save game state'}), 500
        
        return jsonify(game_state)
    except Exception as e:
        logger.error(f"Error in make_guess: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/valid-champions', methods=['POST'])
def get_valid_champions():
    data = request.get_json()
    row_category = data.get('rowCategory')
    col_category = data.get('colCategory')
    
    logger.info(f"API request: get_valid_champions - row: '{row_category}', col: '{col_category}'")
    
    if not row_category or not col_category:
        logger.error("Missing required fields in get_valid_champions request")
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get champions that match both categories
    row_champions = set(get_champions_for_category(CHAMPION_DATA, row_category))
    col_champions = set(get_champions_for_category(CHAMPION_DATA, col_category))
    valid_champions = row_champions.intersection(col_champions)
    
    logger.info(f"Found {len(valid_champions)} valid champions for categories: '{row_category}' x '{col_category}'")
    
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
    logger.info("API request: get_champions")
    return jsonify(CHAMPION_NAMES)

@app.route('/champion_icons/<path:filename>')
def serve_champion_icon(filename):
    # Decode the URL-encoded filename
    decoded_filename = urllib.parse.unquote(filename)
    logger.debug(f"Serving champion icon: {decoded_filename}")
    return send_from_directory(os.path.join(PROJECT_ROOT, 'static', 'champion_icons'), decoded_filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001) 