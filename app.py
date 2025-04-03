"""
Streamlit app for the League of Legends Grid Game.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from categories import CATEGORY_TYPES, get_all_categories

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
with open("champions.json", "r") as f:
    CHAMPION_DATA = json.load(f)["champions"]

# Load champion icons mapping
with open("champion_icons.json", "r") as f:
    CHAMPION_ICONS = json.load(f)

# Get list of all champion names for autocomplete
CHAMPION_NAMES = sorted([champion["name"] for champion in CHAMPION_DATA])

def get_champions_for_categories(category1: str, category2: str) -> List[str]:
    """Get all champions that match both categories."""
    matching_champions = []
    
    for champion in CHAMPION_DATA:
        matches = True
        
        # Check if champion matches category1
        if category1 in CATEGORY_TYPES["location"]["categories"]:
            matches = matches and champion["region"] == category1
        elif category1 in CATEGORY_TYPES["role"]["categories"]:
            matches = matches and category1 in champion["role"]
        elif category1 in CATEGORY_TYPES["resource"]["categories"]:
            matches = matches and champion["resource"] == category1
        elif category1 in CATEGORY_TYPES["species"]["categories"]:
            matches = matches and champion["species"] == category1
        elif category1 in CATEGORY_TYPES["damage_type"]["categories"]:
            matches = matches and champion["primaryDamageType"] == category1
        elif category1 in CATEGORY_TYPES["range"]["categories"]:
            if category1 == "Melee (< 250)":
                matches = matches and champion["range"] < 250
            elif category1 == "Short Range (250-499)":
                matches = matches and 250 <= champion["range"] < 500
            elif category1 == "Long Range (500+)":
                matches = matches and champion["range"] >= 500
        elif category1 in CATEGORY_TYPES["movespeed"]["categories"]:
            matches = matches and str(champion["baseMovespeed"]) == category1
        elif category1 in CATEGORY_TYPES["release"]["categories"]:
            matches = matches and champion["releaseSeason"] == int(category1.split()[-1])
        elif category1 in CATEGORY_TYPES["model_size"]["categories"]:
            if category1 == "Small (55-64)":
                matches = matches and 55 <= champion["modelSize"] <= 64
            elif category1 == "Medium (65-79)":
                matches = matches and 65 <= champion["modelSize"] <= 79
            elif category1 == "Large (80+)":
                matches = matches and champion["modelSize"] >= 80
        elif category1 in CATEGORY_TYPES["abilities"]["categories"]:
            if category1 == "Has Passive E":
                matches = matches and champion["abilities"]["hasPassiveE"]
            elif category1 == "Is Shapeshifter":
                matches = matches and champion["abilities"]["isShapeshifter"]
            elif category1 == "Has Three-Hit Passive":
                matches = matches and champion["abilities"]["hasThreeHitPassive"]
            elif category1 == "Has Auto-Attack Reset":
                matches = matches and champion["abilities"]["hasAutoAttackReset"]
            elif category1 == "Has Ability Charges":
                matches = matches and champion["abilities"]["hasAbilityCharges"]
            elif category1 == "Has Multiple Hard CC":
                matches = matches and champion["abilities"]["hasMultipleHardCC"]
            elif category1 == "Has Changing Abilities":
                matches = matches and champion["abilities"]["hasChangingAbilities"]
        
        # Check if champion matches category2
        if category2 in CATEGORY_TYPES["location"]["categories"]:
            matches = matches and champion["region"] == category2
        elif category2 in CATEGORY_TYPES["role"]["categories"]:
            matches = matches and category2 in champion["role"]
        elif category2 in CATEGORY_TYPES["resource"]["categories"]:
            matches = matches and champion["resource"] == category2
        elif category2 in CATEGORY_TYPES["species"]["categories"]:
            matches = matches and champion["species"] == category2
        elif category2 in CATEGORY_TYPES["damage_type"]["categories"]:
            matches = matches and champion["primaryDamageType"] == category2
        elif category2 in CATEGORY_TYPES["range"]["categories"]:
            if category2 == "Melee (< 250)":
                matches = matches and champion["range"] < 250
            elif category2 == "Short Range (250-499)":
                matches = matches and 250 <= champion["range"] < 500
            elif category2 == "Long Range (500+)":
                matches = matches and champion["range"] >= 500
        elif category2 in CATEGORY_TYPES["movespeed"]["categories"]:
            matches = matches and str(champion["baseMovespeed"]) == category2
        elif category2 in CATEGORY_TYPES["release"]["categories"]:
            matches = matches and champion["releaseSeason"] == int(category2.split()[-1])
        elif category2 in CATEGORY_TYPES["model_size"]["categories"]:
            if category2 == "Small (55-64)":
                matches = matches and 55 <= champion["modelSize"] <= 64
            elif category2 == "Medium (65-79)":
                matches = matches and 65 <= champion["modelSize"] <= 79
            elif category2 == "Large (80+)":
                matches = matches and champion["modelSize"] >= 80
        elif category2 in CATEGORY_TYPES["abilities"]["categories"]:
            if category2 == "Has Passive E":
                matches = matches and champion["abilities"]["hasPassiveE"]
            elif category2 == "Is Shapeshifter":
                matches = matches and champion["abilities"]["isShapeshifter"]
            elif category2 == "Has Three-Hit Passive":
                matches = matches and champion["abilities"]["hasThreeHitPassive"]
            elif category2 == "Has Auto-Attack Reset":
                matches = matches and champion["abilities"]["hasAutoAttackReset"]
            elif category2 == "Has Ability Charges":
                matches = matches and champion["abilities"]["hasAbilityCharges"]
            elif category2 == "Has Multiple Hard CC":
                matches = matches and champion["abilities"]["hasMultipleHardCC"]
            elif category2 == "Has Changing Abilities":
                matches = matches and champion["abilities"]["hasChangingAbilities"]
        
        if matches:
            matching_champions.append(champion["name"])
    
    return matching_champions

def generate_valid_grid() -> Tuple[List[str], List[str], List[List[List[str]]]]:
    """Generate a valid 3x3 grid with categories that have at least one solution."""
    all_categories = get_all_categories()
    valid_grid = False
    row_categories = []
    col_categories = []
    solutions = []
    
    while not valid_grid:
        # Select 6 random categories (3 for rows, 3 for columns)
        categories = random.sample(all_categories, 6)
        row_categories = categories[:3]
        col_categories = categories[3:]
        
        # Check if each cell has at least one valid solution
        solutions = []
        valid_grid = True
        
        for row_cat in row_categories:
            row_solutions = []
            for col_cat in col_categories:
                cell_solutions = get_champions_for_categories(row_cat, col_cat)
                if not cell_solutions:
                    valid_grid = False
                    break
                row_solutions.append(cell_solutions)
            if not valid_grid:
                break
            solutions.append(row_solutions)
    
    return row_categories, col_categories, solutions

def generate_game_state():
    # Generate a valid grid
    row_categories, col_categories, solutions = generate_valid_grid()
    
    # Create grid
    grid = []
    for i, row_solutions in enumerate(solutions):
        row = []
        for j, cell_solutions in enumerate(row_solutions):
            row.append({
                'xCategory': col_categories[j],
                'yCategory': row_categories[i],
                'correctChampions': cell_solutions,
                'guessedChampion': None,
                'isCorrect': None
            })
        grid.append(row)
    
    # Helper function to get category type from category name
    def get_category_type(category):
        for cat_type, info in CATEGORY_TYPES.items():
            if category in info["categories"]:
                return cat_type
        return None
    
    return {
        'grid': grid,
        'categories': {
            'xAxis': [{'name': cat, 'values': list(CATEGORY_TYPES[get_category_type(cat)]["categories"])} for cat in col_categories],
            'yAxis': [{'name': cat, 'values': list(CATEGORY_TYPES[get_category_type(cat)]["categories"])} for cat in row_categories]
        },
        'guessesRemaining': 9,
        'isGameOver': False,
        'score': 0
    }

@app.route('/api/game', methods=['GET'])
def get_game():
    return jsonify(generate_game_state())

@app.route('/api/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    row = data.get('row')
    col = data.get('col')
    champion = data.get('champion')
    
    if not all(x is not None for x in [row, col, champion]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get current game state
    game_state = generate_game_state()  # In a real app, this would be stored in a session
    
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

@app.route('/api/champions', methods=['GET'])
def get_champions():
    return jsonify(CHAMPION_NAMES)

@app.route('/champion_icons/<path:filename>')
def serve_champion_icon(filename):
    return send_from_directory('static/champion_icons', filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001) 