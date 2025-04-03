import { NextResponse } from 'next/server';
import { GameState } from '@/types/game';

// This would typically come from your backend service
const generateGameState = (): GameState => {
  // TODO: Implement game state generation logic
  // For now, return a mock game state
  return {
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
    guessesRemaining: 9,
    isGameOver: false,
    score: 0,
  };
};

export async function GET() {
  const gameState = generateGameState();
  return NextResponse.json(gameState);
} 