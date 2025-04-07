import json
import requests
from typing import Dict, List, Any
from html.parser import HTMLParser
import re
from tqdm import tqdm
import time
import sys
from bs4 import BeautifulSoup

class ChampionInfoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.regions = []
        self.species = []
        self.current_section = None
        self.current_label = None
        self.current_value = None
        self.in_characteristics = False
        self.in_personal_status = False
        self.in_professional_status = False
        self.debug = True

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and 'class' in attrs:
            classes = attrs['class'].split()
            if 'infobox-header' in classes:
                header_text = self.get_text_content()
                if 'Characteristics' in header_text:
                    self.in_characteristics = True
                elif 'Personal status' in header_text:
                    self.in_personal_status = True
                elif 'Professional status' in header_text:
                    self.in_professional_status = True
            elif 'infobox-data-label' in classes:
                self.current_label = True
            elif 'infobox-data-value' in classes:
                self.current_value = True

    def handle_data(self, data):
        if self.debug:
            print(f"Processing data: {data}")
            print(f"Found label: {data.lower()}")

        if self.current_label:
            label = data.strip().lower()
            if 'species' in label:
                self.current_section = 'species'
            elif 'place of origin' in label:
                self.current_section = 'place_of_origin'
            elif 'region' in label:
                self.current_section = 'region'
            self.current_label = False
        elif self.current_value and self.current_section:
            value = data.strip()
            if self.current_section == 'species':
                self.process_species_text(value)
            elif self.current_section == 'place_of_origin':
                self.process_place_of_origin_text(value)
            elif self.current_section == 'region':
                self.process_regions_text(value)
            self.current_value = False

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_characteristics:
                self.in_characteristics = False
            elif self.in_personal_status:
                self.in_personal_status = False
            elif self.in_professional_status:
                self.in_professional_status = False

    def process_species_text(self, text):
        # Handle species with parentheses
        if '(' in text and ')' in text:
            base_species = text[:text.find('(')].strip()
            modifier = text[text.find('('):text.find(')')+1].strip()
            self.species.append(f"{base_species} {modifier}")
        else:
            self.species.append(text)

    def process_place_of_origin_text(self, text):
        # Split by commas and clean up
        places = [p.strip() for p in text.split(',')]
        for place in places:
            if place == 'Sai':
                self.regions.append('Shurima')
            else:
                self.regions.append(place)

    def process_regions_text(self, text):
        # Split by commas and clean up
        regions = [r.strip() for r in text.split(',')]
        for region in regions:
            if region not in self.regions:
                self.regions.append(region)

    def get_text_content(self):
        # Helper method to get text content between tags
        return self.get_starttag_text()

def get_wiki_data(champion_name: str) -> dict:
    """Get region and species data from the League of Legends Universe wiki."""
    # Convert champion name to wiki format
    wiki_name = champion_name.replace("'", "%27")
    url = f"https://wiki.leagueoflegends.com/en-us/Universe:{wiki_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        regions = set()  # Use a set to avoid duplicates
        species = []
        
        # Find all infobox sections
        infobox_sections = soup.find_all('div', class_='infobox-header')
        for section in infobox_sections:
            section_title = section.get_text().strip()
            
            # Get the next sibling which contains the data
            data_section = section.find_next_sibling('div', class_='infobox-section-column')
            if not data_section:
                continue
                
            # Process each data row
            data_rows = data_section.find_all('div', class_='infobox-data-row')
            for row in data_rows:
                label = row.find('div', class_='infobox-data-label')
                value = row.find('div', class_='infobox-data-value')
                
                if not label or not value:
                    continue
                    
                label_text = label.get_text().strip().lower()
                value_text = value.get_text().strip()
                
                if 'species' in label_text:
                    # Handle species with parentheses
                    if '(' in value_text and ')' in value_text:
                        base_species = value_text[:value_text.find('(')].strip()
                        modifier = value_text[value_text.find('('):value_text.find(')')+1].strip()
                        species.append(f"{base_species} {modifier}")
                    else:
                        species.append(value_text)
                        
                elif 'place of origin' in label_text:
                    # Split by commas and clean up
                    places = [p.strip() for p in value_text.split(',')]
                    for place in places:
                        if place == 'Sai':
                            regions.add('Shurima')
                        else:
                            regions.add(place)
                            
                elif 'region' in label_text:
                    # Split by commas and clean up
                    new_regions = [r.strip() for r in value_text.split(',')]
                    for region in new_regions:
                        regions.add(region)
        
        return {
            'regions': list(regions) if regions else ['Unknown'],
            'species': species if species else ['Unknown']
        }
        
    except Exception as e:
        print(f"Error fetching data for {champion_name}: {str(e)}")
        return {
            'regions': ['Unknown'],
            'species': ['Unknown']
        }

