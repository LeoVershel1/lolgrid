export interface Category {
  name: string;
  type: string;
}

export interface GridCell {
  guessedChampion?: string;
  correctChampion?: string;
  correctChampions?: string[];
  isCorrect?: boolean;
} 