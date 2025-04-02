"""
This file defines the category types and specific categories for the League of Legends grid game.
Each category type contains a list of specific categories that can be used in the game.
"""

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
            "Support",
            "Multi-class",
            "Has No Secondary Class"
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
    "movespeed": {
        "name": "Movespeed",
        "description": "Base movement speed categories",
        "categories": [
            "325",
            "330",
            "335",
            "340",
            "345"
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
            "Has Prestige Skin",
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