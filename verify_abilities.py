import json
import requests
from typing import Dict, List, Optional
import time

# Special champion name mappings for Data Dragon API
CHAMPION_NAME_MAPPING = {
    "Aurelion Sol": "AurelionSol",
    "Bel'Veth": "Belveth",
    "Cho'Gath": "Chogath",
    "Dr. Mundo": "DrMundo",
    "Jarvan IV": "JarvanIV",
    "Kai'Sa": "Kaisa",
    "Kha'Zix": "Khazix",
    "Kog'Maw": "KogMaw",
    "K'Sante": "KSante",
    "LeBlanc": "Leblanc",
    "Lee Sin": "LeeSin",
    "Master Yi": "MasterYi",
    "Miss Fortune": "MissFortune",
    "Wukong": "MonkeyKing",
    "Nunu & Willump": "Nunu",
    "Rek'Sai": "RekSai",
    "Renata Glasc": "Renata",
    "Tahm Kench": "TahmKench",
    "Twisted Fate": "TwistedFate",
    "Vel'Koz": "Velkoz",
    "Xin Zhao": "XinZhao"
}

def load_champions_data() -> Dict:
    with open('champions.json', 'r') as f:
        return json.load(f)

def save_champions_data(data: Dict):
    with open('champions.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_champion_data(champion_name: str) -> Optional[Dict]:
    """Fetch champion data from Data Dragon API"""
    try:
        # First get the latest version
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = requests.get(versions_url).json()
        latest_version = versions[0]

        # Use mapped name if it exists
        api_name = CHAMPION_NAME_MAPPING.get(champion_name, champion_name)

        # Then get champion data
        champion_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion/{api_name}.json"
        champion_data = requests.get(champion_url).json()
        
        if 'data' in champion_data and api_name in champion_data['data']:
            return champion_data['data'][api_name]
        return None
    except Exception as e:
        print(f"Error fetching data for {champion_name}: {e}")
        return None

def analyze_ability(ability: Dict) -> Dict[str, bool]:
    """Analyze an ability and return its characteristics"""
    description = ability.get('description', '').lower()
    name = ability.get('name', '').lower()
    flags = {}

    # CC types
    cc_types = {
        'stun': 'hasStun',
        'root': 'hasRoot',
        'silence': 'hasSilence',
        'ground': 'hasGround',
        'knockup': 'hasKnockup',
        'knockback': 'hasKnockback',
        'fear': 'hasFear',
        'charm': 'hasCharm',
        'sleep': 'hasSleep',
        'taunt': 'hasTaunt',
        'polymorph': 'hasPolymorph',
        'suppression': 'hasSuppression'
    }

    # Check for CC
    has_cc = False
    for cc_type, flag in cc_types.items():
        if cc_type in description:
            flags[flag] = True
            has_cc = True

    if has_cc:
        flags['hasHardCC'] = True

    # Check for slows
    if 'slow' in description:
        flags['hasSlows'] = True

    # Check for DoT
    dot_indicators = [
        'damage over time', 'dot', 'burn', 'bleed', 'poison', 'ignite',
        'mark', 'mark of the', 'mark of', 'marking', 'marked'
    ]
    if any(indicator in description for indicator in dot_indicators):
        flags['hasDamageOverTime'] = True

    # Check for AoE
    aoe_indicators = [
        'area', 'aoe', 'radius', 'circle', 'cone', 'line', 'wave',
        'blast', 'explosion', 'burst', 'nova', 'storm', 'field',
        'zone', 'aura', 'pulse', 'shockwave'
    ]
    if any(indicator in description for indicator in aoe_indicators):
        flags['hasAreaOfEffect'] = True

    # Check for auto-attack reset
    if any(phrase in description for phrase in ['reset', 'resets', 'next attack', 'next basic attack']):
        flags['hasAutoAttackReset'] = True

    # Check for ability charges
    if any(phrase in description for phrase in ['charge', 'charges', 'stored', 'store']):
        flags['hasCharges'] = True

    # Check for ability transformations
    if any(phrase in description for phrase in ['changes', 'transforms', 'becomes', 'evolves']):
        flags['isTransforming'] = True

    # Check for shields
    if 'shield' in description:
        flags['hasShield'] = True

    # Check for healing
    if any(word in description for word in ['heal', 'healing', 'restored', 'restores']):
        flags['hasHealing'] = True

    # Detailed mobility checks
    mobility_types = {
        'dash': ['dash', 'dashes', 'dashing'],
        'blink': ['blink', 'teleport', 'flash'],
        'leap': ['leap', 'jump', 'jumping', 'leaping'],
        'pull': ['pull', 'pulls', 'pulling', 'hook'],
        'charge': ['charge toward', 'charges toward', 'charging toward'],
        'ghost': ['phase through', 'move through', 'pass through'],
        'moveSpeed': ['movement speed', 'move speed', 'moves faster', 'moving faster']
    }

    has_mobility = False
    for mobility_type, indicators in mobility_types.items():
        if any(indicator in description for indicator in indicators):
            flags[f'has{mobility_type.capitalize()}'] = True
            has_mobility = True
    
    if has_mobility:
        flags['hasMobility'] = True

    # Check for stealth
    stealth_types = {
        'invisibility': ['invisible', 'invisibility'],
        'camouflage': ['camouflage', 'camouflaged'],
        'untargetable': ['untargetable', 'untargetability'],
        'obscured': ['obscured', 'obscure vision']
    }

    has_stealth = False
    for stealth_type, indicators in stealth_types.items():
        if any(indicator in description for indicator in indicators):
            flags[f'has{stealth_type.capitalize()}'] = True
            has_stealth = True
    
    if has_stealth:
        flags['hasStealth'] = True

    return flags

def process_champion(champion: Dict) -> Dict:
    """Process a champion and organize abilities by slot with individual flags"""
    champion_name = champion['name']
    print(f"Processing {champion_name}...")
    
    # Get champion data from API
    data = get_champion_data(champion_name)
    if not data:
        print(f"Could not fetch data for {champion_name}")
        return champion

    # Initialize abilities structure
    champion['abilities'] = {
        'passive': {},
        'q': {},
        'w': {},
        'e': {},
        'r': {}
    }

    # Process passive
    if 'passive' in data:
        passive = data['passive']
        champion['abilities']['passive'] = {
            'name': passive.get('name', ''),
            'description': passive.get('description', ''),
            'flags': analyze_ability(passive)
        }

    # Process Q, W, E, R abilities
    if 'spells' in data and len(data['spells']) >= 4:
        ability_slots = ['q', 'w', 'e', 'r']
        for i, slot in enumerate(ability_slots):
            ability = data['spells'][i]
            champion['abilities'][slot] = {
                'name': ability.get('name', ''),
                'description': ability.get('description', ''),
                'flags': analyze_ability(ability)
            }

    return champion

def main():
    # Load current champions data
    champions_data = load_champions_data()
    
    # Process each champion
    for i, champion in enumerate(champions_data['champions']):
        champion = process_champion(champion)
        champions_data['champions'][i] = champion
        
        # Save after each champion in case of interruption
        save_champions_data(champions_data)
        print(f"Completed {i + 1}/{len(champions_data['champions'])} champions")
        time.sleep(1)  # Rate limiting

    print("\nAll champions processed!")

if __name__ == "__main__":
    main() 