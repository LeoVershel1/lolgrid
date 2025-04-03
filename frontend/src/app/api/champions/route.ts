import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read the champions.json file from the root of the frontend directory
    const championsPath = path.join(process.cwd(), 'champions.json');
    const data = JSON.parse(fs.readFileSync(championsPath, 'utf8'));
    
    // Extract the champions array and get just the names
    const championsData = data.champions || [];
    const championNames = championsData.map((champion: any) => champion.name);
    
    return NextResponse.json(championNames);
  } catch (error) {
    console.error('Error reading champions data:', error);
    return NextResponse.json({ error: 'Failed to load champions data' }, { status: 500 });
  }
} 