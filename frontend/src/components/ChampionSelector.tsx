"use client";

import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from '../config';

interface ChampionSelectorProps {
  onSelect: (champion: string) => void;
  onClose: () => void;
}

const ChampionSelector: React.FC<ChampionSelectorProps> = ({ onSelect, onClose }) => {
  const [champions, setChampions] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchChampions = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/champions`);
        const data = await response.json();
        setChampions(data);
      } catch (error) {
        console.error('Error fetching champions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChampions();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  const filteredChampions = champions.filter(champion =>
    champion.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (champion: string) => {
    onSelect(champion);
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div 
      ref={dropdownRef}
      className="absolute z-50 bg-white border rounded-lg shadow-lg w-64 max-h-80 overflow-y-auto"
      style={{ top: '100%', left: '0' }}
    >
      <div className="p-2">
        <input
          type="text"
          placeholder="Search champions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full p-2 border rounded mb-2"
          autoFocus
        />
        {isLoading ? (
          <div className="text-center py-2">Loading champions...</div>
        ) : (
          <div className="max-h-60 overflow-y-auto">
            {filteredChampions.map((champion) => (
              <button
                key={champion}
                onClick={() => handleSelect(champion)}
                className="flex items-center w-full p-2 hover:bg-gray-100 rounded"
              >
                <img
                  src={`${API_BASE_URL}/champion_icons/${encodeURIComponent(champion)}.png`}
                  alt={champion}
                  className="w-8 h-8 rounded-full mr-2"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/placeholder-champion.png';
                  }}
                />
                <span className="text-sm">{champion}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChampionSelector; 