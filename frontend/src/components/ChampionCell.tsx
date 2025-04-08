"use client";

import React, { useState } from 'react';
import { GridCell } from '../types/index';
import { API_URL } from '../config';
import ChampionSelector from './ChampionSelector';

// Champion ID mapping for special characters
const CHAMPION_ID_MAPPING: Record<string, string> = {
  "Aurelion Sol": "AurelionSol",
  "Bel'Veth": "Belveth",
  "Cho'Gath": "Chogath",
  "Dr. Mundo": "DrMundo",
  "Jarvan IV": "JarvanIV",
  "Kai'Sa": "Kaisa",
  "K'Sante": "KSante",
  "Kha'Zix": "Khazix",
  "Kog'Maw": "KogMaw",
  "Lee Sin": "LeeSin",
  "Master Yi": "MasterYi",
  "Miss Fortune": "MissFortune",
  "Nunu & Willump": "Nunu",
  "Rek'Sai": "RekSai",
  "Renata Glasc": "Renata",
  "Tahm Kench": "TahmKench",
  "Twisted Fate": "TwistedFate",
  "Vel'Koz": "Velkoz",
  "Xin Zhao": "XinZhao"
};

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

  // Get the champion ID for the icon URL
  const getChampionId = (championName: string): string => {
    // Remove .png extension if it exists
    const cleanName = championName.replace('.png', '');
    return CHAMPION_ID_MAPPING[cleanName] || cleanName;
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
            <div className="flex flex-col items-center">
              <img
                src={`${API_URL}/champion_icons/${encodeURIComponent(getChampionId(cell.guessedChampion))}`}
                alt={cell.guessedChampion}
                className="w-12 h-12 rounded-full mb-2"
                onError={(e) => {
                  console.error(`Failed to load icon for ${cell.guessedChampion}`);
                  (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                }}
              />
              <span className="text-sm font-medium">{cell.guessedChampion}</span>
            </div>
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
                src={`${API_URL}/champion_icons/${encodeURIComponent(getChampionId(cell.correctChampions[0]))}`}
                alt={cell.correctChampions[0]}
                className="w-20 h-20 rounded-full mx-auto"
                onError={(e) => {
                  console.error(`Failed to load icon for ${cell.correctChampions[0]}`);
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