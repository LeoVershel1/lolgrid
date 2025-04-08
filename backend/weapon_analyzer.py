"""
This script analyzes champion data to determine what type of weapon each champion uses.
The results can be used to populate the 'weapons' category in categories.py.
"""

import json
import re
import logging
import os
from typing import Dict, List, Set

# Configure logging
logger = logging.getLogger(__name__)

# Define magic subcategories with their keywords
MAGIC_SUBCATEGORIES = {
    "elemental_magic": ["fire", "water", "earth", "air", "wind", "flame", "ice", "frost", "lightning", "thunder", "storm", "nature", "rock", "magma", "lava"],
    "dark_magic": ["dark", "shadow", "void", "corrupt", "death", "blood", "curse", "drain", "soul", "necro", "demon", "nightmare"],
    "light_magic": ["light", "holy", "divine", "celestial", "star", "sun", "moon", "heal", "shield", "protect", "purify"],
    "arcane_magic": ["arcane", "mana", "energy", "cosmic", "time", "portal", "teleport", "dimension"],
    "mind_magic": ["mind", "psychic", "mental", "illusion", "charm", "control", "dream", "memory"],
    "summoning_magic": ["summon", "pet", "companion", "minion", "clone", "spirit", "ghost"],
    "nature_magic": ["nature", "plant", "animal", "beast", "wild", "grow", "bloom", "forest", "vine", "root", "thorn"],
    "chaos_magic": ["chaos", "random", "wild", "unstable", "transform", "change", "mutate"],
    "force_magic": ["force", "push", "pull", "gravity", "kinetic", "telekinetic", "power", "strength"],
    "runic_magic": ["rune", "glyph", "sigil", "mark", "symbol", "ancient", "ritual"]
}

# Original weapon categories
WEAPON_KEYWORDS = {
    "sword": ["sword", "blade", "greatsword", "broadsword", "longsword", "shortsword", "scimitar", "katana", "rapier"],
    "axe": ["axe", "hatchet", "tomahawk"],
    "spear": ["spear", "lance", "javelin", "halberd", "trident", "polearm"],
    "bow": ["bow", "arrow", "archer", "crossbow", "quiver"],
    "gun": ["gun", "rifle", "pistol", "cannon", "shotgun", "revolver", "blunderbuss", "gatling"],
    "staff": ["staff", "rod", "wand", "scepter", "mace", "club", "hammer"],
    "claws": ["claws", "talons", "fangs", "teeth", "paws", "hands", "fists"],
    "shield": ["shield", "buckler", "aegis"],
    "other": ["dagger", "knife", "throwing", "boomerang", "chakram", "sling", "whip", "chain", "hook"]
}

