"use client";

import React, { useState, useEffect } from 'react';
import { GridCell } from '../types/index';
import { CHAMPION_ICONS_URL } from '../config';
import ChampionSelector from './ChampionSelector';

interface ChampionCellProps {
  cell: GridCell;
  isSelected: boolean;
  onSelect: () => void;
  onGuess: (champion: string) => void;
  showAnswers: boolean;
}

const ChampionCell: React.FC<ChampionCellProps> = ({
  cell,
  isSelected,
  onSelect,
  onGuess,
  showAnswers,
}) => {
  const [showSelector, setShowSelector] = useState(false);

  // Close selector when cell is deselected
  useEffect(() => {
    if (!isSelected) {
      setShowSelector(false);
    }
  }, [isSelected]);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!cell.guessedChampion && !showAnswers) {
      setShowSelector(true);
      onSelect();
    }
  };

  const handleGuess = (champion: string) => {
    onGuess(champion);
    setShowSelector(false);
  };

  const getCellStyle = () => {
    if (!cell.guessedChampion) return 'bg-white hover:bg-gray-50';
    if (cell.isCorrect) return 'bg-green-50';
    return 'bg-red-50';
  };

  return (
    <div
      className={`relative w-full h-full min-h-[180px] rounded-lg cursor-pointer transition-colors duration-200 ${
        getCellStyle()
      } ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      onClick={handleClick}
    >
      {cell?.guessedChampion ? (
        <div className="flex flex-col items-center justify-center h-full">
          <img
            src={`${CHAMPION_ICONS_URL}/${cell.guessedChampion}.png`}
            alt={cell.guessedChampion}
            className="w-20 h-20 rounded-full"
            onError={(e) => {
              // Fallback if image fails to load
              (e.target as HTMLImageElement).src = '/placeholder-champion.png';
            }}
          />
          <span className="text-sm mt-2 font-medium text-gray-700">{cell.guessedChampion}</span>
        </div>
      ) : (
        <div className="flex items-center justify-center h-full">
          <span className="text-gray-400 text-center p-2">Click to guess</span>
        </div>
      )}
      {showAnswers && cell?.correctChampion && (
        <div className="absolute inset-0 flex items-center justify-center bg-green-50 bg-opacity-50">
          <div className="text-center">
            <img
              src={`${CHAMPION_ICONS_URL}/${cell.correctChampion}.png`}
              alt={cell.correctChampion}
              className="w-20 h-20 rounded-full mx-auto"
              onError={(e) => {
                // Fallback if image fails to load
                (e.target as HTMLImageElement).src = '/placeholder-champion.png';
              }}
            />
            <span className="text-sm mt-2 block font-medium text-gray-700">{cell.correctChampion}</span>
          </div>
        </div>
      )}
      {showSelector && (
        <div className="absolute inset-0 z-50" onClick={(e) => e.stopPropagation()}>
          <ChampionSelector
            onSelect={handleGuess}
            onClose={() => setShowSelector(false)}
          />
        </div>
      )}
    </div>
  );
};

export default ChampionCell; 