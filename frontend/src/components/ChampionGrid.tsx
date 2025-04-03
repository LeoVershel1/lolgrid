"use client";

import React, { useState } from 'react';
import ChampionCell from './ChampionCell';
import { GridCell, Category } from '../types/index';

interface ChampionGridProps {
  grid: GridCell[][];
  categories: {
    xAxis: Category[];
    yAxis: Category[];
  };
  onGuess: (row: number, col: number, champion: string) => void;
  showAnswers: boolean;
}

const ChampionGrid: React.FC<ChampionGridProps> = ({
  grid,
  categories,
  onGuess,
  showAnswers,
}) => {
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);

  // Convert 2D grid to 1D array for easier mapping
  const cells = grid.flatMap((row, rowIndex) =>
    row.map((cell, colIndex) => ({
      cell,
      rowIndex,
      colIndex,
    }))
  );

  return (
    <div className="flex flex-col items-center space-y-6 p-6">
      {/* X-axis categories */}
      <div className="grid grid-cols-3 gap-4 w-[600px]">
        {categories.xAxis.map((category, index) => (
          <div key={index} className="text-center font-semibold p-2 text-gray-700">
            {category.name}
          </div>
        ))}
      </div>

      <div className="flex gap-6">
        {/* Y-axis categories */}
        <div className="flex flex-col justify-between py-4">
          {categories.yAxis.map((category, index) => (
            <div key={index} className="text-center font-semibold p-2 text-gray-700 w-32">
              {category.name}
            </div>
          ))}
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-3 grid-rows-3 gap-4 p-4 rounded-lg w-[600px] h-[600px] bg-white shadow-lg">
          {cells.map(({ cell, rowIndex, colIndex }) => (
            <ChampionCell
              key={`${rowIndex}-${colIndex}`}
              cell={cell}
              isSelected={selectedCell?.row === rowIndex && selectedCell?.col === colIndex}
              onSelect={() => setSelectedCell({ row: rowIndex, col: colIndex })}
              onGuess={(champion) => onGuess(rowIndex, colIndex, champion)}
              showAnswers={showAnswers}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChampionGrid; 