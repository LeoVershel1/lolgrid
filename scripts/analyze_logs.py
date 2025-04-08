#!/usr/bin/env python3
"""
Script to analyze game logs and identify issues with game state or category matching.
"""

import os
import re
import sys
import json
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import backend modules
from backend.categories import CATEGORY_TYPES, get_all_categories, get_champions_for_category
from backend.grid_generator import GridGenerator, load_champions_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_champions_data():
    """Load champion data from the JSON file"""
    data_path = os.path.join(PROJECT_ROOT, 'data', 'champions.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["champions"]

def analyze_log_file(log_file_path):
    """Analyze the game log file to identify issues"""
    if not os.path.exists(log_file_path):
        logger.error(f"Log file not found: {log_file_path}")
        return
    
    logger.info(f"Analyzing log file: {log_file_path}")
    
    # Load champion data
    champions_data = load_champions_data()
    logger.info(f"Loaded {len(champions_data)} champions from data file")
    
    # Initialize grid generator
    grid_generator = GridGenerator(champions_data)
    
    # Patterns to match in the log file
    patterns = {
        'game_state': re.compile(r'Generated new game state with ID: ([a-f0-9-]+)'),
        'guess': re.compile(r"API request: make_guess - game: ([a-f0-9-]+), row: (\d+), col: (\d+), champion: '([^']+)'"),
        'guess_result': re.compile(r"Guess result for '([^']+)' in cell \((\d+),(\d+)\): (correct|incorrect)"),
        'correct_champions': re.compile(r"Correct champions for this cell: ([^']+)"),
        'category_match': re.compile(r"Finding champions for category: '([^']+)' \(type: ([^)]+)\)"),
        'matching_champions': re.compile(r"Found (\d+) champions matching category '([^']+)'"),
        'champion_match': re.compile(r"Champion '([^']+)' matches category '([^']+)'"),
        'category_pair': re.compile(r"Category pair '([^']+)' x '([^']+)' difficulty: ([0-9.]+) \((\d+) champions\)"),
        'valid_champions': re.compile(r"Found (\d+) valid champions for categories: '([^']+)' x '([^']+)'"),
        'error': re.compile(r"ERROR - ([^']+)")
    }
    
    # Data structures to store information from the log
    game_states = {}  # game_id -> {row_categories, col_categories, grid}
    guesses = []  # List of {game_id, row, col, champion, is_correct}
    category_matches = defaultdict(list)  # category -> [champions]
    category_pairs = {}  # (category1, category2) -> {difficulty, champions}
    errors = []  # List of error messages
    
    # Read the log file
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Check for game state generation
            match = patterns['game_state'].search(line)
            if match:
                game_id = match.group(1)
                game_states[game_id] = {'id': game_id}
            
            # Check for guesses
            match = patterns['guess'].search(line)
            if match:
                game_id, row, col, champion = match.groups()
                guesses.append({
                    'game_id': game_id,
                    'row': int(row),
                    'col': int(col),
                    'champion': champion,
                    'is_correct': None
                })
            
            # Check for guess results
            match = patterns['guess_result'].search(line)
            if match:
                champion, row, col, result = match.groups()
                is_correct = result == 'correct'
                
                # Find the most recent guess for this champion and cell
                for guess in reversed(guesses):
                    if (guess['champion'] == champion and 
                        guess['row'] == int(row) and 
                        guess['col'] == int(col) and 
                        guess['is_correct'] is None):
                        guess['is_correct'] = is_correct
                        break
            
            # Check for correct champions
            match = patterns['correct_champions'].search(line)
            if match:
                correct_champions_str = match.group(1)
                correct_champions = [c.strip() for c in correct_champions_str.split(',')]
                
                # Associate with the most recent guess
                if guesses:
                    guesses[-1]['correct_champions'] = correct_champions
            
            # Check for category matches
            match = patterns['category_match'].search(line)
            if match:
                category, category_type = match.groups()
                if category not in category_matches:
                    category_matches[category] = []
            
            # Check for matching champions
            match = patterns['matching_champions'].search(line)
            if match:
                count, category = match.groups()
                # This is just informational, we already have the champions from other patterns
            
            # Check for champion matches
            match = patterns['champion_match'].search(line)
            if match:
                champion, category = match.groups()
                if champion not in category_matches[category]:
                    category_matches[category].append(champion)
            
            # Check for category pairs
            match = patterns['category_pair'].search(line)
            if match:
                category1, category2, difficulty, count = match.groups()
                key = (category1, category2)
                category_pairs[key] = {
                    'difficulty': float(difficulty),
                    'champion_count': int(count)
                }
            
            # Check for valid champions for categories
            match = patterns['valid_champions'].search(line)
            if match:
                count, category1, category2 = match.groups()
                key = (category1, category2)
                if key in category_pairs:
                    category_pairs[key]['valid_count'] = int(count)
            
            # Check for errors
            match = patterns['error'].search(line)
            if match:
                error_msg = match.group(1)
                errors.append(error_msg)
    
    # Analyze the data
    logger.info(f"Found {len(game_states)} game states")
    logger.info(f"Found {len(guesses)} guesses")
    logger.info(f"Found {len(category_matches)} categories with matches")
    logger.info(f"Found {len(category_pairs)} category pairs")
    logger.info(f"Found {len(errors)} errors")
    
    # Check for incorrect guesses
    incorrect_guesses = [g for g in guesses if g['is_correct'] is False]
    logger.info(f"Found {len(incorrect_guesses)} incorrect guesses")
    
    # For each incorrect guess, verify if it should be correct
    for guess in incorrect_guesses:
        game_id = guess['game_id']
        row = guess['row']
        col = guess['col']
        champion = guess['champion']
        
        # Get the game state
        if game_id not in game_states:
            logger.warning(f"Game state not found for ID: {game_id}")
            continue
        
        # Get the categories for this cell
        if 'grid' not in game_states[game_id]:
            logger.warning(f"Grid not found in game state: {game_id}")
            continue
        
        # Get the cell
        try:
            cell = game_states[game_id]['grid'][row][col]
            row_category = cell['yCategory']
            col_category = cell['xCategory']
            
            # Get champions that match both categories
            row_champions = set(get_champions_for_category(champions_data, row_category))
            col_champions = set(get_champions_for_category(champions_data, col_category))
            valid_champions = row_champions.intersection(col_champions)
            
            # Check if the champion should be correct
            if champion in valid_champions:
                logger.warning(f"Potential issue: Champion '{champion}' should be correct for cell ({row},{col}) with categories '{row_category}' x '{col_category}'")
                logger.warning(f"Valid champions for this cell: {', '.join(valid_champions)}")
        except Exception as e:
            logger.error(f"Error analyzing guess: {str(e)}")
    
    # Check for category matching issues
    for category, champions in category_matches.items():
        # Get champions that should match this category
        expected_champions = set(get_champions_for_category(champions_data, category))
        
        # Check if there are any discrepancies
        if set(champions) != expected_champions:
            logger.warning(f"Potential issue with category '{category}':")
            logger.warning(f"Expected champions: {', '.join(expected_champions)}")
            logger.warning(f"Found champions: {', '.join(champions)}")
    
    # Check for category pair issues
    for (category1, category2), data in category_pairs.items():
        # Calculate the expected difficulty and champions
        expected_difficulty, expected_champions = grid_generator.calculate_pair_difficulty(category1, category2)
        
        # Check if there are any discrepancies
        if abs(data['difficulty'] - expected_difficulty) > 0.1:
            logger.warning(f"Potential issue with category pair '{category1}' x '{category2}':")
            logger.warning(f"Expected difficulty: {expected_difficulty:.3f}, Found: {data['difficulty']:.3f}")
        
        if 'valid_count' in data and data['valid_count'] != len(expected_champions):
            logger.warning(f"Potential issue with category pair '{category1}' x '{category2}':")
            logger.warning(f"Expected {len(expected_champions)} champions, Found: {data['valid_count']}")
    
    # Print summary of errors
    if errors:
        logger.info("Summary of errors:")
        for error in errors:
            logger.info(f"- {error}")

if __name__ == "__main__":
    log_file_path = os.path.join(PROJECT_ROOT, 'logs', 'game.log')
    analyze_log_file(log_file_path) 