"use client";

import React, { useState } from 'react';
import { GridCell } from '../types/index';
import { CHAMPION_ICONS_URL } from '../config';
import ChampionSelector from './ChampionSelector';

export interface ChampionCellProps {
  guessedChampion: string | null;
  correctChampion: string | null;
  isCorrect: boolean;
  onGuess: (champion: string) => void;
}

const ChampionCell: React.FC<ChampionCellProps> = ({ guessedChampion, correctChampion, isCorrect, onGuess }) => {
  const [isSelectorOpen, setIsSelectorOpen] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSelectorOpen(true);
  };

  const handleChampionSelect = (champion: string) => {
    onGuess(champion);
    setIsSelectorOpen(false);
  };

  const handleClose = () => {
    setIsSelectorOpen(false);
  };

  const getCellStyle = () => {
    if (!guessedChampion) return 'bg-white hover:bg-gray-50';
    if (isCorrect) return 'bg-green-50';
    return 'bg-red-50';
  };

  return (
    <div className="relative">
      <div
        className={`relative w-full h-full min-h-[180px] rounded-lg cursor-pointer transition-colors duration-200 ${
          getCellStyle()
        }`}
        onClick={handleClick}
      >
        {guessedChampion ? (
          <div className="flex flex-col items-center justify-center h-full">
            <img
              src={`${CHAMPION_ICONS_URL}/${guessedChampion}.png`}
              alt={guessedChampion}
              className="w-20 h-20 rounded-full"
              onError={(e) => {
                // Fallback if image fails to load
                (e.target as HTMLImageElement).src = '/placeholder-champion.png';
              }}
            />
            <span className="text-sm mt-2 font-medium text-gray-700">{guessedChampion}</span>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <span className="text-gray-400 text-center p-2">Click to guess</span>
          </div>
        )}
        {correctChampion && (
          <div className="absolute inset-0 flex items-center justify-center bg-green-50 bg-opacity-50">
            <div className="text-center">
              <img
                src={`${CHAMPION_ICONS_URL}/${correctChampion}.png`}
                alt={correctChampion}
                className="w-20 h-20 rounded-full mx-auto"
                onError={(e) => {
                  // Fallback if image fails to load
                  (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                }}
              />
              <span className="text-sm mt-2 block font-medium text-gray-700">{correctChampion}</span>
            </div>
          </div>
        )}
      </div>
      {isSelectorOpen && (
        <div className="absolute inset-0 z-50" onClick={(e) => e.stopPropagation()}>
          <ChampionSelector
            onSelect={handleChampionSelect}
            onClose={handleClose}
          />
        </div>
      )}
    </div>
  );
};

export default ChampionCell; 