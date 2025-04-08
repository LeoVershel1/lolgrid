import random
import json
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
import os
import sys

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from backend.categories import CATEGORY_TYPES, get_all_categories, get_category_type, get_champions_for_category

@dataclass
class CategoryPair:
    """Represents a pair of categories and their difficulty score"""
    category1: str
    category2: str
    difficulty_score: float
    matching_champions: List[str]

class GridGenerator:
    """Handles the generation of valid grids with difficulty scoring"""
    
    def __init__(self, champions_data: Dict):
        self.champions_data = champions_data
        self.category_difficulty_cache = {}  # Cache for category difficulty scores
        self.pair_difficulty_cache = {}      # Cache for category pair difficulty scores
        self.recently_used_categories = set()  # Track recently used categories
        self.max_recent_categories = 20       # How many recent categories to track
        
    def calculate_category_difficulty(self, category: str) -> float:
        """Calculate the difficulty score for a single category based on how many champions match it"""
        if category in self.category_difficulty_cache:
            return self.category_difficulty_cache[category]
        
        matching_champions = get_champions_for_category(self.champions_data, category)
        total_champions = len(self.champions_data)
        
        # Fewer matching champions = higher difficulty
        # Using a logarithmic scale to make the differences more meaningful
        if not matching_champions:
            difficulty = 1.0  # Maximum difficulty if no champions match
        else:
            # Log scale: more champions = lower difficulty
            # Normalize to 0-1 range where 0 is easiest, 1 is hardest
            difficulty = 1.0 - (math.log(len(matching_champions) + 1) / math.log(total_champions + 1))
        
        self.category_difficulty_cache[category] = difficulty
        return difficulty
    
    def calculate_pair_difficulty(self, category1: str, category2: str) -> Tuple[float, List[str]]:
        """Calculate the difficulty score for a pair of categories"""
        cache_key = f"{category1}|{category2}"
        if cache_key in self.pair_difficulty_cache:
            return self.pair_difficulty_cache[cache_key]
        
        # Get champions that match both categories
        matching_champions = []
        
        # Get champions that match each category individually
        champions_cat1 = get_champions_for_category(self.champions_data, category1)
        champions_cat2 = get_champions_for_category(self.champions_data, category2)
        
        # Find champions that match both categories
        for champion_name in champions_cat1:
            if champion_name in champions_cat2:
                matching_champions.append(champion_name)
        
        # Calculate difficulty based on number of matching champions
        total_champions = len(self.champions_data)
        
        # Fewer matching champions = higher difficulty
        if not matching_champions:
            difficulty = 1.0  # Maximum difficulty if no champions match
        else:
            # Log scale: more champions = lower difficulty
            # Normalize to 0-1 range where 0 is easiest, 1 is hardest
            difficulty = 1.0 - (math.log(len(matching_champions) + 1) / math.log(total_champions + 1))
        
        # Add a bonus for category type diversity
        cat1_type = get_category_type(category1)
        cat2_type = get_category_type(category2)
        if cat1_type != cat2_type:
            # Slightly reduce difficulty if categories are from different types
            difficulty *= 0.9
        
        result = (difficulty, matching_champions)
        self.pair_difficulty_cache[cache_key] = result
        return result
    
    def get_category_weight(self, category: str) -> float:
        """Calculate the weight for a category based on recency and difficulty"""
        base_weight = 1.0
        
        # Reduce weight if category was recently used
        if category in self.recently_used_categories:
            base_weight *= 0.5
        
        # Adjust weight based on difficulty
        difficulty = self.calculate_category_difficulty(category)
        
        # We want a mix of easy and hard categories, so we don't want to completely eliminate
        # hard categories, just make them less likely
        return base_weight * (0.5 + difficulty * 0.5)
    
    def select_categories(self, count: int, exclude_categories: Set[str] = None, valid_categories: List[str] = None) -> List[str]:
        """Select categories with weighted randomness, avoiding recently used ones"""
        if exclude_categories is None:
            exclude_categories = set()
        
        if valid_categories is None:
            valid_categories = get_all_categories()
        
        available_categories = [cat for cat in valid_categories if cat not in exclude_categories]
        
        if not available_categories:
            # If all categories are excluded, reset the recently used set
            self.recently_used_categories = set()
            available_categories = valid_categories
        
        # Calculate weights for each category
        weights = [self.get_category_weight(cat) for cat in available_categories]
        
        # Select categories based on weights
        selected = random.choices(available_categories, weights=weights, k=count)
        
        # Update recently used categories
        self.recently_used_categories.update(selected)
        if len(self.recently_used_categories) > self.max_recent_categories:
            # Remove oldest categories if we exceed the limit
            self.recently_used_categories = set(list(self.recently_used_categories)[-self.max_recent_categories:])
        
        return selected
    
    def generate_valid_grid(self, target_difficulty: float = 0.5) -> Tuple[List[str], List[str], List[List[List[str]]], float]:
        """
        Generate a valid 3x3 grid with categories that have at least one solution.
        Target difficulty is a value between 0 (easiest) and 1 (hardest).
        """
        valid_grid = False
        row_categories = []
        col_categories = []
        solutions = []
        grid_difficulty = 0.0
        attempts = 0
        max_attempts = 100
        
        # Pre-filter categories that have at least one champion
        all_categories = get_all_categories()
        valid_categories = []
        for category in all_categories:
            matching_champions = get_champions_for_category(self.champions_data, category)
            if matching_champions:
                valid_categories.append(category)
        
        if len(valid_categories) < 6:
            raise ValueError(f"Not enough valid categories found. Need at least 6, but only found {len(valid_categories)}")
        
        while not valid_grid and attempts < max_attempts:
            attempts += 1
            
            # Select 6 random categories (3 for rows, 3 for columns)
            row_categories = self.select_categories(3, valid_categories=valid_categories)
            col_categories = self.select_categories(3, exclude_categories=set(row_categories), valid_categories=valid_categories)
            
            # Check if each cell has at least one valid solution
            solutions = []
            valid_grid = True
            total_difficulty = 0.0
            cell_count = 0
            
            for row_cat in row_categories:
                row_solutions = []
                for col_cat in col_categories:
                    difficulty, cell_solutions = self.calculate_pair_difficulty(row_cat, col_cat)
                    if not cell_solutions:
                        valid_grid = False
                        break
                    row_solutions.append(cell_solutions)
                    total_difficulty += difficulty
                    cell_count += 1
                if not valid_grid:
                    break
                solutions.append(row_solutions)
            
            if valid_grid:
                # Calculate average grid difficulty
                grid_difficulty = total_difficulty / cell_count
                
                # If the grid difficulty is too far from target, try again
                if abs(grid_difficulty - target_difficulty) > 0.3:
                    valid_grid = False
        
        return row_categories, col_categories, solutions, grid_difficulty
    
    def generate_game_state(self, target_difficulty: float = 0.5):
        """Generate a game state with the specified target difficulty"""
        # Generate a valid grid
        row_categories, col_categories, solutions, grid_difficulty = self.generate_valid_grid(target_difficulty)
        
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
            'score': 0,
            'difficulty': grid_difficulty
        }

def load_champions_data() -> Dict:
    """Load champion data from the JSON file"""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, 'data', 'champions.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["champions"]  # Return the champions array

# Example usage
if __name__ == "__main__":
    champions_data = load_champions_data()
    generator = GridGenerator(champions_data)
    
    # Generate grids with different difficulty levels
    for difficulty in [0.3, 0.5, 0.7]:
        game_state = generator.generate_game_state(difficulty)
        print(f"\nGenerated grid with difficulty: {game_state['difficulty']:.2f}")
        print("Row categories:", game_state['categories']['yAxis'])
        print("Column categories:", game_state['categories']['xAxis'])
        
        # Print a sample of matching champions for each cell
        for i, row in enumerate(game_state['grid']):
            for j, cell in enumerate(row):
                champions = cell['correctChampions']
                print(f"Cell ({i},{j}): {cell['yCategory']} x {cell['xCategory']} - {len(champions)} champions")
                if champions:
                    print(f"  Sample: {', '.join(random.sample(champions, min(3, len(champions))))}") 