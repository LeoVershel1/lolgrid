import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

interface AbilityQuery {
  slot: 'passive' | 'q' | 'w' | 'e' | 'r' | 'any';
  flags: string[];
  requiredCount?: number;
}

function checkAbilityFlags(ability: any, requiredFlags: string[]): boolean {
  if (!ability || !ability.flags) return false;
  return requiredFlags.every(flag => ability.flags[flag] === true);
}

function checkChampionAbilities(champion: any, query: AbilityQuery): boolean {
  if (!champion || !champion.abilities) return false;

  const abilities = champion.abilities;
  let matchingFlags = 0;

  if (query.slot === 'any') {
    // Check all abilities
    ['passive', 'q', 'w', 'e', 'r'].forEach(slot => {
      if (abilities[slot] && checkAbilityFlags(abilities[slot], query.flags)) {
        matchingFlags++;
      }
    });
  } else {
    // Check specific ability slot
    if (abilities[query.slot] && checkAbilityFlags(abilities[query.slot], query.flags)) {
      matchingFlags++;
    }
  }

  return matchingFlags >= (query.requiredCount || 1);
}

export async function POST(request: Request) {
  try {
    const query: AbilityQuery = await request.json();
    
    // Read champions data
    const championsPath = path.join(process.cwd(), 'champions.json');
    const championsData = JSON.parse(fs.readFileSync(championsPath, 'utf8'));
    
    // Find matching champions
    const matchingChampions = championsData.champions
      .filter((champion: any) => checkChampionAbilities(champion, query))
      .map((champion: any) => champion.name);

    return NextResponse.json({ champions: matchingChampions });
  } catch (error) {
    console.error('Error querying champions:', error);
    return NextResponse.json({ error: 'Failed to query champions' }, { status: 500 });
  }
} 