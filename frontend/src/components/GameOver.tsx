"use client";

import React from 'react';

interface GameOverProps {
  onPlayAgain: () => void;
  onShowAnswers: () => void;
  showAnswers: boolean;
  score: number;
  difficulty: number;
}

const GameOver: React.FC<GameOverProps> = ({
  onPlayAgain,
  onShowAnswers,
  showAnswers,
  score,
  difficulty
}) => {
  return (
    <div className="mt-4 p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-2">Game Over!</h2>
      <div className="mb-4">
        <p className="text-gray-600">Final Score: {score}/9</p>
        <p className="text-gray-600">Difficulty: {difficulty.toFixed(1)}</p>
      </div>
      <div className="flex justify-center space-x-4">
        <button
          onClick={onPlayAgain}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Play Again
        </button>
        <button
          onClick={onShowAnswers}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
        >
          {showAnswers ? 'Hide Answers' : 'Show Answers'}
        </button>
      </div>
    </div>
  );
};

export default GameOver; 