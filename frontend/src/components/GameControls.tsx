"use client";

import React from 'react';

interface GameControlsProps {
  guessesRemaining: number;
  onGiveUp: () => void;
}

const GameControls: React.FC<GameControlsProps> = ({ guessesRemaining, onGiveUp }) => {
  return (
    <div className="flex justify-between items-center p-4 bg-white rounded-lg shadow">
      <div className="text-lg font-semibold">
        Guesses remaining: {guessesRemaining}
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