import { NextResponse } from 'next/server';
import { GameState } from '@/types/game';

export async function POST(request: Request) {
  try {
    const { row, col, champion } = await request.json();

    // TODO: Implement actual game logic
    // For now, return a mock response
    const mockGameState: GameState = {
      grid: Array(3).fill(null).map(() =>
        Array(3).fill(null).map(() => ({
          xCategory: 'Region',
          yCategory: 'Role',
          correctChampions: ['Ahri', 'Lux', 'Zed'],
          guessedChampion: undefined,
          isCorrect: undefined,
        }))
      ),
      categories: {
        xAxis: [
          { name: 'Region', values: ['Ionia', 'Demacia', 'Noxus'] },
          { name: 'Role', values: ['Mid', 'Support', 'Top'] },
          { name: 'Resource', values: ['Mana', 'Energy', 'Rage'] },
        ],
        yAxis: [
          { name: 'Species', values: ['Human', 'Yordle', 'Void-being'] },
          { name: 'Damage Type', values: ['AP', 'AD', 'Hybrid'] },
          { name: 'Range', values: ['Melee', 'Ranged', 'Mixed'] },
        ],
      },
      guessesRemaining: 8,
      isGameOver: false,
      score: 1,
    };

    // Update the guessed cell
    mockGameState.grid[row][col] = {
      ...mockGameState.grid[row][col],
      guessedChampion: champion,
      isCorrect: true, // This would be determined by actual game logic
    };

    return NextResponse.json(mockGameState);
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
} 