"""
This file defines the category types and specific categories for the League of Legends grid game.
Each category type contains a list of specific categories that can be used in the game.
"""

from typing import List, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)

CATEGORY_TYPES = {
    "location": {
        "name": "Location",
        "description": "Geographic or regional categories",
        "categories": [
            "Ionia",
            "Demacia",
            "Noxus",
            "Freljord",
            "Piltover",
            "Zaun",
            "Bilgewater",
            "Shurima",
            "Targon",
            "Ixtal",
            "Bandle City",
            "Shadow Isles",
            "Void",
            "Runeterra"
        ]
    },
    "role": {
        "name": "Role",
        "description": "Champion roles and positions",
        "categories": [
            "Fighter",
            "Tank",
            "Mage",
            "Assassin",
            "Marksman",
            "Support"
        ]
    },
    "position": {
        "name": "Position",
        "description": "Champion positions in game",
        "categories": [
            "Top",
            "Jungle",
            "Mid",
            "Bot",
            "Support"
        ]
    },
    "resource": {
        "name": "Resource",
        "description": "Primary resource type used by champions",
        "categories": [
            "Mana",
            "Energy",
            "Rage",
            "Health",
            "No Resource"
        ]
    },
    "species": {
        "name": "Species",
        "description": "Champion species or race",
        "categories": [
            "Human",
            "Yordle",
            "Vastaya",
            "Darkin",
            "Voidborn",
            "Celestial",
            "God-Warrior",
            "Brackern",
            "Undead",
            "Spirit",
            "Iceborn",
            "Minotaur",
            "Yeti",
            "Dragon",
            "Is Shapeshifter"
        ]
    },
    "damage_type": {
        "name": "Damage Type",
        "description": "Primary damage type dealt by champions",
        "categories": [
            "AD",
            "AP",
            "Hybrid",
            "Has True Damage"
        ]
    },
    "range": {
        "name": "Range",
        "description": "Attack range categories",
        "categories": [
            "Melee (< 250)",
            "Short Range (250-499)",
            "Long Range (500+)"
        ]
    },
    "release": {
        "name": "Release",
        "description": "Champion release timing",
        "categories": [
            "Pre-Season",
            "Season 1",
            "Season 2",
            "Season 3",
            "Season 4",
            "Season 5",
            "Season 6",
            "Season 7",
            "Season 8",
            "Season 9",
            "Season 10",
            "Season 11",
            "Season 12",
            "Season 13",
            "Season 14"
        ]
    },
    "model_size": {
        "name": "Model Size",
        "description": "Champion model size categories",
        "categories": [
            "Small (55-64)",
            "Medium (65-79)",
            "Large (80+)"
        ]
    },
    "abilities": {
        "name": "Abilities",
        "description": "Special ability characteristics",
        "categories": [
            "Has Passive Abiltiy",
            "Has Passive Q",
            "Has Passive W",
            "Has Passive E",
            "Has Passive Ultimate",
            "Has Three-Hit Passive",
            "Has Auto-Attack Reset",
            "Has Ability Charges",
            "Has Hard CC on Q",
            "Has Hard CC on W",
            "Has Hard CC on E",
            "Has Hard CC on Ultimate",
            "Has Multiple Hard CC",
            "Has Hard CC",
            "Has No CC",
            "Has Slows",
            "Has Exactly One CC",
            "Has Ground",
            "Has Root",
            "Has Stun",
            "Has Silence",
            "Has Changing Abilities",
            "Has Damage Over Time",
            "Has Damage Over Time Q",
            "Has Damage Over Time W",
            "Has Damage Over Time E",
            "Has Damage Over Time Ultimate",
            "Has Area of Effect",
            "Has Area of Effect Q",
            "Has Area of Effect W",
            "Has Area of Effect E",
            "Has Area of Effect Ultimate"
        ]
    },
    "skins": {
        "name": "Skins",
        "description": "Skin-related categories",
        "categories": [
            "Has 2 or Less Skins",
            "Has 6+ Skins",
            "Blood Moon",
            "Project",
            "Star Guardian",
            "High Noon",
            "Arcade",
            "Pulsefire",
            "K/DA",
            "True Damage",
            "Odyssey",
            "Battle Academia",
            "Spirit Blossom",
            "Coven"
        ]
    },
    "weapons": {
        "name": "Weapons",
        "description": "Champion weapon types",
        "categories": [
            "Has Gun",
            "Has Sword",
            "Has Bow",
            "Has Staff",
            "Has Shield",
            "Has Claws",
            "Has Magic"
        ]
    }
}

