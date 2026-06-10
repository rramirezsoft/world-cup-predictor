"""
Configuracion central del proyecto World Cup 2026 Predictor.
Todas las constantes, hiperparametros y rutas en un solo lugar.
"""

from pathlib import Path
import numpy as np

# --- Rutas ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "saved_models"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# --- Semilla para reproducibilidad ---
RANDOM_SEED = 42

# --- ELO ---
ELO_K = 32              # Factor K reducido para suavizar cambios de rating
ELO_INITIAL = 1500
ELO_HOME_ADV = 100
ELO_MEAN_REVERSION = 0.003  # Ligera regresion a la media tras cada partido

TOURNAMENT_WEIGHTS = {
    "FIFA World Cup": 1.5,
    "UEFA Euro": 1.4,
    "Copa America": 1.4,
    "African Cup of Nations": 1.3,
    "Confederations Cup": 1.3,
    "Gold Cup": 1.2,
    "AFC Asian Cup": 1.2,
    "FIFA World Cup qualification": 1.1,
    "UEFA Euro qualification": 1.1,
    "Copa America qualification": 1.1,
    "African Cup of Nations qualification": 1.0,
    "AFC Asian Cup qualification": 1.0,
    "CONCACAF Nations League": 1.0,
    "UEFA Nations League A": 1.0,
    "UEFA Nations League B": 0.9,
    "UEFA Nations League C": 0.8,
    "UEFA Nations League D": 0.7,
    "Friendly": 0.6,
}
TOURNAMENT_WEIGHT_DEFAULT = 0.85

# --- Feature Engineering ---
FORM_WINDOW = 10       # Ultimos N partidos para forma reciente
H2H_WINDOW = 5         # Ultimos N enfrentamientos directos
STREAK_MAX = 15        # Maximo de racha a considerar

# --- Confederaciones ---
CONFEDERATIONS = {
    # UEFA (55 miembros)
    "UEFA": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus",
        "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
        "Czech Republic", "Czechia", "Denmark", "England", "Estonia", "Faroe Islands",
        "Finland", "France", "Georgia", "Germany", "Gibraltar", "Greece",
        "Hungary", "Iceland", "Israel", "Italy", "Kazakhstan", "Kosovo",
        "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
        "Moldova", "Montenegro", "Netherlands", "North Macedonia", "Northern Ireland",
        "Norway", "Poland", "Portugal", "Republic of Ireland", "Romania",
        "Russia", "San Marino", "Scotland", "Serbia", "Slovakia", "Slovenia",
        "Spain", "Sweden", "Switzerland", "Turkey", "Türkiye", "Ukraine", "Wales",
    ],
    # CONMEBOL (10 miembros)
    "CONMEBOL": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
        "Paraguay", "Peru", "Uruguay", "Venezuela",
    ],
    # CONCACAF (41 miembros - principales)
    "CONCACAF": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Bermuda",
        "Canada", "Cayman Islands", "Costa Rica", "Cuba", "Curaçao", "Curacao",
        "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala",
        "Guyana", "Haiti", "Honduras", "Jamaica", "Mexico", "Montserrat",
        "Nicaragua", "Panama", "Puerto Rico", "Saint Kitts and Nevis",
        "Saint Lucia", "Saint Vincent and the Grenadines", "Suriname",
        "Trinidad and Tobago", "Turks and Caicos Islands",
        "US Virgin Islands", "United States",
    ],
    # CAF (54 miembros - principales)
    "CAF": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
        "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
        "Congo", "DR Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea",
        "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
        "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
        "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco",
        "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda",
        "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo",
        "Tunisia", "Uganda", "Zambia", "Zimbabwe",
    ],
    # AFC (47 miembros - principales)
    "AFC": [
        "Afghanistan", "Australia", "Bahrain", "Bangladesh", "Bhutan", "Brunei",
        "Cambodia", "China PR", "Chinese Taipei", "Guam", "Hong Kong",
        "India", "Indonesia", "Iran", "Iraq", "Japan", "Jordan", "Kuwait",
        "Kyrgyzstan", "Laos", "Lebanon", "Macau", "Malaysia", "Maldives",
        "Mongolia", "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan",
        "Palestine", "Philippines", "Qatar", "Saudi Arabia", "Singapore",
        "South Korea", "Korea Republic", "Sri Lanka", "Syria", "Tajikistan",
        "Thailand", "Timor-Leste", "Turkmenistan", "United Arab Emirates",
        "Uzbekistan", "Vietnam", "Yemen",
    ],
    # OFC (11 miembros)
    "OFC": [
        "American Samoa", "Cook Islands", "Fiji", "New Caledonia", "New Zealand",
        "Papua New Guinea", "Samoa", "Solomon Islands", "Tahiti", "Tonga", "Vanuatu",
    ],
}

