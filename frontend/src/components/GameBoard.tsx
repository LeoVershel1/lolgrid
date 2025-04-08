'use client';

import { useState, useEffect } from 'react';
import ChampionSelector from './ChampionSelector';
import { API_URL } from '../config';

interface GameBoardProps {
  categories: {
    rows: string[];
    cols: string[];
  };
}

interface Cell {
  row: number;
  col: number;
  champion: string | null;
  isCorrect: boolean | null;
}

interface ValidChampion {
  name: string;
  icon: string;
}

export default function GameBoard({ categories }: GameBoardProps) {
  const [cells, setCells] = useState<Cell[]>(
    Array.from({ length: 9 }, (_, index) => ({
      row: Math.floor(index / 3),
      col: index % 3,
      champion: null,
      isCorrect: null
    }))
  );
  const [showSelector, setShowSelector] = useState(false);
  const [activeCell, setActiveCell] = useState<Cell | null>(null);
  const [solvedCount, setSolvedCount] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [showValidChampions, setShowValidChampions] = useState(false);
  const [validChampions, setValidChampions] = useState<ValidChampion[]>([]);
  const [selectedCell, setSelectedCell] = useState<Cell | null>(null);

  useEffect(() => {
    // Check if the game is complete
    if (cells.every(cell => cell.champion !== null)) {
      setIsComplete(true);
    }
  }, [cells]);

  const handleCellClick = (cell: Cell) => {
    if (isComplete) {
      // Show valid champions for the cell
      setSelectedCell(cell);
      setShowValidChampions(true);
      fetchValidChampions(cell);
    } else if (!cell.champion) {
      setActiveCell(cell);
      setShowSelector(true);
    }
  };

  const fetchValidChampions = async (cell: Cell) => {
    try {
      const response = await fetch(`${API_URL}/api/valid-champions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rowCategory: categories.rows[cell.row],
          colCategory: categories.cols[cell.col]
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch valid champions');
      const data = await response.json();
      setValidChampions(data.champions);
    } catch (error) {
      console.error('Error fetching valid champions:', error);
    }
  };

  const handleChampionSelect = async (champion: string) => {
    if (!activeCell) return;

    try {
      const response = await fetch(`${API_URL}/api/daily/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          row: activeCell.row,
          col: activeCell.col,
          champion
        }),
      });

      if (!response.ok) throw new Error('Failed to verify champion');
      const data = await response.json();

      // Update the cell with the selected champion and verification result
      setCells(prevCells => 
        prevCells.map(cell => 
          cell.row === activeCell.row && cell.col === activeCell.col
            ? { ...cell, champion, isCorrect: data.isCorrect }
            : cell
        )
      );

      if (data.isCorrect) {
        setSolvedCount(prev => prev + 1);
      }

      setShowSelector(false);
      setActiveCell(null);
    } catch (error) {
      console.error('Error verifying champion:', error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Column categories */}
      <div className="grid grid-cols-4 gap-4">
        <div className="h-12" /> {/* Empty cell for alignment */}
        <div className="h-12 flex items-center justify-center text-center font-medium">
          {categories.cols[0]}
        </div>
        <div className="h-12 flex items-center justify-center text-center font-medium">
          {categories.cols[1]}
        </div>
        <div className="h-12 flex items-center justify-center text-center font-medium">
          {categories.cols[2]}
        </div>
      </div>

      {/* Grid with row categories */}
      <div className="grid grid-cols-4 gap-4">
        {/* Row categories */}
        <div className="flex flex-col justify-between">
          <div className="aspect-square flex items-center justify-center text-center font-medium">
            {categories.rows[0]}
          </div>
          <div className="aspect-square flex items-center justify-center text-center font-medium">
            {categories.rows[1]}
          </div>
          <div className="aspect-square flex items-center justify-center text-center font-medium">
            {categories.rows[2]}
          </div>
        </div>

        {/* Grid cells */}
        <div className="col-span-3 grid grid-cols-3 gap-4">
          {cells.map((cell, index) => (
            <div
              key={index}
              className={`
                aspect-square border-2 rounded-lg p-4 cursor-pointer relative
                ${cell.isCorrect === true ? 'border-green-500 bg-green-50' : ''}
                ${cell.isCorrect === false ? 'border-red-500 bg-red-50' : ''}
                ${!cell.champion ? 'border-gray-200 hover:border-blue-500' : ''}
                ${isComplete && selectedCell?.row === cell.row && selectedCell?.col === cell.col ? 'border-blue-500 bg-blue-50' : ''}
              `}
              onClick={() => handleCellClick(cell)}
            >
              <div className="h-full flex flex-col justify-center items-center text-center">
                {cell.champion ? (
                  <div className="flex flex-col items-center">
                    <img
                      src={`${API_URL}/champion_icons/${encodeURIComponent(cell.champion)}.png`}
                      alt={cell.champion}
                      className="w-12 h-12 rounded-full mb-2"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                      }}
                    />
                    <span className="text-sm font-medium">{cell.champion}</span>
                  </div>
                ) : (
                  <div className="text-gray-400">Click to guess</div>
                )}
              </div>
              
              {/* Champion selector dropdown */}
              {showSelector && activeCell?.row === cell.row && activeCell?.col === cell.col && (
                <div className="absolute top-0 left-0 z-10">
                  <ChampionSelector
                    onSelect={handleChampionSelect}
                    onClose={() => {
                      setShowSelector(false);
                      setActiveCell(null);
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="text-center text-sm text-gray-600">
        Solved: {solvedCount}/9
      </div>

      {isComplete && (
        <div className="text-center text-lg font-medium text-green-600">
          Game Complete! Click any cell to see valid champions.
        </div>
      )}

      {/* Valid champions display */}
      {showValidChampions && selectedCell && (
        <div className="mt-4">
          <h3 className="text-lg font-medium mb-2">Valid Champions for this Cell:</h3>
          <div className="grid grid-cols-4 gap-2">
            {validChampions.map((champion) => (
              <div key={champion.name} className="flex flex-col items-center">
                <img
                  src={champion.icon}
                  alt={champion.name}
                  className="w-12 h-12 rounded-full"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                  }}
                />
                <span className="text-xs mt-1">{champion.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 