def get_all_categories():
    """Returns a flat list of all specific categories across all types."""
    all_categories = []
    for category_type in CATEGORY_TYPES.values():
        all_categories.extend(category_type["categories"])
    return all_categories

def get_category_type(category):
    """Returns the type of a specific category."""
    for type_name, type_data in CATEGORY_TYPES.items():
        if category in type_data["categories"]:
            return type_name
    return None

def get_champions_for_category(champions_data: Dict, category: str) -> List[str]:
    """Get all champions that match a given category"""
    matching_champions = []
    category_type = get_category_type(category)
    
    logger.debug(f"Finding champions for category: '{category}' (type: {category_type})")
    
    for champion in champions_data:
        matches = False
        
        if category_type == "location" and category in champion["region"]:
            matches = True
        elif category_type == "role" and category in champion["class"]:
            matches = True
        elif category_type == "position" and category in champion["positions"]:
            matches = True
        elif category_type == "resource" and champion["resource"] == category:
            matches = True
        elif category_type == "species" and category in champion["species"]:
            matches = True
        elif category_type == "damage_type":
            if category == "AD" and champion["primaryDamageType"] == "AD":
                matches = True
            elif category == "AP" and champion["primaryDamageType"] == "AP":
                matches = True
            elif category == "Hybrid" and champion["primaryDamageType"] == "Hybrid":
                matches = True
            elif category == "Has True Damage" and champion.get("hasTrueDamage", False):
                matches = True
        elif category_type == "range":
            range_value = champion["range"]
            if category == "Melee (< 250)" and range_value < 250:
                matches = True
            elif category == "Short Range (250-499)" and 250 <= range_value < 500:
                matches = True
            elif category == "Long Range (500+)" and range_value >= 500:
                matches = True
        elif category_type == "release":
            season_num = int(category.split()[-1]) if category != "Pre-Season" else 0
            if champion["releaseSeason"] == season_num:
                matches = True
        elif category_type == "model_size":
            size = champion["modelSize"]
            if category == "Small (55-64)" and 55 <= size <= 64:
                matches = True
            elif category == "Medium (65-79)" and 65 <= size <= 79:
                matches = True
            elif category == "Large (80+)" and size >= 80:
                matches = True
        elif category_type == "abilities":
            # Check ability flags
            if category == "Has Passive Ability":
                matches = "passive" in champion["abilities"]
            elif category == "Has Passive Q":
                matches = "q" in champion["abilities"] and champion["abilities"]["q"].get("flags", {}).get("isPassive", False)
            elif category == "Has Passive W":
                matches = "w" in champion["abilities"] and champion["abilities"]["w"].get("flags", {}).get("isPassive", False)
            elif category == "Has Passive E":
                matches = "e" in champion["abilities"] and champion["abilities"]["e"].get("flags", {}).get("isPassive", False)
            elif category == "Has Passive Ultimate":
                matches = "r" in champion["abilities"] and champion["abilities"]["r"].get("flags", {}).get("isPassive", False)
            elif category == "Has Three-Hit Passive":
                matches = "passive" in champion["abilities"] and champion["abilities"]["passive"].get("flags", {}).get("hasThreeHitPassive", False)
            elif category == "Has Auto-Attack Reset":
                matches = any(ability.get("flags", {}).get("hasAutoAttackReset", False) for ability in champion["abilities"].values())
            elif category == "Has Ability Charges":
                matches = any(ability.get("flags", {}).get("hasCharges", False) for ability in champion["abilities"].values())
            elif category == "Has Hard CC on Q":
                matches = "q" in champion["abilities"] and champion["abilities"]["q"].get("flags", {}).get("hasHardCC", False)
            elif category == "Has Hard CC on W":
                matches = "w" in champion["abilities"] and champion["abilities"]["w"].get("flags", {}).get("hasHardCC", False)
            elif category == "Has Hard CC on E":
                matches = "e" in champion["abilities"] and champion["abilities"]["e"].get("flags", {}).get("hasHardCC", False)
            elif category == "Has Hard CC on Ultimate":
                matches = "r" in champion["abilities"] and champion["abilities"]["r"].get("flags", {}).get("hasHardCC", False)
            elif category == "Has Multiple Hard CC":
                hard_cc_count = sum(1 for ability in champion["abilities"].values() if ability.get("flags", {}).get("hasHardCC", False))
                matches = hard_cc_count > 1
            elif category == "Has Hard CC":
                matches = any(ability.get("flags", {}).get("hasHardCC", False) for ability in champion["abilities"].values())
            elif category == "Has No CC":
                matches = not any(ability.get("flags", {}).get("hasHardCC", False) or ability.get("flags", {}).get("hasSoftCC", False) for ability in champion["abilities"].values())
            elif category == "Has Slows":
                matches = any(ability.get("flags", {}).get("hasSlow", False) for ability in champion["abilities"].values())
            elif category == "Has Exactly One CC":
                cc_count = sum(1 for ability in champion["abilities"].values() if ability.get("flags", {}).get("hasHardCC", False) or ability.get("flags", {}).get("hasSoftCC", False))
                matches = cc_count == 1
            elif category == "Has Ground":
                matches = any(ability.get("flags", {}).get("hasGround", False) for ability in champion["abilities"].values())
            elif category == "Has Root":
                matches = any(ability.get("flags", {}).get("hasRoot", False) for ability in champion["abilities"].values())
            elif category == "Has Stun":
                matches = any(ability.get("flags", {}).get("hasStun", False) for ability in champion["abilities"].values())
            elif category == "Has Silence":
                matches = any(ability.get("flags", {}).get("hasSilence", False) for ability in champion["abilities"].values())
            elif category == "Has Changing Abilities":
                matches = any(ability.get("flags", {}).get("hasChangingAbilities", False) for ability in champion["abilities"].values())
            elif category == "Has Damage Over Time":
                matches = any(ability.get("flags", {}).get("hasDamageOverTime", False) for ability in champion["abilities"].values())
            elif category == "Has Damage Over Time Q":
                matches = "q" in champion["abilities"] and champion["abilities"]["q"].get("flags", {}).get("hasDamageOverTime", False)
            elif category == "Has Damage Over Time W":
                matches = "w" in champion["abilities"] and champion["abilities"]["w"].get("flags", {}).get("hasDamageOverTime", False)
            elif category == "Has Damage Over Time E":
                matches = "e" in champion["abilities"] and champion["abilities"]["e"].get("flags", {}).get("hasDamageOverTime", False)
            elif category == "Has Damage Over Time Ultimate":
                matches = "r" in champion["abilities"] and champion["abilities"]["r"].get("flags", {}).get("hasDamageOverTime", False)
            elif category == "Has Area of Effect":
                matches = any(ability.get("flags", {}).get("hasAreaOfEffect", False) for ability in champion["abilities"].values())
            elif category == "Has Area of Effect Q":
                matches = "q" in champion["abilities"] and champion["abilities"]["q"].get("flags", {}).get("hasAreaOfEffect", False)
            elif category == "Has Area of Effect W":
                matches = "w" in champion["abilities"] and champion["abilities"]["w"].get("flags", {}).get("hasAreaOfEffect", False)
            elif category == "Has Area of Effect E":
                matches = "e" in champion["abilities"] and champion["abilities"]["e"].get("flags", {}).get("hasAreaOfEffect", False)
            elif category == "Has Area of Effect Ultimate":
                matches = "r" in champion["abilities"] and champion["abilities"]["r"].get("flags", {}).get("hasAreaOfEffect", False)
        elif category_type == "skins":
            if category == "Has 2 or Less Skins":
                matches = len(champion["skinLines"]) <= 2
            elif category == "Has 6+ Skins":
                matches = len(champion["skinLines"]) >= 6
            elif category == "Has Prestige Skin":
                matches = any("Prestige" in skin for skin in champion["skinLines"])
            else:
                # For skin lines, handle special cases like "PROJECT:"
                matches = any(skin_line.lower().startswith(category.lower()) for skin_line in champion["skinLines"])
        elif category_type == "weapons":
            # We'll keep the weapons categories but they won't match any champions for now
            # This allows for future data to be added without changing the code
            matches = False
        
        if matches:
            matching_champions.append(champion["name"])
            logger.debug(f"Champion '{champion['name']}' matches category '{category}'")
    
    logger.info(f"Found {len(matching_champions)} champions matching category '{category}'")
    if matching_champions:
        logger.debug(f"Matching champions: {', '.join(matching_champions)}")
    
    return matching_champions

def validate_categories(champions_data):
    """
    Validates that each category has at least one champion and no category is empty.
    Returns a dictionary of empty categories if any are found.
    """
    empty_categories = {}
    
    logger.info("Validating all categories to ensure they have at least one champion")
    
    for category_type, type_data in CATEGORY_TYPES.items():
        for category in type_data["categories"]:
            matching_champions = get_champions_for_category(champions_data, category)
            if not matching_champions:
                empty_categories[category] = category_type
                logger.warning(f"Empty category found: '{category}' (type: {category_type})")
    
    if empty_categories:
        logger.warning(f"Found {len(empty_categories)} empty categories")
    else:
        logger.info("All categories have at least one champion")
    
    return empty_categories 