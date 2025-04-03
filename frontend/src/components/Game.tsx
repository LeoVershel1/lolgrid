"use client";

import React, { useState, useEffect } from 'react';
import ChampionGrid from './ChampionGrid';
import GameControls from './GameControls';
import GameOver from './GameOver';
import { GridCell, Category } from '../types/index';
import { API_BASE_URL } from '../config';

interface GameState {
  grid: GridCell[][];
  categories: {
    xAxis: Category[];
    yAxis: Category[];
  };
  guessesRemaining: number;
  isGameOver: boolean;
}

const Game: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [showAnswers, setShowAnswers] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isGuessing, setIsGuessing] = useState(false);

  const fetchNewGame = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/game`);
      const data = await response.json();
      setGameState({
        grid: data.grid,
        categories: data.categories,
        guessesRemaining: 9,
        isGameOver: false,
      });
    } catch (error) {
      console.error('Error fetching game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNewGame();
  }, []);

  const handleGuess = async (row: number, col: number, champion: string) => {
    if (!gameState || isGuessing) return;

    setIsGuessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/guess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ row, col, champion }),
      });

      const data = await response.json();
      const newGrid = [...gameState.grid];
      newGrid[row][col] = {
        ...newGrid[row][col],
        guessedChampion: champion,
        correctChampion: data.correctChampion,
        isCorrect: champion === data.correctChampion,
      };

      setGameState({
        ...gameState,
        grid: newGrid,
        guessesRemaining: gameState.guessesRemaining - 1,
        isGameOver: gameState.guessesRemaining - 1 === 0,
      });
    } catch (error) {
      console.error('Error making guess:', error);
    } finally {
      setIsGuessing(false);
    }
  };

  const handleGiveUp = () => {
    if (!gameState) return;
    setGameState({ ...gameState, isGameOver: true });
  };

  const handlePlayAgain = () => {
    setIsLoading(true);
    fetchNewGame();
    setShowAnswers(false);
  };

  if (isLoading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  if (!gameState) {
    return <div className="text-center p-4">Error loading game</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <ChampionGrid
        grid={gameState.grid}
        categories={gameState.categories}
        onGuess={handleGuess}
        showAnswers={showAnswers}
      />
      <div className="mt-4">
        <GameControls
          guessesRemaining={gameState.guessesRemaining}
          onGiveUp={handleGiveUp}
        />
      </div>
      {gameState.isGameOver && (
        <GameOver
          onPlayAgain={handlePlayAgain}
          onShowAnswers={() => setShowAnswers(!showAnswers)}
          showAnswers={showAnswers}
        />
      )}
    </div>
  );
};

export default Game; 