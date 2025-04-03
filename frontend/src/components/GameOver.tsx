"use client";

import React from 'react';

interface GameOverProps {
  onPlayAgain: () => void;
  onShowAnswers: () => void;
  showAnswers: boolean;
}

const GameOver: React.FC<GameOverProps> = ({ onPlayAgain, onShowAnswers, showAnswers }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4">Game Over!</h2>
        <div className="space-y-4">
          <button
            onClick={onPlayAgain}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Play Again
          </button>
          <button
            onClick={onShowAnswers}
            className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
          >
            {showAnswers ? 'Hide Answers' : 'Show Answers'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GameOver; 