export type AbilitySlot = 'passive' | 'q' | 'w' | 'e' | 'r' | 'any';

export interface AbilityQuery {
  slot: AbilitySlot;
  flags: string[];
  requiredCount?: number;
}

export async function queryChampions(query: AbilityQuery): Promise<string[]> {
  try {
    const response = await fetch('/api/champions/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
    });

    if (!response.ok) {
      throw new Error('Failed to query champions');
    }

    const data = await response.json();
    return data.champions;
  } catch (error) {
    console.error('Error querying champions:', error);
    return [];
  }
}

// Helper function to find champions that match both queries
export async function findChampionsMatchingBothQueries(query1: AbilityQuery, query2: AbilityQuery): Promise<string[]> {
  const [champions1, champions2] = await Promise.all([
    queryChampions(query1),
    queryChampions(query2),
  ]);

  // Return champions that appear in both lists
  return champions1.filter(champion => champions2.includes(champion));
} 