def load_champion_data(file_path: str) -> Dict:
    """Load champion data from JSON file."""
    try:
        print(f"Attempting to load champion data from: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            champions = data.get("champions", [])
            print(f"Successfully loaded {len(champions)} champions")
            return champions
    except Exception as e:
        print(f"Error loading champion data: {e}")
        return []

def analyze_champion_weapons(champion: Dict) -> Set[str]:
    """
    Analyze a champion's data to determine what weapons they use.
    Returns a set of weapon categories.
    """
    weapons = set()
    
    # Check champion name for weapon references
    name = champion.get("name", "").lower()
    
    # Check abilities for weapon references
    abilities = champion.get("abilities", {})
    ability_text = ""
    
    # Combine all ability descriptions
    for ability_key in ["passive", "q", "w", "e", "r"]:
        if ability_key in abilities:
            ability = abilities[ability_key]
            ability_text += " " + ability.get("name", "").lower() + " " + ability.get("description", "").lower()
    
    # Check for weapon keywords in name and abilities
    for weapon_category, keywords in WEAPON_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name or keyword in ability_text:
                weapons.add(weapon_category)
    
    # Special case for champions that primarily use magic
    if champion.get("primaryDamageType") == "AP":
        weapons.add("magic")
    
    # If no weapons found, default to "other"
    if not weapons:
        weapons.add("other")
    
    return weapons

def analyze_magic_types(champion: Dict) -> Set[str]:
    """
    Analyze what types of magic a champion uses.
    Returns a set of magic subcategories.
    """
    magic_types = set()
    
    # Get all text to analyze
    name = champion.get("name", "").lower()
    abilities = champion.get("abilities", {})
    text_to_analyze = name
    
    # Add ability descriptions
    for ability_key in ["passive", "q", "w", "e", "r"]:
        if ability_key in abilities:
            ability = abilities[ability_key]
            text_to_analyze += " " + ability.get("name", "").lower() + " " + ability.get("description", "").lower()
    
    # Check for magic keywords
    for magic_type, keywords in MAGIC_SUBCATEGORIES.items():
        for keyword in keywords:
            if keyword in text_to_analyze:
                magic_types.add(magic_type)
                break
    
    return magic_types

def analyze_all_champions(champions_data: List[Dict]) -> Dict[str, List[str]]:
    """
    Analyze all champions and return dictionaries mapping categories to champion names.
    """
    weapon_categories = {category: [] for category in WEAPON_KEYWORDS.keys()}
    weapon_categories["magic"] = []  # Add general magic category
    magic_categories = {category: [] for category in MAGIC_SUBCATEGORIES.keys()}
    
    for champion in champions_data:
        champion_name = champion.get("name", "Unknown")
        
        # Analyze weapons
        weapons = analyze_champion_weapons(champion)
        for weapon in weapons:
            weapon_categories[weapon].append(champion_name)
        
        # Analyze magic types for AP champions
        if champion.get("primaryDamageType") == "AP":
            magic_types = analyze_magic_types(champion)
            for magic_type in magic_types:
                magic_categories[magic_type].append(champion_name)
    
    return weapon_categories, magic_categories

def generate_category_updates(weapon_categories: Dict[str, List[str]], magic_categories: Dict[str, List[str]]) -> str:
    """
    Generate code to update the weapons and magic categories in categories.py.
    """
    # Count champions per category
    weapon_counts = {category: len(champions) for category, champions in weapon_categories.items()}
    magic_counts = {category: len(champions) for category, champions in magic_categories.items()}
    
    # Generate code
    code = "# Weapon and magic categories based on champion analysis\n"
    code += "WEAPON_CATEGORIES = [\n"
    
    # Add weapon categories
    for category, count in sorted(weapon_counts.items(), key=lambda x: x[1], reverse=True):
        code += f"    \"Has {category.capitalize()}\",  # {count} champions\n"
    
    code += "]\n\n"
    code += "# Magic subcategories with 10+ champions\n"
    code += "MAGIC_CATEGORIES = [\n"
    
    # Add magic categories with 10+ champions
    for category, count in sorted(magic_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 10:
            formatted_name = category.replace("_", " ").title()
            code += f"    \"Uses {formatted_name}\",  # {count} champions\n"
    
    code += "]\n"
    return code

def main():
    """Main function to run the weapon analysis."""
    # Load champion data
    file_path = "data/champions.json"
    print(f"Starting weapon and magic analysis with file path: {file_path}")
    
    champions_data = load_champion_data(file_path)
    
    if not champions_data:
        print("No champion data loaded. Exiting.")
        return
    
    # Analyze all champions
    print("Analyzing champions for weapon types and magic categories...")
    weapon_categories, magic_categories = analyze_all_champions(champions_data)
    
    # Generate category updates
    category_updates = generate_category_updates(weapon_categories, magic_categories)
    
    # Print results
    print("\nMagic Category Analysis Results:")
    print("==============================")
    
    # Sort magic categories by count and show those with 10+ champions
    magic_counts = {category: len(champions) for category, champions in magic_categories.items()}
    for category, count in sorted(magic_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 10:
            print(f"\n{category.replace('_', ' ').title()} ({count} champions):")
            print(", ".join(sorted(magic_categories[category])))
    
    print("\n\nSuggested Category Updates:")
    print("=========================")
    print(category_updates)
    
    # Save results to a file
    output_file = "magic_analysis_results.txt"
    print(f"Saving results to {output_file}...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Magic Category Analysis Results:\n")
        f.write("==============================\n\n")
        
        for category, champions in sorted(magic_categories.items(), key=lambda x: len(x[1]), reverse=True):
            if len(champions) >= 10:
                f.write(f"{category.replace('_', ' ').title()} ({len(champions)} champions):\n")
                f.write(", ".join(sorted(champions)) + "\n\n")
        
        f.write("\nSuggested Category Updates:\n")
        f.write("=========================\n")
        f.write(category_updates)
    
    print(f"Analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main() 