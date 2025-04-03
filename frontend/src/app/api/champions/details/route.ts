import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read the champions.json file from the root of the frontend directory
    const championsPath = path.join(process.cwd(), 'champions.json');
    console.log('Reading champions from:', championsPath);
    
    const data = JSON.parse(fs.readFileSync(championsPath, 'utf8'));
    console.log('Data type:', typeof data);
    console.log('Has champions key?', 'champions' in data);
    
    // Extract the champions array from the data
    const championsData = data.champions || [];
    
    // Return the champions array
    return NextResponse.json(championsData);
  } catch (error) {
    console.error('Error reading champions data:', error);
    return NextResponse.json({ error: 'Failed to load champions data' }, { status: 500 });
  }
} 