import json
import requests
from typing import Dict, List, Any
from html.parser import HTMLParser
import re
from datetime import datetime
import asyncio
import aiohttp
from tqdm import tqdm

class ChampionInfoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.region = None
        self.species = None
        self.positions = []
        self.in_infobox = False
        self.current_field = None
        self.data_buffer = []
        self.in_data_value = False
        self.in_list = False
        self.in_strikethrough = False
        self.in_anchor = False
        self.all_text = []
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "data-source" in attrs:
            self.current_field = attrs["data-source"]
            self.in_infobox = True
            self.data_buffer = []
        elif tag == "div" and "class" in attrs and "pi-data-value" in attrs["class"]:
            self.in_data_value = True
            self.data_buffer = []
        elif tag == "a" and "href" in attrs:
            href = attrs["href"]
            if (self.current_field in ["region", "origin", "birthplace"] and "/wiki/" in href):
                region = href.split("/wiki/")[1].split("/")[0].split("(")[0]
                if region in ["Runeterra", "Demacia", "Noxus", "Freljord", "Ionia", "Bilgewater", 
                            "Piltover", "Zaun", "Shurima", "Targon", "Ixtal", "Bandle_City", 
                            "Shadow_Isles", "Void"]:
                    self.region = region.replace("_", " ")
            elif (self.current_field in ["species", "race", "type"] and "/wiki/" in href):
                species = href.split("/wiki/")[1].split("/")[0].split("(")[0]
                if any(s in species for s in ["Darkin", "Human", "Yordle", "Vastaya", "Celestial", 
                                            "God-Warrior", "Brackern", "Voidborn", "Undead", "Spirit",
                                            "Iceborn", "Minotaur", "Yeti", "Dragon"]):
                    self.species = species.replace("_", " ")
            elif self.current_field == "position" and "/wiki/Category:" in href and "_champion" in href:
                position = href.split("Category:")[1].split("_")[0]
                if position == "Middle":
                    position = "Mid"
                elif position == "Bottom":
                    position = "Bot"
                if position in ["Top", "Jungle", "Mid", "Bot", "Support"] and position not in self.positions:
                    self.positions.append(position)
    
    def handle_endtag(self, tag):
        if tag == "div" and self.in_infobox:
            self.in_data_value = False
            self.in_infobox = False
            self.current_field = None
        elif tag == "ul" and self.in_data_value:
            self.in_list = False
        elif tag == "li" and self.in_list:
            pass
        elif tag == "s":
            self.in_strikethrough = False
        elif tag == "a":
            self.in_anchor = False
    
    def handle_data(self, data):
        if not self.in_strikethrough:
            self.data_buffer.append(data.strip())
            self.all_text.append(data.strip())
            
            # Try to extract region and species from text if not found in links
            if self.current_field in ["region", "origin", "birthplace"] and not self.region:
                self.process_regions()
            
            if self.current_field in ["species", "race", "type"] and not self.species:
                self.process_species()
    
    def process_regions(self):
        """Process the collected data buffer to extract regions"""
        # First try to find regions in the data buffer
        self._find_regions(" ".join(self.data_buffer).lower())
        
        # If no regions found, try searching through all text
        if not self.region:
            self._find_regions(" ".join(self.all_text).lower())
    
    def _find_regions(self, text):
        """Find regions in the given text"""
        region_mapping = {
            "runeterra": "Runeterra",
            "demacia": "Demacia",
            "noxus": "Noxus",
            "freljord": "Freljord",
            "ionia": "Ionia",
            "bilgewater": "Bilgewater",
            "piltover": "Piltover",
            "zaun": "Zaun",
            "shurima": "Shurima",
            "mount targon": "Targon",
            "targon": "Targon",
            "ixtal": "Ixtal",
            "bandle city": "Bandle City",
            "shadow isles": "Shadow Isles",
            "blessed isles": "Shadow Isles",  # Historical name for Shadow Isles
            "void": "Void",
            "icathia": "Void"  # Historical region now part of the Void
        }
        
        for keyword, region in region_mapping.items():
            if keyword in text and not self.region:
                self.region = region
                break
    
    def process_species(self):
        """Process the collected data buffer to extract species"""
        # First try to find species in the data buffer
        self._find_species(" ".join(self.data_buffer).lower())
        
        # If no species found, try searching through all text
        if not self.species:
            self._find_species(" ".join(self.all_text).lower())
    
    def _find_species(self, text):
        """Find species in the given text"""
        species_mapping = {
            "darkin": "Darkin",
            "human": "Human",
            "yordle": "Yordle",
            "vastaya": "Vastaya",
            "vastayan": "Vastaya",
            "celestial": "Celestial",
            "aspect": "Celestial",
            "god-warrior": "God-Warrior",
            "ascended": "God-Warrior",
            "brackern": "Brackern",
            "voidborn": "Voidborn",
            "void-being": "Voidborn",
            "undead": "Undead",
            "wraith": "Undead",
            "revenant": "Undead",
            "spirit": "Spirit",
            "demon": "Spirit",
            "iceborn": "Iceborn",
            "minotaur": "Minotaur",
            "yeti": "Yeti",
            "dragon": "Dragon",
            "drake": "Dragon"
        }
        
        for keyword, species in species_mapping.items():
            if keyword in text and not self.species:
                self.species = species
                break
    
    def process_positions(self):
        """Process the collected data buffer to extract positions"""
        # Only process positions from explicit position declarations
        text = " ".join(self.data_buffer).lower()
        
        # Look for explicit position declarations
        position_mapping = {
            r'\btop\s*lane[r]?\b': "Top",
            r'\btop\b': "Top",
            r'\bjungle[r]?\b': "Jungle",
            r'\bmid\s*lane[r]?\b': "Mid",
            r'\bmiddle\s*lane[r]?\b': "Mid",
            r'\bmid\b': "Mid",
            r'\bmiddle\b': "Mid",
            r'\bbot\s*lane[r]?\b': "Bot",
            r'\bbottom\s*lane[r]?\b': "Bot",
            r'\bbot\b': "Bot",
            r'\bbottom\b': "Bot",
            r'\badc\b': "Bot",
            r'\bmarksman\b': "Bot",
            r'\bsupport\b': "Support",
            r'\bsupp\b': "Support"
        }
        
        # Only process if we're in a position field and haven't found positions from category links
        if self.current_field == "position" and not self.positions:
            for pattern, position in position_mapping.items():
                if re.search(pattern, text) and position not in self.positions:
                    self.positions.append(position)
    
    def get_primary_position(self):
        """Return the primary position if any positions were found"""
        return self.positions[0] if self.positions else "Unknown"

