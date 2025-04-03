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

export async function POST(request: Request) {
  try {
    const { champion, categories } = await request.json();

    // Read champions data
    const championsPath = path.join(process.cwd(), 'champions.json');
    const championsContent = fs.readFileSync(championsPath, 'utf8');
    const champions: { [key: string]: Champion } = JSON.parse(championsContent);

    // Get the champion data
    const championData = champions[champion];
    if (!championData) {
      return NextResponse.json({ isValid: false });
    }

    // Check if the champion has abilities that match both categories
    const hasRowCategory = Object.values(championData.abilities).some(ability =>
      ability.flags.includes(categories[0])
    );

    const hasColCategory = Object.values(championData.abilities).some(ability =>
      ability.flags.includes(categories[1])
    );

    return NextResponse.json({
      isValid: hasRowCategory && hasColCategory
    });
  } catch (error) {
    console.error('Error verifying champion:', error);
    return NextResponse.json(
      { error: 'Failed to verify champion' },
      { status: 500 }
    );
  }
} 