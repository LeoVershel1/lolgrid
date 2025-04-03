export interface GridCell {
  guessedChampion: string | null;
  correctChampion: string | null;
  isCorrect: boolean;
}

export interface Category {
  name: string;
  type: string;
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