class ReleaseInfoParser(HTMLParser):
    def __init__(self, target_champion):
        super().__init__()
        self.target_champion = target_champion
        self.release_date = None
        self.in_table = False
        self.in_row = False
        self.current_champion = None
        self.current_column = 0
        self.data_buffer = []
        self.found_champion = False
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and "class" in attrs and "sticky-header" in attrs["class"]:
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_column = 0
            self.current_champion = None
            self.data_buffer = []
        elif tag == "td" and self.in_row:
            self.current_column += 1
            self.data_buffer = []
            if self.current_column == 1:  # Champion name column
                for attr_name, attr_value in attrs.items():
                    if attr_name == "data-sort-value":
                        if attr_value == self.target_champion:
                            self.found_champion = True
    
    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tr" and self.in_row:
            self.in_row = False
        elif tag == "td" and self.in_row:
            data = "".join(self.data_buffer).strip()
            if self.current_column == 3 and self.found_champion:  # Release date column
                self.release_date = data
                self.found_champion = False  # Reset for next champion
    
    def handle_data(self, data):
        if self.in_row:
            self.data_buffer.append(data)

async def get_champion_data(session: aiohttp.ClientSession) -> Dict[str, Any]:
    """Get detailed champion data from Data Dragon."""
    async with session.get("https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion.json") as response:
        data = await response.json()
        return data["data"]

async def get_detailed_champion_data(session: aiohttp.ClientSession, champion_id: str) -> Dict[str, Any]:
    """Get even more detailed data for a specific champion."""
    url = f"https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion/{champion_id}.json"
    async with session.get(url) as response:
        data = await response.json()
        return data["data"][champion_id]

