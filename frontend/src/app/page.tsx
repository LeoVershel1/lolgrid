'use client';

import { useState, useEffect } from 'react';
import GameBoard from '../components/GameBoard';
import { API_URL } from '../config';

interface DailyChallenge {
  rows: string[];
  cols: string[];
}

export default function Home() {
  const [challenge, setChallenge] = useState<DailyChallenge | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDailyChallenge();
  }, []);

  const fetchDailyChallenge = async () => {
    try {
      const response = await fetch(`${API_URL}/api/daily`);
      if (!response.ok) throw new Error('Failed to fetch daily challenge');
      const data = await response.json();
      setChallenge(data);
    } catch (error) {
      console.error('Error fetching daily challenge:', error);
      setError('Failed to load the daily challenge. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-center">LoL Grid</h1>
          <div className="text-center">Loading today's challenge...</div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-center">LoL Grid</h1>
          <div className="text-center text-red-600">{error}</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">LoL Grid</h1>
        
        <div className="mb-8">
          <div className="text-center text-sm text-gray-600 mb-4">
            Today's Challenge
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-4">
              {challenge?.rows.map((category, index) => (
                <div key={index} className="text-sm font-medium text-gray-700">
                  {category}
                </div>
              ))}
            </div>
            <div className="space-y-4">
              {challenge?.cols.map((category, index) => (
                <div key={index} className="text-sm font-medium text-gray-700">
                  {category}
                </div>
              ))}
            </div>
          </div>
        </div>

        {challenge && (
          <GameBoard categories={challenge} />
        )}
      </div>
    </main>
  );
} 