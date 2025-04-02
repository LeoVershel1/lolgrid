# LoLGrid

A League of Legends themed grid game inspired by games like Pokedle and NBA Grid.

## Description

LoLGrid is a daily puzzle game where players need to find League of Legends champions that match pairs of categories. The game presents a 3x3 grid where each row and column represents a different category (e.g., region, role, species, etc.). Players must guess champions that fit both the row and column categories for each cell.

## Features

- 3x3 grid with different category combinations each game
- Multiple possible categories including:
  - Region (Ionia, Demacia, Piltover, etc.)
  - Role (Top, Mid, Support, etc.)
  - Resource Type (Mana, Energy, etc.)
  - Species (Yordle, Human, Void-being, etc.)
  - Primary Damage Type (AD, AP, Hybrid)
  - Range Type (Melee, Short Range, Long Range)
  - Release Season
  - And more!
- Visual feedback for correct and incorrect guesses
- Post-game analysis showing all possible answers

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Generation

The game uses champion data from multiple sources:
- Riot Games Data Dragon API
- League of Legends Wiki
- Manual verification for certain attributes

To update the champion data:
```bash
python3 generate_champion_data.py
```

## Project Structure

- `generate_champion_data.py`: Script to fetch and compile champion data
- `champions.json`: Generated champion data used by the game
- `requirements.txt`: Python dependencies

## Development Status

Current development is focused on:
1. Data collection and verification
2. Grid generation logic
3. User interface implementation

## Contributing

Feel free to contribute by:
1. Reporting bugs
2. Suggesting new features
3. Submitting pull requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by [Pokedle](https://pokedle.net/) and [NBA Grid](https://www.nbagrids.com/)
- Champion data from [Riot Games Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon) and [League of Legends Wiki](https://leagueoflegends.fandom.com/) 