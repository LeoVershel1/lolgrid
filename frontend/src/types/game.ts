export type Category = {
  name: string;
  values: string[];
};

export type GridCell = {
  xCategory: string;
  yCategory: string;
  correctChampions: string[];
  guessedChampion?: string;
  isCorrect?: boolean;
};

export type GameState = {
  grid: GridCell[][];
  categories: {
    xAxis: Category[];
    yAxis: Category[];
  };
  guessesRemaining: number;
  isGameOver: boolean;
  score: number;
};

export type ChampionIcon = {
  [key: string]: string;
}; 