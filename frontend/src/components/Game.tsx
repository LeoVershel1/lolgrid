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
  score: number;
  gameId: string;
  difficulty: number;
}

const Game: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [showAnswers, setShowAnswers] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isGuessing, setIsGuessing] = useState(false);
  const [difficulty, setDifficulty] = useState(0.5);

  const fetchNewGame = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/game?difficulty=${difficulty}`);
      const data = await response.json();
      setGameState({
        grid: data.grid,
        categories: data.categories,
        guessesRemaining: 9,
        isGameOver: false,
        score: 0,
        gameId: data.gameId,
        difficulty: data.difficulty
      });
    } catch (error) {
      console.error('Error fetching game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNewGame();
  }, [difficulty]);

  const handleGuess = async (row: number, col: number, champion: string) => {
    if (!gameState || isGuessing) return;

    setIsGuessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/guess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          row, 
          col, 
          champion,
          gameId: gameState.gameId 
        }),
      });

      const data = await response.json();
      setGameState(data);
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

  const handleDifficultyChange = (newDifficulty: number) => {
    setDifficulty(newDifficulty);
    setIsLoading(true);
  };

  if (isLoading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  if (!gameState) {
    return <div className="text-center p-4">Error loading game</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Difficulty:</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={difficulty}
          onChange={(e) => handleDifficultyChange(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="text-sm text-gray-600">
          Current difficulty: {difficulty.toFixed(1)}
        </div>
      </div>
      <ChampionGrid
        grid={gameState.grid}
        categories={gameState.categories}
        onGuess={handleGuess}
        showAnswers={showAnswers}
      />
      <div className="mt-4">
        <GameControls
          guessesRemaining={gameState.guessesRemaining}
          score={gameState.score}
          onGiveUp={handleGiveUp}
        />
      </div>
      {gameState.isGameOver && (
        <GameOver
          onPlayAgain={handlePlayAgain}
          onShowAnswers={() => setShowAnswers(!showAnswers)}
          showAnswers={showAnswers}
          score={gameState.score}
          difficulty={gameState.difficulty}
        />
      )}
    </div>
  );
};

export default Game; 