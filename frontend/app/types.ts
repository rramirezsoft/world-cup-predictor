export interface Team {
  name: string;
  group: string;
  elo: number;
  confederation: string;
}

export interface MatchResult {
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  winner: string;
}

export interface GroupStanding {
  team: string;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  gf: number;
  gc: number;
  gd: number;
  points: number;
  position: number;
}

export interface GroupData {
  teams: string[];
  standings: GroupStanding[];
  matches: MatchResult[];
}

export interface SimulationResult {
  groups: Record<string, GroupData>;
  knockout: {
    r32: MatchResult[];
    r16: MatchResult[];
    qf: MatchResult[];
    sf: MatchResult[];
    final: MatchResult[];
  };
  champion: string;
  runner_up: string;
}

export interface MonteCarloTeam {
  team: string;
  champion_pct: number;
  final_pct: number;
  sf_pct: number;
  qf_pct: number;
  r16_pct: number;
  r32_pct: number;
  elo: number;
}

export interface PredictionResult {
  home_team: string;
  away_team: string;
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  home_elo: number;
  away_elo: number;
}

// ISO 3166-1 alpha-2 codes for all 48 World Cup 2026 teams
// Used with flagcdn.com: https://flagcdn.com/w40/{code}.png
export const COUNTRY_CODES: Record<string, string> = {
  // UEFA (16)
  "Germany": "de",
  "Spain": "es",
  "France": "fr",
  "England": "gb-eng",
  "Portugal": "pt",
  "Netherlands": "nl",
  "Belgium": "be",
  "Italy": "it",
  "Croatia": "hr",
  "Denmark": "dk",
  "Switzerland": "ch",
  "Austria": "at",
  "Serbia": "rs",
  "Scotland": "gb-sct",
  "Slovenia": "si",
  "Poland": "pl",
  "Wales": "gb-wls",
  "Turkey": "tr",
  "Ukraine": "ua",
  "Hungary": "hu",
  "Sweden": "se",
  "Norway": "no",
  "Romania": "ro",
  "Czech Republic": "cz",
  "Greece": "gr",
  "Slovakia": "sk",
  "Albania": "al",
  // CONMEBOL (6)
  "Argentina": "ar",
  "Brazil": "br",
  "Uruguay": "uy",
  "Colombia": "co",
  "Ecuador": "ec",
  "Paraguay": "py",
  "Chile": "cl",
  "Peru": "pe",
  "Venezuela": "ve",
  "Bolivia": "bo",
  // CONCACAF (6)
  "Mexico": "mx",
  "United States": "us",
  "USA": "us",
  "Canada": "ca",
  "Jamaica": "jm",
  "Honduras": "hn",
  "Costa Rica": "cr",
  "Panama": "pa",
  "Trinidad and Tobago": "tt",
  "El Salvador": "sv",
  // CAF (9)
  "Morocco": "ma",
  "Senegal": "sn",
  "Nigeria": "ng",
  "Cameroon": "cm",
  "Egypt": "eg",
  "Ghana": "gh",
  "Tunisia": "tn",
  "Ivory Coast": "ci",
  "Cote d'Ivoire": "ci",
  "Algeria": "dz",
  "Mali": "ml",
  "DR Congo": "cd",
  "South Africa": "za",
  "Burkina Faso": "bf",
  "Congo": "cg",
  "Tanzania": "tz",
  "Mozambique": "mz",
  "Benin": "bj",
  "Uganda": "ug",
  "Gabon": "ga",
  "Zambia": "zm",
  "Zimbabwe": "zw",
  "Equatorial Guinea": "gq",
  "Cape Verde": "cv",
  "Guinea": "gn",
  // AFC (8)
  "Japan": "jp",
  "South Korea": "kr",
  "Korea Republic": "kr",
  "Iran": "ir",
  "Australia": "au",
  "Saudi Arabia": "sa",
  "Qatar": "qa",
  "Iraq": "iq",
  "Uzbekistan": "uz",
  "China PR": "cn",
  "China": "cn",
  "Oman": "om",
  "United Arab Emirates": "ae",
  "Bahrain": "bh",
  "Jordan": "jo",
  "Indonesia": "id",
  "Palestine": "ps",
  // OFC
  "New Zealand": "nz",
};

export function getCountryCode(teamName: string): string {
  return COUNTRY_CODES[teamName] || "";
}

export function getFlagUrl(teamName: string, width: number = 40): string {
  const code = getCountryCode(teamName);
  if (!code) return "";
  return `https://flagcdn.com/w${width}/${code}.png`;
}
