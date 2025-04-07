import json
import re

# Define the valid regions
VALID_REGIONS = [
    "Bandle City", "Bilgewater", "Demacia", "Ionia", "Ixtal", "Noxus", 
    "Piltover", "Shadow Isles", "Shurima", "Targon", "Freljord", 
    "The Void", "Zaun"
]

# Region mapping for specific locations to their parent regions
REGION_MAPPING = {
    # Shurima related
    "Icathia": "Shurima",
    "Blessed Isles": "Shadow Isles",
    "Serpent Isles": "Shadow Isles",
    "Kathkan": "Shurima",
    "Oovi-Kat Island": "Shurima",
    "Ixaocan": "Ixtal",
    "Shimon Village": "Ionia",
    "Navori": "Ionia",
    "Wuju": "Ionia",
    "Koyehn": "Ionia",
    "Marai Territory": "Bilgewater",
    "Rygann's Reach": "Freljord",
    "Vathcaer": "Freljord",
    "Rakkor Caves": "Targon",
    "Mount Targon": "Targon",
    "Temple of Thanjuul": "Shurima",
    "Monolith": "Targon",
    "High Silvermere": "Demacia",
    "Noxus Prime": "Noxus",
    "Camavor": "Shadow Isles",
    "Kingdom of Camavor": "Shadow Isles",
    "Ramshara": "Bandle City",
    "Targon Prime": "Targon",
    "Spirit Realm": "Unknown",
    "Runeterra": "Unknown"
}

def clean_species(species_data):
    """
    Convert a species string or list to a list of species.
    Handles species separated by newlines and parentheses.
    Species with parentheses are split into separate entries.
    E.g., "Human (Iceborn)" becomes ["Human", "Iceborn"]
    """
    # If species_data is already a list and doesn't contain any parentheses, return it
    if isinstance(species_data, list):
        # Check if any item in the list contains parentheses
        has_parentheses = any('(' in item for item in species_data)
        if not has_parentheses:
            return species_data
        # If there are parentheses, process each item
        cleaned_species = []
        for item in species_data:
            cleaned = clean_species(item)
            for species in cleaned:
                if species not in cleaned_species:
                    cleaned_species.append(species)
        return cleaned_species
    
    # If species_data is a string, process it
    if isinstance(species_data, str):
        if not species_data:
            return ["Unknown"]
        
        # Split by newlines and clean up
        species_list = [s.strip() for s in species_data.split('\n') if s.strip()]
        
        # Handle species with parentheses
        cleaned_species = []
        for species in species_list:
            if '(' in species and ')' in species:
                # Extract the base species and the modifier
                base = species[:species.find('(')].strip()
                modifier = species[species.find('(')+1:species.find(')')].strip()
                
                # Add base species if not already in list
                if base and base not in cleaned_species:
                    cleaned_species.append(base)
                
                # Handle multiple modifiers separated by semicolons
                modifiers = [m.strip() for m in modifier.split(';')]
                for mod in modifiers:
                    if mod and mod not in cleaned_species:
                        cleaned_species.append(mod)
            else:
                if species and species not in cleaned_species:
                    cleaned_species.append(species)
        
        return cleaned_species if cleaned_species else ["Unknown"]
    
    # If species_data is neither a string nor a list, return Unknown
    return ["Unknown"]

def clean_region(region_data):
    """
    Convert a region string or list to a list of valid regions.
    Maps specific locations to their parent regions.
    """
    # If region_data is already a list, process each item
    if isinstance(region_data, list):
        cleaned_regions = []
        for region in region_data:
            if isinstance(region, str):
                cleaned = clean_region(region)
                cleaned_regions.extend(cleaned)
        return list(set(cleaned_regions)) if cleaned_regions else ["Unknown"]
    
    # If region_data is a string, process it
    if isinstance(region_data, str):
        if not region_data:
            return ["Unknown"]
        
        # Split by newlines and clean up
        regions = [r.strip() for r in region_data.split('\n') if r.strip()]
        
        # Clean up regions with parentheses
        cleaned_regions = []
        for region in regions:
            # Remove text in parentheses
            base_region = re.sub(r'\s*\([^)]*\)', '', region).strip()
            
            # Map to parent region if needed
            if base_region in REGION_MAPPING:
                mapped_region = REGION_MAPPING[base_region]
                if mapped_region not in cleaned_regions:
                    cleaned_regions.append(mapped_region)
            elif base_region in VALID_REGIONS:
                if base_region not in cleaned_regions:
                    cleaned_regions.append(base_region)
            else:
                # If not in mapping or valid regions, try to find a match
                for valid_region in VALID_REGIONS:
                    if valid_region.lower() in base_region.lower():
                        if valid_region not in cleaned_regions:
                            cleaned_regions.append(valid_region)
        
        return cleaned_regions if cleaned_regions else ["Unknown"]
    
    # If region_data is neither a string nor a list, return Unknown
    return ["Unknown"]

def update_champions_json():
    """Update species and region data in champions.json."""
    # Load the champions.json file
    try:
        with open("champions.json", "r") as f:
            champions_data = json.load(f)
    except FileNotFoundError:
        print("Error: champions.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: champions.json is not a valid JSON file.")
        return
    
    # Check if the file has the expected structure
    if "champions" not in champions_data:
        print("Error: champions.json does not have the expected structure.")
        return
    
    # Update each champion's species and region data
    updated_count = 0
    for champion in champions_data["champions"]:
        # Clean up species
        if "species" in champion:
            champion["species"] = clean_species(champion["species"])
        
        # Clean up region
        if "region" in champion:
            champion["region"] = clean_region(champion["region"])
        
        updated_count += 1
    
    # Save the updated data back to champions.json
    with open("champions.json", "w") as f:
        json.dump(champions_data, f, indent=2)
    
    print(f"Updated {updated_count} champions in champions.json")

if __name__ == "__main__":
    update_champions_json() 