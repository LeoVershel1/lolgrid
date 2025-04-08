'use client';

import { useState, useEffect } from 'react';
import ChampionSelector from './ChampionSelector';
import { API_URL } from '../config';

interface GameBoardProps {
  categories: {
    rows: string[];
    cols: string[];
  };
  gameState: {
    gameId: string;
    grid: any[][];
  } | null;
  setGameState: (state: {gameId: string, grid: any[][]} | null) => void;
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

export default function GameBoard({ categories, gameState, setGameState }: GameBoardProps) {
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
  const [selectedCell, setSelectedCell] = useState<{row: number, col: number} | null>(null);
  const [showChampionSelector, setShowChampionSelector] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if the game is complete
    if (cells.every(cell => cell.champion !== null)) {
      setIsComplete(true);
    }
  }, [cells]);

  const handleCellClick = (cell: Cell) => {
    if (isComplete) {
      // Show valid champions for the cell
      setSelectedCell({ row: cell.row, col: cell.col });
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
    if (!activeCell || !gameState) return;

    try {
      const response = await fetch(`${API_URL}/api/guess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gameId: gameState.gameId,
          row: activeCell.row,
          col: activeCell.col,
          champion: champion
        }),
      });

      const data = await response.json();
      console.log('Guess response:', data); // Debug log

      if (data.error) {
        setError(data.error);
        return;
      }

      // Update the game state with the response
      setGameState({
        gameId: data.gameId,
        grid: data.grid
      });

      // Update the cells state directly
      const updatedCells = cells.map(cell => {
        if (cell.row === activeCell.row && cell.col === activeCell.col) {
          const gridCell = data.grid[cell.row][cell.col];
          console.log('Updating cell:', gridCell); // Debug log
          return {
            ...cell,
            champion: gridCell.guessedChampion,
            isCorrect: gridCell.isCorrect === true ? true : gridCell.isCorrect === false ? false : null
          };
        }
        return cell;
      });

      console.log('Updated cells:', updatedCells); // Debug log

      // Update both states
      setCells(updatedCells);

      // Update solved count only if the guess was correct
      if (data.grid[activeCell.row][activeCell.col].isCorrect === true) {
        setSolvedCount(prev => prev + 1);
      }

      // Reset UI state
      setShowSelector(false);
      setActiveCell(null);
    } catch (error) {
      console.error('Error making guess:', error);
      setError('Failed to make guess. Please try again.');
    }
  };

  // Add useEffect to sync cells with gameState
  useEffect(() => {
    if (gameState) {
      console.log('Game state updated:', gameState); // Debug log
      
      // Create a new cells array based on the game state
      const newCells = cells.map(cell => {
        const gridCell = gameState.grid[cell.row][cell.col];
        console.log(`Cell ${cell.row},${cell.col}:`, gridCell); // Debug log
        
        // Use the values from the game state, ensuring isCorrect is a boolean
        return {
          ...cell,
          champion: gridCell?.guessedChampion || null,
          isCorrect: gridCell?.isCorrect === true ? true : gridCell?.isCorrect === false ? false : null
        };
      });
      
      console.log('New cells after game state update:', newCells); // Debug log
      setCells(newCells);
    }
  }, [gameState]);

  return (
    <div className="space-y-4">
      {/* Column categories */}
      <div className="grid grid-cols-4 gap-4">
        <div className="h-12" /> {/* Empty cell for alignment */}
        {categories.cols.map((category, index) => (
          <div key={index} className="h-12 flex items-center justify-center text-center font-medium">
            {category}
          </div>
        ))}
      </div>

      {/* Grid with row categories */}
      <div className="grid grid-cols-4 gap-4">
        {/* Row categories */}
        <div className="flex flex-col justify-between">
          {categories.rows.map((category, index) => (
            <div key={index} className="aspect-square flex items-center justify-center text-center font-medium">
              {category}
            </div>
          ))}
        </div>

        {/* Grid cells */}
        <div className="col-span-3 grid grid-cols-3 gap-4">
          {cells.map((cell, index) => {
            console.log(`Rendering cell ${cell.row},${cell.col}:`, cell); // Debug log
            return (
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
            );
          })}
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

      {error && (
        <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
    </div>
  );
} 