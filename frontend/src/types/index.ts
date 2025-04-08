export interface GridCell {
  xCategory: string;
  yCategory: string;
  correctChampions: string[];
  guessedChampion: string | null;
  isCorrect: boolean | null;
}

export interface Category {
  name: string;
  values: string[];
}

export interface ChampionAbilities {
  hasPassiveE: boolean;
  isShapeshifter: boolean;
  hasThreeHitPassive: boolean;
  hasAutoAttackReset: boolean;
  hasAbilityCharges: boolean;
  hasMultipleHardCC: boolean;
  hasChangingAbilities: boolean;
}

export interface Champion {
  name: string;
  region: string;
  role: string[];
  resource: string;
  species: string;
  primaryDamageType: string;
  range: number;
  baseMovespeed: number;
  releaseSeason: number;
  modelSize: number;
  skinLines: string[];
  abilities: ChampionAbilities;
}

// ChampionData is just an array of Champions
export type ChampionData = Champion[];

export interface GameState {
  grid: GridCell[][];
  categories: {
    xAxis: Category[];
    yAxis: Category[];
  };
  guessesRemaining: number;
  isGameOver: boolean;
  score: number;
  gameId: string;
  difficulty: number;
} 