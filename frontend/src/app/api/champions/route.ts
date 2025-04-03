import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const championsPath = path.join(process.cwd(), 'champions.json');
    const championsContent = fs.readFileSync(championsPath, 'utf8');
    const champions = JSON.parse(championsContent);

    return NextResponse.json({
      champions: Object.keys(champions)
    });
  } catch (error) {
    console.error('Error fetching champions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch champions' },
      { status: 500 }
    );
  }
} 