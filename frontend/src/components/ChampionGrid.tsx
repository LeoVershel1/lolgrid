"use client";

import React from 'react';
import ChampionCell from './ChampionCell';
import { GridCell, Category } from '../types';

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
  showAnswers
}) => {
  return (
    <div className="space-y-4">
      {/* Column categories */}
      <div className="grid grid-cols-4 gap-4">
        <div className="h-12" /> {/* Empty cell for alignment */}
        {categories.xAxis.map((category, index) => (
          <div
            key={index}
            className="h-12 flex items-center justify-center text-center font-medium"
          >
            {category.name}
          </div>
        ))}
      </div>

      {/* Grid with row categories */}
      <div className="grid grid-cols-4 gap-4">
        {/* Row categories */}
        <div className="flex flex-col justify-between">
          {categories.yAxis.map((category, index) => (
            <div
              key={index}
              className="aspect-square flex items-center justify-center text-center font-medium"
            >
              {category.name}
            </div>
          ))}
        </div>

        {/* Grid cells */}
        <div className="col-span-3 grid grid-cols-3 gap-4">
          {grid.map((row, rowIndex) =>
            row.map((cell, colIndex) => (
              <ChampionCell
                key={`${rowIndex}-${colIndex}`}
                cell={cell}
                onGuess={(champion) => onGuess(rowIndex, colIndex, champion)}
                showAnswers={showAnswers}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ChampionGrid; 