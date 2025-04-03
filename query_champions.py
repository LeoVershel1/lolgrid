import json
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class AbilitySlot(Enum):
    PASSIVE = "passive"
    Q = "q"
    W = "w"
    E = "e"
    R = "r"
    ANY = "any"  # For checking across all abilities

@dataclass
class AbilityQuery:
    slot: AbilitySlot
    flags: Set[str]
    required_count: int = 1  # How many flags need to match

def load_champions_data() -> Dict:
    with open('champions.json', 'r') as f:
        return json.load(f)

def check_ability_flags(ability: Dict, required_flags: Set[str]) -> bool:
    """Check if an ability has all the required flags"""
    if not ability or 'flags' not in ability:
        return False
    return all(ability['flags'].get(flag, False) for flag in required_flags)

def check_champion_abilities(champion: Dict, query: AbilityQuery) -> bool:
    """Check if a champion matches the ability query"""
    if not champion or 'abilities' not in champion:
        return False

    abilities = champion['abilities']
    matching_flags = 0

    if query.slot == AbilitySlot.ANY:
        # Check all abilities
        for slot in [AbilitySlot.PASSIVE, AbilitySlot.Q, AbilitySlot.W, AbilitySlot.E, AbilitySlot.R]:
            if slot.value in abilities:
                if check_ability_flags(abilities[slot.value], query.flags):
                    matching_flags += 1
    else:
        # Check specific ability slot
        if query.slot.value in abilities:
            if check_ability_flags(abilities[query.slot.value], query.flags):
                matching_flags += 1

    return matching_flags >= query.required_count

def find_champions(query: AbilityQuery) -> List[str]:
    """Find all champions that match the given ability query"""
    champions_data = load_champions_data()
    matching_champions = []

    for champion in champions_data['champions']:
        if check_champion_abilities(champion, query):
            matching_champions.append(champion['name'])

    return matching_champions

def print_champions(champions: List[str], query: AbilityQuery):
    """Print the matching champions in a formatted way"""
    print(f"\nChampions with {query.slot.value.upper()} ability containing flags: {', '.join(query.flags)}")
    print(f"Found {len(champions)} champions:")
    for champion in sorted(champions):
        print(f"- {champion}")

def main():
    # Example queries
    queries = [
        # Champions with hard CC on Q
        AbilityQuery(AbilitySlot.Q, {'hasHardCC'}),
        
        # Champions with dash on E
        AbilityQuery(AbilitySlot.E, {'hasDash'}),
        
        # Champions with stealth on any ability
        AbilityQuery(AbilitySlot.ANY, {'hasStealth'}),
        
        # Champions with both AoE and CC on ultimate
        AbilityQuery(AbilitySlot.R, {'hasAreaOfEffect', 'hasHardCC'}),
        
        # Champions with healing on W
        AbilityQuery(AbilitySlot.W, {'hasHealing'}),
        
        # Champions with multiple mobility types
        AbilityQuery(AbilitySlot.ANY, {'hasDash', 'hasBlink', 'hasLeap'}, required_count=2),
    ]

    for query in queries:
        champions = find_champions(query)
        print_champions(champions, query)

if __name__ == "__main__":
    main() 