import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read categories.py
    const categoriesPath = path.join(process.cwd(), 'categories.py');
    const categoriesContent = fs.readFileSync(categoriesPath, 'utf8');

    // Parse the categories from the Python file
    const categories: string[] = [];
    const lines = categoriesContent.split('\n');
    
    for (const line of lines) {
      if (line.trim().startsWith('"') && line.trim().endsWith('"')) {
        // Extract the category name from the Python string
        const category = line.trim().slice(1, -1);
        categories.push(category);
      }
    }

    return NextResponse.json({ categories });
  } catch (error) {
    console.error('Error reading categories:', error);
    return NextResponse.json({ error: 'Failed to read categories' }, { status: 500 });
  }
} 