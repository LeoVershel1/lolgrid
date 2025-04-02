"""
This file handles fetching and organizing champion icons from the Data Dragon API.
"""

import json
import os
import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageEnhance
import io

# Create a directory for storing champion icons if it doesn't exist
ICONS_DIR = Path("static/champion_icons")
ICONS_DIR.mkdir(parents=True, exist_ok=True)

# Define standard icon sizes
ICON_SIZES = {
    "small": (32, 32),
    "medium": (64, 64),
    "large": (96, 96),
    "xlarge": (128, 128)
}

# Define tint colors (in RGB)
TINT_COLORS = {
    "correct": (0, 255, 0),  # Green
    "incorrect": (255, 0, 0),  # Red
    "default": (255, 255, 255)  # White (no tint)
}

def resize_icon(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """Resize an icon to the specified dimensions while maintaining aspect ratio."""
    return image.resize(size, Image.Resampling.LANCZOS)

def apply_tint(image: Image.Image, tint_color: Tuple[int, int, int], strength: float = 0.5) -> Image.Image:
    """
    Apply a tint color to the image.
    strength: 0.0 to 1.0, where 1.0 is full tint and 0.0 is no tint
    """
    # Convert image to RGBA if it isn't already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a new image with the tint color
    tint = Image.new('RGBA', image.size, tint_color + (255,))
    
    # Blend the tint with the original image
    return Image.blend(image, tint, strength)

def process_icon(icon_path: str, size: str = "medium", tint: str = "default", tint_strength: float = 0.5) -> Image.Image:
    """
    Process an icon with the specified size and tint.
    Returns a PIL Image object.
    """
    # Open the original icon
    with Image.open(icon_path) as img:
        # Resize the image
        if size in ICON_SIZES:
            img = resize_icon(img, ICON_SIZES[size])
        
        # Apply tint if specified
        if tint in TINT_COLORS:
            img = apply_tint(img, TINT_COLORS[tint], tint_strength)
        
        return img

def save_processed_icon(icon_path: str, output_path: str, size: str = "medium", tint: str = "default", tint_strength: float = 0.5) -> None:
    """
    Process an icon and save it to the specified output path.
    """
    img = process_icon(icon_path, size, tint, tint_strength)
    img.save(output_path, "PNG")

async def fetch_champion_icons(session: aiohttp.ClientSession, version: str = "15.7.1") -> Dict[str, str]:
    """
    Fetch champion icons from Data Dragon API and save them locally.
    Returns a dictionary mapping champion names to their icon paths.
    """
    # First, get the champion data to get all champion IDs
    champion_data_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    async with session.get(champion_data_url) as response:
        champion_data = await response.json()
    
    # Create a mapping of champion names to their icon paths
    champion_icons = {}
    
    # Download icons for each champion
    for champion_id, champion_info in champion_data["data"].items():
        champion_name = champion_info["name"]
        icon_filename = f"{champion_id}.png"
        icon_path = ICONS_DIR / icon_filename
        
        # Skip if we already have the icon
        if icon_path.exists():
            champion_icons[champion_name] = str(icon_path)
            continue
        
        # Download the icon
        icon_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{icon_filename}"
        try:
            async with session.get(icon_url) as response:
                if response.status == 200:
                    icon_data = await response.read()
                    with open(icon_path, "wb") as f:
                        f.write(icon_data)
                    champion_icons[champion_name] = str(icon_path)
                else:
                    print(f"Failed to download icon for {champion_name}: {response.status}")
        except Exception as e:
            print(f"Error downloading icon for {champion_name}: {e}")
    
    return champion_icons

def generate_processed_icons(champion_icons: Dict[str, str]) -> None:
    """
    Generate processed versions of all champion icons with different sizes and tints.
    """
    processed_dir = ICONS_DIR / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    for champion_name, icon_path in champion_icons.items():
        # Generate different sizes
        for size in ICON_SIZES.keys():
            output_path = processed_dir / f"{champion_name}_{size}.png"
            save_processed_icon(icon_path, str(output_path), size=size)
        
        # Generate tinted versions
        for tint in ["correct", "incorrect"]:
            output_path = processed_dir / f"{champion_name}_{tint}.png"
            save_processed_icon(icon_path, str(output_path), tint=tint)

async def main():
    """Main function to fetch and save champion icons."""
    async with aiohttp.ClientSession() as session:
        champion_icons = await fetch_champion_icons(session)
        
        # Save the mapping to a JSON file
        with open("champion_icons.json", "w") as f:
            json.dump(champion_icons, f, indent=2)
        
        # Generate processed versions of all icons
        generate_processed_icons(champion_icons)
        
        print(f"Successfully downloaded {len(champion_icons)} champion icons")
        print("Icon paths have been saved to champion_icons.json")
        print("Processed icons have been generated in static/champion_icons/processed/")

if __name__ == "__main__":
    asyncio.run(main()) 