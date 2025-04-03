"use client";

import React, { useState, useEffect, useRef } from 'react';
import { CHAMPION_ICONS_URL } from '../config';
import type { Champion } from '../types/index';

interface ChampionSelectorProps {
  onSelect: (champion: string) => void;
  onClose: () => void;
}

const ChampionSelector: React.FC<ChampionSelectorProps> = ({ onSelect, onClose }) => {
  const [champions, setChampions] = useState<Champion[]>([]);
  const [filteredChampions, setFilteredChampions] = useState<Champion[]>([]);
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchChampions = async () => {
      try {
        const response = await fetch('/api/champions/details');
        const data = await response.json();
        // Ensure data is an array before setting state
        const championsArray = Array.isArray(data) ? data : [];
        setChampions(championsArray);
        setFilteredChampions(championsArray);
      } catch (error) {
        console.error('Error fetching champions:', error);
        // Set empty arrays on error
        setChampions([]);
        setFilteredChampions([]);
      }
    };

    fetchChampions();
  }, []);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // Filter champions based on search term
    const filtered = champions.filter((champion) => {
      const searchTerm = search.toLowerCase();
      return champion.name.toLowerCase().includes(searchTerm);
    });
    setFilteredChampions(filtered);
    setSelectedIndex(0); // Reset selection when filtering
  }, [search, champions]);

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
      onSelect(selectedChampion.name);
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredChampions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    }
  };

  const handleChampionClick = (e: React.MouseEvent, champion: Champion) => {
    e.preventDefault();
    e.stopPropagation();
    onSelect(champion.name);
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
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search champion by name..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          onClick={(e) => e.stopPropagation()}
        />
      </div>
      <div className="mt-2 max-h-[400px] overflow-y-auto bg-white rounded-lg shadow-inner">
        {filteredChampions.length === 0 ? (
          <div className="px-4 py-2 text-gray-500 text-center">
            No champions found
          </div>
        ) : (
          filteredChampions.map((champion, index) => (
            <button
              key={champion.name}
              onClick={(e) => handleChampionClick(e, champion)}
              className={`w-full flex items-center px-4 py-2 hover:bg-gray-50 text-left border-b border-gray-100 last:border-0 ${
                index === selectedIndex ? 'bg-blue-50' : ''
              }`}
            >
              <img
                src={`${CHAMPION_ICONS_URL}/${champion.name}.png`}
                alt={champion.name}
                className="w-8 h-8 rounded-full mr-3"
                onError={(e) => {
                  // Fallback if image fails to load
                  (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                }}
              />
              <span className="text-gray-900 font-medium">{champion.name}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ChampionSelector; 