async def get_wiki_data(champion_name: str) -> dict:
    wiki_name = champion_name.replace("'", "%27").replace(" ", "_")
    url = f"https://leagueoflegends.fandom.com/wiki/{wiki_name}/LoL"
    release_url = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
    
    try:
        # First get the champion's page for region and species
        response = requests.get(url)
        response.raise_for_status()
        
        parser = ChampionInfoParser()
        parser.feed(response.text)
        
        # Process regions and species to ensure they're extracted
        parser.process_regions()
        parser.process_species()
        parser.process_positions()
        
        # Then get the release date from the champion list page
        response = requests.get(release_url)
        response.raise_for_status()
        
        release_parser = ReleaseInfoParser(champion_name)
        release_parser.feed(response.text)
        
        # Determine release season from release date
        release_season = None
        if release_parser.release_date:
            try:
                # The release date is in YYYY-MM-DD format
                release_date = datetime.strptime(release_parser.release_date, "%Y-%m-%d")
                year = release_date.year
                month = release_date.month
                
                if year < 2009:
                    release_season = 0  # Pre-season
                elif year == 2009:
                    release_season = 1  # Season 1
                elif year == 2010:
                    release_season = 1
                elif year == 2011:
                    release_season = 1 if month < 8 else 2
                elif year == 2012:
                    release_season = 2 if month < 10 else 3
                elif year == 2013:
                    release_season = 3 if month < 10 else 4
                elif year == 2014:
                    release_season = 4 if month < 11 else 5
                elif year == 2015:
                    release_season = 5 if month < 11 else 6
                elif year == 2016:
                    release_season = 6 if month < 11 else 7
                elif year == 2017:
                    release_season = 7 if month < 11 else 8
                elif year == 2018:
                    release_season = 8 if month < 11 else 9
                elif year == 2019:
                    release_season = 9 if month < 11 else 10
                elif year == 2020:
                    release_season = 10 if month < 11 else 11
                elif year == 2021:
                    release_season = 11 if month < 11 else 12
                elif year == 2022:
                    release_season = 12 if month < 11 else 13
                elif year == 2023:
                    release_season = 13 if month < 11 else 14
                else:
                    release_season = 14  # Current season
            except Exception as e:
                print(f"Error parsing release date for {champion_name}: {e}")
        
        return {
            "region": parser.region or "Unknown",
            "species": parser.species or "Unknown",
            "positions": parser.positions or ["Unknown"],
            "release_season": release_season
        }
    except Exception as e:
        print(f"Error fetching wiki data for {champion_name}: {e}")
        return {
            "region": "Unknown",
            "species": "Unknown",
            "positions": ["Unknown"],
            "release_season": None
        }

def determine_primary_damage_type(tags: List[str], spells: List[Dict[str, Any]]) -> str:
    """Determine primary damage type based on champion tags and abilities."""
    if "Marksman" in tags:
        return "AD"
    if "Mage" in tags or "AP" in " ".join(spell.get("description", "") for spell in spells):
        return "AP"
    return "AD"  # Default to AD for fighters/tanks/etc

def determine_positions(tags: List[str]) -> List[str]:
    """Determine likely positions based on champion tags/classes"""
    # Define common positions for each class
    class_positions = {
        "Assassin": ["Middle", "Jungle"],
        "Fighter": ["Top", "Jungle"],
        "Mage": ["Middle", "Support"],
        "Marksman": ["Bottom"],
        "Support": ["Support"],
        "Tank": ["Top", "Support", "Jungle"]
    }
    
    positions = set()
    for tag in tags:
        if tag in class_positions:
            positions.update(class_positions[tag])
    
    return sorted(list(positions))

