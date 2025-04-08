'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center space-y-8">
          <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            League of Legends Grid Game
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Test your League of Legends knowledge with our interactive grid game. Match champions, items, and more in this challenging puzzle experience.
          </p>
          
          <div className="flex justify-center space-x-4 mt-8">
            <Link 
              href="/grid"
              className="px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 text-lg font-semibold"
            >
              Play Now
            </Link>
          </div>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-3 text-blue-400">How to Play</h3>
            <p className="text-gray-300">
              Fill in the grid by matching the correct champions, items, or other League elements based on the given categories.
            </p>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-3 text-purple-400">Multiple Difficulties</h3>
            <p className="text-gray-300">
              Choose from Easy, Medium, or Hard difficulty levels to test your knowledge and challenge yourself.
            </p>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-3 text-green-400">Learn & Improve</h3>
            <p className="text-gray-300">
              Discover new connections between different League elements and expand your game knowledge.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
} 