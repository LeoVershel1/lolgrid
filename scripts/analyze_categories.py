import json
import random
from collections import defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import from backend directory
from backend.grid_generator import GridGenerator, load_champions_data
from backend.categories import CATEGORY_TYPES, get_all_categories, get_category_type, get_champions_for_category

def analyze_category_difficulties():
    """Analyze the difficulty of all categories and generate a report"""
    champions_data = load_champions_data()
    generator = GridGenerator(champions_data)
    
    # Calculate difficulty for each category
    all_categories = get_all_categories()
    category_difficulties = {}
    
    for category in all_categories:
        difficulty = generator.calculate_category_difficulty(category)
        category_difficulties[category] = difficulty
    
    # Sort categories by difficulty
    sorted_categories = sorted(category_difficulties.items(), key=lambda x: x[1])
    
    # Print report
    print("Category Difficulty Analysis")
    print("===========================")
    print(f"Total categories: {len(all_categories)}")
    print("\nEasiest categories (most champions match):")
    for category, difficulty in sorted_categories[:10]:
        matching_champions = get_champions_for_category(champions_data, category)
        print(f"  {category}: {difficulty:.3f} ({len(matching_champions)} champions)")
    
    print("\nHardest categories (fewest champions match):")
    for category, difficulty in sorted_categories[-10:]:
        matching_champions = get_champions_for_category(champions_data, category)
        print(f"  {category}: {difficulty:.3f} ({len(matching_champions)} champions)")
    
    # Group by category type
    category_types = defaultdict(list)
    for category, difficulty in sorted_categories:
        cat_type = get_category_type(category)
        if cat_type:
            category_types[cat_type].append((category, difficulty))
    
    print("\nDifficulty by category type:")
    for cat_type, categories in category_types.items():
        avg_difficulty = sum(d for _, d in categories) / len(categories)
        print(f"  {cat_type}: {avg_difficulty:.3f} (avg)")
    
    return category_difficulties

def analyze_category_pairs():
    """Analyze the difficulty of category pairs and generate a report"""
    champions_data = load_champions_data()
    generator = GridGenerator(champions_data)
    
    # Sample some category pairs to analyze
    all_categories = get_all_categories()
    
    # Sample pairs from different category types
    category_types = list(CATEGORY_TYPES.keys())
    sampled_pairs = []
    
    # Same type pairs
    for cat_type in category_types:
        categories = CATEGORY_TYPES[cat_type]["categories"]
        if len(categories) >= 2:
            # Sample up to 5 pairs from each category type
            pairs = random.sample(categories, min(5, len(categories)))
            for i in range(0, len(pairs), 2):
                if i + 1 < len(pairs):
                    sampled_pairs.append((pairs[i], pairs[i+1]))
    
    # Different type pairs
    for i, type1 in enumerate(category_types):
        for type2 in category_types[i+1:]:
            cat1 = random.choice(CATEGORY_TYPES[type1]["categories"])
            cat2 = random.choice(CATEGORY_TYPES[type2]["categories"])
            sampled_pairs.append((cat1, cat2))
    
    # Calculate difficulty for each pair
    pair_difficulties = {}
    
    for cat1, cat2 in sampled_pairs:
        difficulty, matching_champions = generator.calculate_pair_difficulty(cat1, cat2)
        pair_difficulties[(cat1, cat2)] = (difficulty, len(matching_champions))
    
    # Sort pairs by difficulty
    sorted_pairs = sorted(pair_difficulties.items(), key=lambda x: x[1][0])
    
    # Print report
    print("\nCategory Pair Difficulty Analysis")
    print("================================")
    print(f"Total pairs analyzed: {len(sampled_pairs)}")
    
    print("\nEasiest pairs (most champions match):")
    for (cat1, cat2), (difficulty, count) in sorted_pairs[:10]:
        print(f"  {cat1} x {cat2}: {difficulty:.3f} ({count} champions)")
    
    print("\nHardest pairs (fewest champions match):")
    for (cat1, cat2), (difficulty, count) in sorted_pairs[-10:]:
        print(f"  {cat1} x {cat2}: {difficulty:.3f} ({count} champions)")
    
    # Analyze same type vs different type pairs
    same_type_pairs = []
    different_type_pairs = []
    
    for (cat1, cat2), (difficulty, _) in sorted_pairs:
        type1 = get_category_type(cat1)
        type2 = get_category_type(cat2)
        
        if type1 == type2:
            same_type_pairs.append(difficulty)
        else:
            different_type_pairs.append(difficulty)
    
    if same_type_pairs and different_type_pairs:
        avg_same_type = sum(same_type_pairs) / len(same_type_pairs)
        avg_different_type = sum(different_type_pairs) / len(different_type_pairs)
        
        print(f"\nSame type pairs (avg): {avg_same_type:.3f}")
        print(f"Different type pairs (avg): {avg_different_type:.3f}")
    
    return pair_difficulties