async def create_champion_template(session: aiohttp.ClientSession, champ_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a champion entry with data from the API and template for manual data."""
    champ_id = champ_data["id"]
    detailed_data = await get_detailed_champion_data(session, champ_id)
    wiki_data = await get_wiki_data(champ_data["name"])
    
    # Extract skin line information
    skin_lines = set()
    for skin in detailed_data.get("skins", []):
        skin_name = skin.get("name", "")
        if skin_name and skin_name != "default":
            # Extract skin line from skin name (e.g., "Blood Moon Aatrox" -> "Blood Moon")
            skin_line = " ".join(skin_name.split()[:-1])
            if skin_line:
                skin_lines.add(skin_line)
    
    # Create ability structure with name, description, and empty flags
    abilities = {
        "passive": {"name": "", "description": "", "flags": {}},
        "q": {"name": "", "description": "", "flags": {}},
        "w": {"name": "", "description": "", "flags": {}},
        "e": {"name": "", "description": "", "flags": {}},
        "r": {"name": "", "description": "", "flags": {}}
    }
    
    # Fill in ability names and descriptions if available
    if "passive" in detailed_data:
        abilities["passive"]["name"] = detailed_data["passive"].get("name", "")
        abilities["passive"]["description"] = detailed_data["passive"].get("description", "")
    
    if "spells" in detailed_data and len(detailed_data["spells"]) >= 4:
        ability_slots = ["q", "w", "e", "r"]
        for i, slot in enumerate(ability_slots):
            if i < len(detailed_data["spells"]):
                abilities[slot]["name"] = detailed_data["spells"][i].get("name", "")
                abilities[slot]["description"] = detailed_data["spells"][i].get("description", "")
    
    # Map Data Dragon tags to champion classes
    class_mapping = {
        "Assassin": "Assassin",
        "Fighter": "Fighter",
        "Mage": "Mage",
        "Marksman": "Marksman",
        "Support": "Support",
        "Tank": "Tank"
    }
    
    # Extract classes from tags
    classes = []
    for tag in champ_data["tags"]:
        if tag in class_mapping:
            classes.append(class_mapping[tag])
    
    return {
        "name": champ_data["name"],
        "region": wiki_data["region"],
        "class": classes,  # Champion classes from Data Dragon tags
        "positions": wiki_data["positions"],  # Positions from wiki
        "resource": champ_data.get("partype", ""),  # Resource type (Mana, Energy, etc)
        "species": wiki_data["species"],
        "primaryDamageType": determine_primary_damage_type(champ_data["tags"], detailed_data["spells"]),
        "range": int(champ_data.get("stats", {}).get("attackrange", 0)),
        "baseMovespeed": int(champ_data.get("stats", {}).get("movespeed", 0)),
        "releaseSeason": wiki_data["release_season"],
        "modelSize": int(champ_data.get("stats", {}).get("gameplay_radius", 0)),  # Model size from gameplay radius
        "skinLines": sorted(list(skin_lines)),  # Add skin lines as a sorted list
        "abilities": abilities
    }

async def test_single_champion(champion_name: str):
    """Test the wiki data extraction on a single champion."""
    print(f"Testing wiki data extraction for {champion_name}...")
    
    wiki_name = champion_name.replace("'", "%27").replace(" ", "_")
    url = f"https://leagueoflegends.fandom.com/wiki/{wiki_name}/LoL"
    
    try:
        # Get the champion's page
        response = requests.get(url)
        response.raise_for_status()
        
        # Print relevant HTML sections
        html = response.text
        print("\nSearching for position information in HTML...")
        
        # Look for common position-related HTML patterns with more context
        patterns = [
            'data-source="position"',
            'data-source="role"',
            'data-source="positions"',
            'class="pi-data-label">Position',
            'class="pi-data-label">Role',
            '<th>Position</th>',
            '<th>Role</th>',
            'class="champion-ability-title">Position',
            'class="champion-ability-title">Role',
            'data-param="position"',
            'data-param="role"'
        ]
        
        for pattern in patterns:
            if pattern in html:
                print(f"\nFound pattern: {pattern}")
                # Get more context around the pattern
                start_idx = max(0, html.find(pattern) - 200)
                # Find the next closing div or table cell after this pattern
                end_idx = min(len(html), html.find(pattern) + 400)
                context = html[start_idx:end_idx]
                print("Context around pattern:")
                print(context)
                
                # Try to extract position information from this context
                position_keywords = ["top", "jungle", "mid", "middle", "bot", "bottom", "support"]
                found_positions = []
                for keyword in position_keywords:
                    if keyword in context.lower():
                        print(f"Found position keyword: {keyword}")
                        found_positions.append(keyword)
                
                if found_positions:
                    print(f"Positions found in this section: {found_positions}")
        
        # Also look for region and species information
        print("\nSearching for region and species information in HTML...")
        region_patterns = [
            'data-source="region"',
            'data-source="origin"',
            'data-source="birthplace"',
            'class="pi-data-label">Region',
            'class="pi-data-label">Origin',
            'class="pi-data-label">Birthplace',
            '<th>Region</th>',
            '<th>Origin</th>',
            '<th>Birthplace</th>'
        ]
        
        species_patterns = [
            'data-source="species"',
            'data-source="race"',
            'data-source="type"',
            'class="pi-data-label">Species',
            'class="pi-data-label">Race',
            'class="pi-data-label">Type',
            '<th>Species</th>',
            '<th>Race</th>',
            '<th>Type</th>'
        ]
        
        for pattern in region_patterns:
            if pattern in html:
                print(f"\nFound region pattern: {pattern}")
                start_idx = max(0, html.find(pattern) - 200)
                end_idx = min(len(html), html.find(pattern) + 400)
                context = html[start_idx:end_idx]
                print("Context around region pattern:")
                print(context)
                
                # Look for region links and text
                region_links = re.findall(r'href="/wiki/([^"]+)"', context)
                print(f"Region links found: {region_links}")
                
                # Try to extract region information from this context
                region_keywords = ["runeterra", "demacia", "noxus", "freljord", "ionia", "bilgewater", 
                                 "piltover", "zaun", "shurima", "targon", "ixtal", "bandle city", 
                                 "shadow isles", "void"]
                found_regions = []
                for keyword in region_keywords:
                    if keyword in context.lower():
                        print(f"Found region keyword: {keyword}")
                        found_regions.append(keyword)
                
                if found_regions:
                    print(f"Regions found in this section: {found_regions}")
        
        for pattern in species_patterns:
            if pattern in html:
                print(f"\nFound species pattern: {pattern}")
                start_idx = max(0, html.find(pattern) - 200)
                end_idx = min(len(html), html.find(pattern) + 400)
                context = html[start_idx:end_idx]
                print("Context around species pattern:")
                print(context)
                
                # Look for species links and text
                species_links = re.findall(r'href="/wiki/([^"]+)"', context)
                print(f"Species links found: {species_links}")
                
                # Try to extract species information from this context
                species_keywords = ["darkin", "human", "yordle", "vastaya", "celestial", 
                                  "god-warrior", "brackern", "voidborn", "undead", "spirit",
                                  "iceborn", "minotaur", "yeti", "dragon"]
                found_species = []
                for keyword in species_keywords:
                    if keyword in context.lower():
                        print(f"Found species keyword: {keyword}")
                        found_species.append(keyword)
                
                if found_species:
                    print(f"Species found in this section: {found_species}")
        
        # Continue with normal processing
        wiki_data = await get_wiki_data(champion_name)
        
        print("\nResults:")
        print(f"Region: {wiki_data['region']}")
        print(f"Species: {wiki_data['species']}")
        print(f"Positions: {wiki_data['positions']}")
        
        # Also test the Data Dragon API
        async with aiohttp.ClientSession() as session:
            # Get champion data
            async with session.get("https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion.json") as response:
                data = await response.json()
                champions = data["data"]
                
                # Find the champion
                for champ_id, champ_data in champions.items():
                    if champ_data["name"] == champion_name:
                        print("\nData Dragon API Data:")
                        print(f"Tags: {champ_data['tags']}")
                        
                        # Get detailed champion data
                        async with session.get(f"https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion/{champ_id}.json") as detail_response:
                            detail_data = await detail_response.json()
                            champion_detail = detail_data["data"][champ_id]
                            
                            print("\nAbilities:")
                            if "passive" in champion_detail:
                                print(f"Passive: {champion_detail['passive']['name']}")
                            
                            if "spells" in champion_detail:
                                for i, spell in enumerate(champion_detail["spells"]):
                                    print(f"{['Q', 'W', 'E', 'R'][i]}: {spell['name']}")
                        
                        break
    except Exception as e:
        print(f"Error during testing: {e}")

async def main():
    # Check if a test champion was specified
    import sys
    if len(sys.argv) > 1:
        test_champion = sys.argv[1]
        await test_single_champion(test_champion)
        return
    
    async with aiohttp.ClientSession() as session:
        # Get all champion data
        champions_data = await get_champion_data(session)
        
        # Create champion data structure with progress bar
        champion_data = {
            "champions": []
        }
        
        for champ_data in tqdm(champions_data.values(), desc="Fetching champion data"):
            champion_data["champions"].append(await create_champion_template(session, champ_data))
        
        # Write to JSON file
        with open("champions.json", "w") as f:
            json.dump(champion_data, f, indent=2)
        
        print(f"\nGenerated template for {len(champions_data)} champions in champions.json")
        print("\nNote: Ability flags will be determined by verify_abilities.py")

if __name__ == "__main__":
    asyncio.run(main()) 