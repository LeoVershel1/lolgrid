import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';

interface AbilityFlags {
  [key: string]: boolean;
}

interface Ability {
  name: string;
  description: string;
  flags: AbilityFlags;
}

interface Champion {
  name: string;
  region: string;
  role: string[];
  resource: string;
  species: string;
  primaryDamageType: string;
  range: number;
  baseMovespeed: number;
  releaseSeason: number;
  modelSize: number;
  skinLines: string[];
  abilities: {
    [key: string]: Ability;
  };
}

interface Champions {
  champions: Champion[];
}

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// Read champions data
const championsPath = path.join(__dirname, '../../champions.json');
console.log('Reading champions from:', championsPath);
const championsContent = fs.readFileSync(championsPath, 'utf8');
const champions: Champions = JSON.parse(championsContent);
console.log('Loaded champions:', champions.champions.map(c => c.name));
console.log('First champion data:', champions.champions[0]);

// Extract unique ability flags
const uniqueFlags = new Set<string>();
champions.champions.forEach(champion => {
  Object.values(champion.abilities).forEach(ability => {
    Object.keys(ability.flags).forEach(flag => {
      uniqueFlags.add(flag);
    });
  });
});
console.log('Available ability flags:', Array.from(uniqueFlags));

// Read categories
const categoriesPath = path.join(__dirname, '../../categories.py');
console.log('Reading categories from:', categoriesPath);
const categoriesContent = fs.readFileSync(categoriesPath, 'utf8');
const allCategories: string[] = [];
const lines = categoriesContent.split('\n');

let currentCategoryType = '';
for (const line of lines) {
  const trimmedLine = line.trim();
  
  // Skip empty lines and comments
  if (!trimmedLine || trimmedLine.startsWith('#')) continue;
  
  // Look for category type definitions
  if (trimmedLine.startsWith('def get_')) {
    currentCategoryType = trimmedLine.split('get_')[1].split('(')[0];
    continue;
  }
  
  // Look for category values
  if (trimmedLine.includes('"') && !trimmedLine.includes('def') && !trimmedLine.includes('return')) {
    const match = trimmedLine.match(/"([^"]+)"/);
    if (match && match[1]) {
      const category = match[1].trim();
      // Skip empty categories, structural elements, and category type names
      if (category && 
          !category.includes('Returns') && 
          !category.includes('function') &&
          !category.includes('category') &&
          category !== 'categories' &&
          category !== 'category_type' &&
          category !== 'category_value' &&
          // Skip category type names
          !['name', 'role', 'skins', 'location', 'description', 'resource', 'species', 'damage_type', 'range', 'model_size', 'releaseSeason', 'weapons'].includes(category)) {
        allCategories.push(category);
      }
    }
  }
}

// Remove duplicates and sort
const uniqueCategories = Array.from(new Set(allCategories)).sort();
console.log('Loaded categories:', uniqueCategories);

