"use client";

import React, { useState, useEffect, useRef } from 'react';
import { API_URL } from '../config';

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

  // Get the champion ID for the icon URL
  const getChampionId = (championName: string): string => {
    // Remove .png extension if it exists
    const cleanName = championName.replace('.png', '');
    return CHAMPION_ID_MAPPING[cleanName] || cleanName;
  };

  useEffect(() => {
    const fetchChampions = async () => {
      try {
        const response = await fetch(`${API_URL}/api/champions`);
        if (response.ok) {
          const data = await response.json();
          // Handle both array format and object with champions property
          const championsList = Array.isArray(data) ? data : (data.champions || []);
          setChampions(championsList);
        } else {
          console.error('Failed to fetch champions');
          setChampions([]);
        }
      } catch (error) {
        console.error('Error fetching champions:', error);
        setChampions([]);
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

  const handleSelect = (champion: string) => {
    onSelect(champion);
    setIsOpen(false);
  };

  const filteredChampions = champions.filter(champion =>
    champion.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
                  src={`${API_URL}/champion_icons/${encodeURIComponent(getChampionId(champion))}`}
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