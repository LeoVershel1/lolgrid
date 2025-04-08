# League of Legends Grid Game

A web-based game where players need to identify League of Legends champions that match specific category combinations.

## Features

- 3x3 grid with category combinations
- Difficulty-based grid generation
- Category weighting system
- Comprehensive category analysis tools
- Champion icon display
- Score tracking
- Game state management

## Project Structure

- `app.py` - Flask backend server with grid generation logic
- `categories.py` - Category definitions and matching logic
- `grid_generator.py` - Grid generation with difficulty scoring
- `analyze_categories.py` - Utility for analyzing category difficulties
- `champions.json` - Champion data
- `champion_icons.json` - Champion icon mappings
- `frontend/` - Next.js frontend application

## Grid Generation System

The grid generation system has been improved with:

1. Difficulty Scoring
   - Each category has a difficulty score based on the number of matching champions
   - Category pairs are scored based on the intersection of matching champions
   - Grid difficulty is calculated as the average of all cell difficulties

2. Category Weighting
   - Categories are weighted based on recency of use
   - Harder categories are given higher weights to ensure variety
   - Recently used categories are temporarily excluded

3. Grid Validation
   - Ensures each cell has at least one valid champion
   - Maintains target difficulty while generating valid grids
   - Prevents impossible combinations

## Running the Application

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python app.py
```

3. In a new terminal, start the frontend:
```bash
cd frontend
npm install
npm run dev
```

4. Open http://localhost:3000 in your browser

## API Endpoints

- `GET /api/game?difficulty=0.5` - Get a new game state with specified difficulty
- `POST /api/guess` - Submit a champion guess for a cell
- `GET /api/champions` - Get list of all champions
- `GET /champion_icons/<filename>` - Get champion icon image

## Difficulty Levels

- 0.0 - Easiest (many champions match each category)
- 0.5 - Medium (balanced difficulty)
- 1.0 - Hardest (few champions match each category)

## Future Improvements

- Add more category types
- Implement user accounts and high scores
- Add multiplayer support
- Improve champion icon loading
- Add more game modes 