def visualize_difficulties(category_difficulties, pair_difficulties):
    """Create visualizations of the difficulty distributions"""
    # Category difficulty distribution
    difficulties = list(category_difficulties.values())
    
    plt.figure(figsize=(10, 6))
    plt.hist(difficulties, bins=20, alpha=0.7, color='blue')
    plt.title('Distribution of Category Difficulties')
    plt.xlabel('Difficulty Score')
    plt.ylabel('Number of Categories')
    plt.grid(True, alpha=0.3)
    plt.savefig('category_difficulty_distribution.png')
    
    # Pair difficulty distribution
    pair_diffs = [diff for _, (diff, _) in pair_difficulties.items()]
    
    plt.figure(figsize=(10, 6))
    plt.hist(pair_diffs, bins=20, alpha=0.7, color='green')
    plt.title('Distribution of Category Pair Difficulties')
    plt.xlabel('Difficulty Score')
    plt.ylabel('Number of Pairs')
    plt.grid(True, alpha=0.3)
    plt.savefig('pair_difficulty_distribution.png')
    
    print("\nVisualizations saved as 'category_difficulty_distribution.png' and 'pair_difficulty_distribution.png'")

def generate_grid_samples():
    """Generate sample grids with different difficulty levels"""
    champions_data = load_champions_data()
    generator = GridGenerator(champions_data)
    
    difficulties = [0.3, 0.5, 0.7]
    
    print("\nSample Grids with Different Difficulties")
    print("=====================================")
    
    for difficulty in difficulties:
        game_state = generator.generate_game_state(difficulty)
        print(f"\nGrid with target difficulty: {difficulty:.1f}")
        print(f"Actual difficulty: {game_state['difficulty']:.3f}")
        
        print("\nRow categories:")
        for cat in game_state['categories']['yAxis']:
            print(f"  {cat['name']}")
        
        print("\nColumn categories:")
        for cat in game_state['categories']['xAxis']:
            print(f"  {cat['name']}")
        
        print("\nSample champions for each cell:")
        for i, row in enumerate(game_state['grid']):
            for j, cell in enumerate(row):
                champions = cell['correctChampions']
                print(f"  Cell ({i},{j}): {cell['yCategory']} x {cell['xCategory']} - {len(champions)} champions")
                if champions:
                    sample = random.sample(champions, min(3, len(champions)))
                    print(f"    Sample: {', '.join(sample)}")

def main():
    print("Analyzing League of Legends Grid Game Categories")
    print("=============================================")
    
    # Analyze individual categories
    category_difficulties = analyze_category_difficulties()
    
    # Analyze category pairs
    pair_difficulties = analyze_category_pairs()
    
    # Visualize the results
    visualize_difficulties(category_difficulties, pair_difficulties)
    
    # Generate sample grids
    generate_grid_samples()

if __name__ == "__main__":
    main() 