def get_fallback_wiki_data(champion_name: str) -> dict:
    """Fallback to the regular wiki page if the Universe page fails."""
    wiki_name = champion_name.replace("'", "%27").replace(" ", "_")
    fallback_url = f"https://leagueoflegends.fandom.com/wiki/{wiki_name}/LoL/Background"
    
    try:
        print(f"Fetching data from fallback page: {fallback_url}")
        response = requests.get(fallback_url)
        response.raise_for_status()
        
        parser = ChampionInfoParser()
        parser.feed(response.text)
        
        return {
            "regions": parser.regions if parser.regions else ["Unknown"],
            "species": parser.species if parser.species else ["Unknown"]
        }
    except Exception as e:
        print(f"Error fetching fallback wiki data for {champion_name}: {e}")
        return {
            "regions": ["Unknown"],
            "species": ["Unknown"]
        }

def test_champion(champion_name: str):
    """Test the region and species data extraction for a specific champion."""
    print(f"\nTesting data extraction for {champion_name}...")
    
    # Get current data from champions.json
    try:
        with open("champions.json", "r") as f:
            champions_data = json.load(f)
    except FileNotFoundError:
        print("Error: champions.json file not found. Please run generate_champion_data.py first.")
        return
    except json.JSONDecodeError:
        print("Error: champions.json is not a valid JSON file.")
        return
    
    # Find the champion in the data
    champion = None
    for champ in champions_data["champions"]:
        if champ["name"] == champion_name:
            champion = champ
            break
    
    if not champion:
        print(f"Error: Champion '{champion_name}' not found in champions.json.")
        return
    
    # Get current region and species
    current_region = champion.get("region", "Unknown")
    current_species = champion.get("species", "Unknown")
    
    # Get wiki data
    wiki_data = get_wiki_data(champion_name)
    
    # Print comparison
    print(f"\nCurrent data:")
    print(f"  Region: {current_region}")
    print(f"  Species: {current_species}")
    
    print(f"\nWiki data:")
    print(f"  Regions: {wiki_data['regions']}")
    print(f"  Species: {wiki_data['species']}")
    
    # Check if there are differences
    if current_region != wiki_data["regions"][0] or current_species != wiki_data["species"][0]:
        print("\nDifferences found!")
    else:
        print("\nNo differences found in primary region/species.")

def update_champions_json():
    """Update region and species data in champions.json."""
    # Load the champions.json file
    try:
        with open("champions.json", "r") as f:
            champions_data = json.load(f)
    except FileNotFoundError:
        print("Error: champions.json file not found. Please run generate_champion_data.py first.")
        return
    except json.JSONDecodeError:
        print("Error: champions.json is not a valid JSON file.")
        return
    
    # Check if the file has the expected structure
    if "champions" not in champions_data:
        print("Error: champions.json does not have the expected structure.")
        return
    
    # Update each champion's region and species data
    updated_count = 0
    for champion in tqdm(champions_data["champions"], desc="Updating champion data"):
        champion_name = champion["name"]
        wiki_data = get_wiki_data(champion_name)
        
        # Convert current single region/species to lists if they're not already
        current_regions = champion.get("regions", [champion.get("region", "Unknown")])
        current_species = champion.get("species", [champion.get("species", "Unknown")])
        
        # Only update if the wiki data is different from the current data
        if set(wiki_data["regions"]) != set(current_regions) or set(wiki_data["species"]) != set(current_species):
            # Update the champion data with the new regions and species
            champion["regions"] = wiki_data["regions"]
            champion["species"] = wiki_data["species"]
            
            # For backward compatibility, also set the single region and species
            champion["region"] = wiki_data["regions"][0] if wiki_data["regions"] else "Unknown"
            champion["species"] = wiki_data["species"][0] if wiki_data["species"] else "Unknown"
            
            updated_count += 1
            print(f"Updated {champion_name}: Regions: {wiki_data['regions']}, Species: {wiki_data['species']}")
        
        # Add a small delay to avoid overwhelming the wiki server
        time.sleep(0.5)
    
    # Save the updated data back to champions.json
    with open("champions.json", "w") as f:
        json.dump(champions_data, f, indent=2)
    
    print(f"\nUpdated {updated_count} champions in champions.json")

if __name__ == "__main__":
    # Check if a test champion was specified
    if len(sys.argv) > 1:
        test_champion(sys.argv[1])
    else:
        update_champions_json() 