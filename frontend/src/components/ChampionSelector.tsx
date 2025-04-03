"use client";

import React, { useState, useEffect, useRef } from 'react';
import { CHAMPION_ICONS_URL } from '../config';

interface ChampionSelectorProps {
  onSelect: (champion: string) => void;
  onClose: () => void;
}

const ChampionSelector: React.FC<ChampionSelectorProps> = ({ onSelect, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [champions, setChampions] = useState<string[]>([]);
  const [filteredChampions, setFilteredChampions] = useState<string[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch champions list when component mounts
    fetch('/api/champions')
      .then(res => res.json())
      .then(data => {
        const sortedChampions = data.sort();
        setChampions(sortedChampions);
        setFilteredChampions(sortedChampions);
      })
      .catch(error => console.error('Error fetching champions:', error));
  }, []);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // Filter champions based on search term
    const filtered = champions.filter(champion =>
      champion.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredChampions(filtered);
    setSelectedIndex(0); // Reset selection when filtering
  }, [searchTerm, champions]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'Enter' && filteredChampions.length > 0) {
      e.preventDefault();
      const selectedChampion = filteredChampions[selectedIndex];
      onSelect(selectedChampion);
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredChampions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    }
  };

  const handleChampionClick = (e: React.MouseEvent, champion: string) => {
    e.preventDefault();
    e.stopPropagation();
    onSelect(champion);
    onClose();
  };

  const handleContainerClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <div 
      ref={containerRef}
      className="absolute inset-0 bg-gray-100 rounded-lg shadow-xl z-50 p-4"
      onClick={handleContainerClick}
    >
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search champion..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          onClick={(e) => e.stopPropagation()}
        />
      </div>
      <div className="mt-2 max-h-[300px] overflow-y-auto bg-white rounded-lg shadow-inner">
        {filteredChampions.length === 0 ? (
          <div className="px-4 py-2 text-gray-500 text-center">
            No champions found
          </div>
        ) : (
          filteredChampions.map((champion, index) => (
            <button
              key={champion}
              onClick={(e) => handleChampionClick(e, champion)}
              className={`w-full flex items-center px-4 py-2 hover:bg-gray-50 text-left border-b border-gray-100 last:border-0 ${
                index === selectedIndex ? 'bg-blue-50' : ''
              }`}
            >
              <img
                src={`${CHAMPION_ICONS_URL}/${champion}.png`}
                alt={champion}
                className="w-6 h-6 rounded-full mr-3"
                onError={(e) => {
                  // Fallback if image fails to load
                  (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                }}
              />
              <span className="text-gray-700">{champion}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ChampionSelector; 