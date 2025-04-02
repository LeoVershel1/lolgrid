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
        self.in_infobox = False
        self.current_field = None
        self.data_buffer = []
        self.in_data_value = False
        self.in_list = False
        self.in_strikethrough = False
        self.in_anchor = False
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "data-source" in attrs:
            self.in_infobox = True
            self.current_field = attrs["data-source"]
            self.data_buffer = []
        elif tag == "div" and "class" in attrs and "pi-data-value" in attrs["class"]:
            self.in_data_value = True
            self.data_buffer = []
        elif tag == "ul" and self.in_data_value:
            self.in_list = True
            self.data_buffer = []
        elif tag == "li" and self.in_list:
            self.data_buffer = []
        elif tag == "s":
            self.in_strikethrough = True
        elif tag == "a" and "href" in attrs:
            self.in_anchor = True
            if self.current_field == "region" and not self.in_strikethrough:
                href = attrs["href"]
                if "/wiki/" in href:
                    region = href.split("/wiki/")[1]
                    if region in ["Runeterra", "Demacia", "Noxus", "Freljord", "Ionia", "Bilgewater", 
                                "Piltover", "Zaun", "Shurima", "Targon", "Ixtal", "Bandle_City", 
                                "Shadow_Isles", "Void"]:
                        self.region = region.replace("_", " ")
            elif self.current_field == "species" and not self.in_strikethrough:
                href = attrs["href"]
                if "/wiki/" in href:
                    species = href.split("/wiki/")[1]
                    if any(s in species for s in ["Darkin", "Human", "Yordle", "Vastaya", "Celestial", 
                                                "God-Warrior", "Brackern", "Voidborn", "Undead", "Spirit",
                                                "Iceborn", "Minotaur", "Yeti", "Dragon"]):
                        self.species = species.replace("_", " ")
    
    def handle_endtag(self, tag):
        if tag == "div" and self.in_infobox:
            self.in_data_value = False
            self.in_infobox = False
        elif tag == "ul" and self.in_data_value:
            self.in_list = False
        elif tag == "li" and self.in_list:
            pass
        elif tag == "s":
            self.in_strikethrough = False
        elif tag == "a":
            self.in_anchor = False
    
    def handle_data(self, data):
        if self.in_infobox and not self.in_strikethrough:
            self.data_buffer.append(data)

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
    url = f"https://leagueoflegends.fandom.com/wiki/{wiki_name}"
    release_url = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
    
    try:
        # First get the champion's page for region and species
        response = requests.get(url)
        response.raise_for_status()
        
        parser = ChampionInfoParser()
        parser.feed(response.text)
        
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
            "release_season": release_season
        }
    except Exception as e:
        print(f"Error fetching wiki data for {champion_name}: {e}")
        return {
            "region": "Unknown",
            "species": "Unknown",
            "release_season": None
        }

def determine_primary_damage_type(tags: List[str], spells: List[Dict[str, Any]]) -> str:
    """Determine primary damage type based on champion tags and abilities."""
    if "Marksman" in tags:
        return "AD"
    if "Mage" in tags or "AP" in " ".join(spell.get("description", "") for spell in spells):
        return "AP"
    return "AD"  # Default to AD for fighters/tanks/etc

async def create_champion_template(session: aiohttp.ClientSession, champ_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a champion entry with data from the API and template for manual data."""
    champ_id = champ_data["id"]
    detailed_data = await get_detailed_champion_data(session, champ_id)
    wiki_data = await get_wiki_data(champ_data["name"])
    
    return {
        "name": champ_data["name"],
        "region": wiki_data["region"],
        "role": champ_data["tags"],  # Automatically filled from tags
        "resource": champ_data.get("partype", ""),  # Resource type (Mana, Energy, etc)
        "species": wiki_data["species"],
        "primaryDamageType": determine_primary_damage_type(champ_data["tags"], detailed_data["spells"]),
        "range": int(champ_data.get("stats", {}).get("attackrange", 0)),
        "baseMovespeed": int(champ_data.get("stats", {}).get("movespeed", 0)),
        "releaseSeason": wiki_data["release_season"],
        "modelSize": int(champ_data.get("stats", {}).get("collision_radius", 0) * 100),  # Approximate from collision radius
        "abilities": {
            "hasPassiveE": False,  # To be filled manually
            "isShapeshifter": "TransformationChampion" in detailed_data.get("allytips", []),
            "hasThreeHitPassive": False,  # To be filled manually
            "hasAutoAttackReset": False,  # To be filled manually
            "hasAbilityCharges": any("charge" in spell.get("description", "").lower() for spell in detailed_data["spells"]),
            "hasMultipleHardCC": sum(1 for spell in detailed_data["spells"] if any(cc in spell.get("description", "").lower() for cc in ["stun", "knock", "root", "suppress"])) >= 2,
            "hasChangingAbilities": any("evolve" in spell.get("description", "").lower() or "transform" in spell.get("description", "").lower() for spell in detailed_data["spells"])
        }
    }

async def main():
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
        print("\nFields that still need manual filling:")
        print("- Some ability flags may need verification")

if __name__ == "__main__":
    asyncio.run(main()) 