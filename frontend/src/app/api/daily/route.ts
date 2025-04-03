import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

interface Champion {
  name: string;
  abilities: {
    [key: string]: {
      flags: string[];
    };
  };
}

function shuffleArray<T>(array: T[]): T[] {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

function hasValidSolution(categories: string[], champions: Champion[]): boolean {
  // Check if there are champions that satisfy each category
  for (const category of categories) {
    const hasChampion = champions.some(champion => {
      return Object.values(champion.abilities).some(ability => 
        ability.flags.includes(category)
      );
    });
    if (!hasChampion) return false;
  }
  return true;
}

export async function GET() {
  try {
    // Read categories.py
    const categoriesPath = path.join(process.cwd(), 'categories.py');
    const categoriesContent = fs.readFileSync(categoriesPath, 'utf8');
    
    // Read champions.json
    const championsPath = path.join(process.cwd(), 'champions.json');
    const championsContent = fs.readFileSync(championsPath, 'utf8');
    const champions: Champion[] = JSON.parse(championsContent);

    // Parse categories from Python file
    const allCategories: string[] = [];
    const lines = categoriesContent.split('\n');
    for (const line of lines) {
      if (line.trim().startsWith('"') && line.trim().endsWith('"')) {
        const category = line.trim().slice(1, -1);
        allCategories.push(category);
      }
    }

    // Try to find 6 categories that have valid solutions
    let validCategories: string[] = [];
    let attempts = 0;
    const maxAttempts = 100;

    while (attempts < maxAttempts) {
      const shuffledCategories = shuffleArray(allCategories);
      const selectedCategories = shuffledCategories.slice(0, 6);
      
      if (hasValidSolution(selectedCategories, champions)) {
        validCategories = selectedCategories;
        break;
      }
      attempts++;
    }

    if (validCategories.length === 0) {
      return NextResponse.json(
        { error: 'Could not find valid categories' },
        { status: 500 }
      );
    }

    // Split into rows and columns
    const rows = validCategories.slice(0, 3);
    const cols = validCategories.slice(3);

    return NextResponse.json({ rows, cols });
  } catch (error) {
    console.error('Error generating daily challenge:', error);
    return NextResponse.json(
      { error: 'Failed to generate daily challenge' },
      { status: 500 }
    );
  }
} 