// Helper function to shuffle array
function shuffleArray<T>(array: T[]): T[] {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

// Helper function to check if a champion matches a category
function checkCategory(champion: Champion, category: string): boolean {
  // Check different types of categories
  if (category === champion.region) return true;
  if (champion.role.includes(category)) return true;
  if (champion.resource === category) return true;
  if (champion.species === category) return true;
  if (champion.primaryDamageType === category) return true;
  if (champion.skinLines.includes(category)) return true;
  
  // Check range categories
  if (category === 'Melee (< 250)' && champion.range < 250) return true;
  if (category === 'Short Range (250-499)' && champion.range >= 250 && champion.range < 500) return true;
  if (category === 'Long Range (500+)' && champion.range >= 500) return true;
  
  // Check model size categories
  if (category === 'Small (55-64)' && champion.modelSize >= 55 && champion.modelSize <= 64) return true;
  if (category === 'Large (80+)' && champion.modelSize >= 80) return true;
  
  // Check ability flags
  if (champion.abilities) {
    return Object.values(champion.abilities).some(ability => {
      const typedAbility = ability as Ability;
      if (!typedAbility || !typedAbility.flags) return false;
      
      // Convert category to a flag name format
      const flagName = category.toLowerCase()
        .replace(/\s+/g, '')
        .replace(/[^a-z0-9]/g, '');
      
      // Check if any flag matches the category
      return Object.keys(typedAbility.flags).some(flag => 
        flag.toLowerCase().includes(flagName) || 
        flagName.includes(flag.toLowerCase())
      );
    });
  }
  
  return false;
}

// Helper function to find valid champions for a category combination
function findValidChampions(rowCategory: string, colCategory: string): string[] {
  return champions.champions
    .filter(champion => checkCategory(champion, rowCategory) && checkCategory(champion, colCategory))
    .map(champion => champion.name);
}

// Helper function to check if categories have valid solutions
function hasValidSolution(categories: string[]): boolean {
  const rows = categories.slice(0, 3);
  const cols = categories.slice(3);

  // Check each cell in the grid
  for (const rowCategory of rows) {
    for (const colCategory of cols) {
      const validChampions = findValidChampions(rowCategory, colCategory);
      if (validChampions.length === 0) {
        console.log(`No valid champions found for row: ${rowCategory}, col: ${colCategory}`);
        return false;
      }
    }
  }

  return true;
}

// Get all champions
app.get('/api/champions', (req, res) => {
  res.json({
    champions: champions.champions.map(champion => ({
      name: champion.name,
      icon: `https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${champion.name.replace(/\s+/g, '')}.png`
    }))
  });
});

// Get daily challenge
app.get('/api/daily', (req, res) => {
  try {
    console.log('Generating daily challenge...');
    console.log('Available categories:', uniqueCategories);
    
    let validCategories: string[] = [];
    let attempts = 0;
    const maxAttempts = 100;

    while (attempts < maxAttempts) {
      // Shuffle and select 6 unique categories
      const shuffledCategories = shuffleArray([...uniqueCategories]);
      const selectedCategories = shuffledCategories.slice(0, 6);
      
      if (hasValidSolution(selectedCategories)) {
        validCategories = selectedCategories;
        console.log('Found valid categories:', validCategories);
        
        // Log valid champions for each cell
        const rows = validCategories.slice(0, 3);
        const cols = validCategories.slice(3);
        console.log('\nValid champions for each cell:');
        for (const rowCategory of rows) {
          for (const colCategory of cols) {
            const validChampions = findValidChampions(rowCategory, colCategory);
            console.log(`[${rowCategory}] x [${colCategory}]: ${validChampions.join(', ')}`);
          }
        }
        break;
      }
      attempts++;
    }

    if (validCategories.length === 0) {
      console.error('Could not find valid categories after', maxAttempts, 'attempts');
      return res.status(500).json({ error: 'Could not find valid categories' });
    }

    // Split into rows and columns
    const rows = validCategories.slice(0, 3);
    const cols = validCategories.slice(3);

    console.log('Sending response with rows:', rows, 'and cols:', cols);
    res.json({ rows, cols });
  } catch (error) {
    console.error('Error generating daily challenge:', error);
    res.status(500).json({ error: 'Failed to generate daily challenge' });
  }
});

// Verify champion guess
app.post('/api/query', (req, res) => {
  try {
    const { champion, categories } = req.body;

    // Get the champion data
    const championData = champions.champions.find(c => c.name === champion);
    if (!championData) {
      return res.json({ isValid: false });
    }

    // Check if the champion matches both categories
    const hasRowCategory = checkCategory(championData, categories[0]);
    const hasColCategory = checkCategory(championData, categories[1]);

    res.json({
      isValid: hasRowCategory && hasColCategory
    });
  } catch (error) {
    console.error('Error verifying champion:', error);
    res.status(500).json({ error: 'Failed to verify champion' });
  }
});

// Get valid champions for a cell
app.post('/api/valid-champions', (req, res) => {
  try {
    const { rowCategory, colCategory } = req.body;
    
    const validChampions = champions.champions
      .filter(champion => checkCategory(champion, rowCategory) && checkCategory(champion, colCategory))
      .map(champion => ({
        name: champion.name,
        icon: `https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${champion.name.replace(/\s+/g, '')}.png`
      }));

    res.json({ champions: validChampions });
  } catch (error) {
    console.error('Error getting valid champions:', error);
    res.status(500).json({ error: 'Failed to get valid champions' });
  }
});

app.listen(port, () => {
  console.log(`Backend server running at http://localhost:${port}`);
}); 