"use client";

import React from 'react';

interface GameControlsProps {
  guessesRemaining: number;
  score: number;
  onGiveUp: () => void;
}

const GameControls: React.FC<GameControlsProps> = ({ guessesRemaining, score, onGiveUp }) => {
  return (
    <div className="flex justify-between items-center">
      <div className="text-sm text-gray-600">
        Guesses remaining: {guessesRemaining}
      </div>
      <div className="text-sm text-gray-600">
        Score: {score}
      </div>
      <button
        onClick={onGiveUp}
        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
      >
        Give Up
      </button>
    </div>
  );
};

export default GameControls; 