# Crear mapa inverso: equipo -> confederacion
TEAM_TO_CONFEDERATION = {}
for conf, teams in CONFEDERATIONS.items():
    for team in teams:
        TEAM_TO_CONFEDERATION[team] = conf

# --- Torneos principales (para feature de experiencia) ---
MAJOR_TOURNAMENTS = {
    "FIFA World Cup",
    "UEFA Euro",
    "Copa America",
    "African Cup of Nations",
    "AFC Asian Cup",
    "Gold Cup",
    "Confederations Cup",
    "UEFA Nations League A",
}

# --- Torneos con fase de eliminatoria directa ---
KNOCKOUT_TOURNAMENTS = {
    "FIFA World Cup",
    "UEFA Euro",
    "Copa America",
    "African Cup of Nations",
    "AFC Asian Cup",
    "Gold Cup",
    "Confederations Cup",
}

# --- Data Split ---
TRAIN_START_YEAR = 2000
TRAIN_END_YEAR = 2021
VAL_YEAR = 2022
TEST_START_YEAR = 2023

# --- Feature Columns ---
FEATURE_COLS = [
    # ELO
    "home_elo", "away_elo", "elo_diff", "elo_expected_home",
    # Forma reciente - local
    "home_form_wins", "home_form_draws", "home_form_losses",
    "home_form_gf", "home_form_gc", "home_form_points", "home_form_gd",
    # Forma reciente - visitante
    "away_form_wins", "away_form_draws", "away_form_losses",
    "away_form_gf", "away_form_gc", "away_form_points", "away_form_gd",
    # Head-to-Head
    "h2h_home_wins", "h2h_away_wins", "h2h_draws",
    "h2h_home_goals", "h2h_away_goals", "h2h_dominance",
    # Diferencias
    "form_points_diff", "form_gd_diff", "form_gf_diff",
    # Contextuales
    "neutral_int", "tournament_weight", "is_competitive",
    # Confederacion
    "home_conf_strength", "away_conf_strength", "is_inter_confederation",
    # Rachas
    "home_streak", "away_streak",
    "home_unbeaten_streak", "away_unbeaten_streak",
    # Descanso
    "home_days_rest", "away_days_rest", "rest_advantage",
    # Clean sheets
    "home_clean_sheet_pct", "away_clean_sheet_pct",
    # Fase de torneo
    "is_knockout",
    # Experiencia en grandes torneos
    "home_major_tournament_exp", "away_major_tournament_exp",
    # Rendimiento local/visitante especifico
    "home_home_record", "away_away_record",
    # Ranking FIFA
    "home_fifa_rank", "away_fifa_rank", "fifa_rank_diff",
]

TARGET = "result"

# --- Grupos Mundial 2026 ---
# Los nombres deben coincidir EXACTAMENTE con los de results.csv
# Grupos definitivos tras la resolucion de todas las repescas (marzo 2026)
WORLD_CUP_2026_GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Jamaica", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Sedes del Mundial 2026 (todos en campo neutral)
WC2026_HOST_COUNTRIES = ["United States", "Mexico", "Canada"]

# --- Hyperparameter Tuning ---
OPTUNA_N_TRIALS = 100
CV_N_SPLITS = 5

# --- Simulacion ---
MONTE_CARLO_SIMULATIONS = 10_000

# --- Ranking FIFA (abril 2026, fuente: football-ranking.com) ---
# Usado como feature estatica. Equipos no listados reciben rank 100 (por defecto).
FIFA_RANKINGS = {
    "France": 1, "Spain": 2, "Argentina": 3, "England": 4, "Portugal": 5,
    "Brazil": 6, "Netherlands": 7, "Morocco": 8, "Belgium": 9, "Germany": 10,
    "Croatia": 11, "Colombia": 12, "Senegal": 13, "Italy": 14, "Mexico": 15,
    "United States": 16, "Uruguay": 17, "Japan": 18, "Switzerland": 19,
    "Iran": 20, "Denmark": 21, "Turkey": 22, "Ecuador": 23, "Austria": 24,
    "South Korea": 25, "Nigeria": 26, "Australia": 27, "Algeria": 28,
    "Egypt": 29, "Canada": 30, "Norway": 31, "Ukraine": 32, "Panama": 33,
    "Ivory Coast": 34, "Poland": 35, "Sweden": 37, "Czech Republic": 38,
    "Paraguay": 41, "Scotland": 43, "Tunisia": 44, "Uzbekistan": 49,
    "Qatar": 55, "Iraq": 57, "South Africa": 60, "Saudi Arabia": 61,
    "Jordan": 63, "Bosnia and Herzegovina": 65, "Cape Verde": 69,
    "Ghana": 74, "Haiti": 83, "New Zealand": 85, "Jamaica": 87,
    "Curaçao": 95,
}
FIFA_RANK_DEFAULT = 100
