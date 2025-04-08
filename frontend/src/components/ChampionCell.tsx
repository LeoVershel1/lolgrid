"use client";

import React, { useState } from 'react';
import { GridCell } from '../types/index';
import { CHAMPION_ICONS_URL } from '../config';
import ChampionSelector from './ChampionSelector';

interface ChampionCellProps {
  cell: GridCell;
  onGuess: (champion: string) => void;
  showAnswers: boolean;
}

const ChampionCell: React.FC<ChampionCellProps> = ({ cell, onGuess, showAnswers }) => {
  const [showSelector, setShowSelector] = useState(false);

  const handleClick = () => {
    if (!cell.guessedChampion) {
      setShowSelector(true);
    }
  };

  const getCellStyle = () => {
    if (!cell.guessedChampion) return 'bg-white hover:bg-gray-50';
    if (cell.isCorrect) return 'bg-green-50';
    return 'bg-red-50';
  };

  return (
    <div className="relative">
      <div
        className={`
          aspect-square border-2 rounded-lg p-4 cursor-pointer relative
          ${cell.isCorrect === true ? 'border-green-500 bg-green-50' : ''}
          ${cell.isCorrect === false ? 'border-red-500 bg-red-50' : ''}
          ${!cell.guessedChampion ? 'border-gray-200 hover:border-blue-500' : ''}
        `}
        onClick={handleClick}
      >
        <div className="h-full flex flex-col justify-center items-center text-center">
          {cell.guessedChampion ? (
            <div className="font-medium">{cell.guessedChampion}</div>
          ) : showAnswers ? (
            <div className="text-sm text-gray-600">
              {cell.correctChampions.slice(0, 3).join(', ')}
              {cell.correctChampions.length > 3 ? '...' : ''}
            </div>
          ) : (
            <div className="text-gray-400">Click to guess</div>
          )}
        </div>
        {cell.correctChampions.length > 0 && (
          <div className="absolute inset-0 flex items-center justify-center bg-green-50 bg-opacity-50">
            <div className="text-center">
              <img
                src={`${CHAMPION_ICONS_URL}/${cell.correctChampions[0]}.png`}
                alt={cell.correctChampions[0]}
                className="w-20 h-20 rounded-full mx-auto"
                onError={(e) => {
                  // Fallback if image fails to load
                  (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                }}
              />
              <span className="text-sm mt-2 block font-medium text-gray-700">{cell.correctChampions[0]}</span>
            </div>
          </div>
        )}
      </div>
      {showSelector && (
        <div className="absolute inset-0 z-50" onClick={(e) => e.stopPropagation()}>
          <ChampionSelector
            onSelect={(champion) => {
              onGuess(champion);
              setShowSelector(false);
            }}
            onClose={() => setShowSelector(false)}
          />
        </div>
      )}
    </div>
  );
};

export default ChampionCell; 