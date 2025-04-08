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
  const [difficulty, setDifficulty] = useState(0.5);

  const fetchDailyChallenge = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/daily`);
      if (!response.ok) throw new Error('Failed to fetch daily challenge');
      const data = await response.json();
      setChallenge(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const generateNewGrid = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ difficulty }),
      });
      if (!response.ok) throw new Error('Failed to generate new grid');
      const data = await response.json();
      setChallenge(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDailyChallenge();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">League of Legends Grid Game</h1>
          <div className="space-x-4">
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(Number(e.target.value))}
              className="px-4 py-2 border rounded-lg"
            >
              <option value={0.3}>Easy</option>
              <option value={0.5}>Medium</option>
              <option value={0.7}>Hard</option>
            </select>
            <button
              onClick={generateNewGrid}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Generate New Grid
            </button>
          </div>
        </div>
        {challenge && <GameBoard categories={challenge} />}
      </div>
    </main>
  );
} 