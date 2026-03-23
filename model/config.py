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
ELO_K = 40
ELO_INITIAL = 1500
ELO_HOME_ADV = 100

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
]

TARGET = "result"

# --- Grupos Mundial 2026 ---
# Los nombres deben coincidir EXACTAMENTE con los de results.csv
WORLD_CUP_2026_GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Denmark"],         # Denmark = favorito repesca UEFA D
    "B": ["Canada", "Italy", "Qatar", "Switzerland"],                  # Italy = favorito repesca UEFA A
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],         # Turkey = favorito repesca UEFA C
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Poland", "Tunisia"],                # Poland = favorito repesca UEFA B
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],                     # Iraq = favorito repesca intercont. 2
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],          # DR Congo = favorito repesca intercont. 1
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Sedes del Mundial 2026 (todos en campo neutral)
WC2026_HOST_COUNTRIES = ["United States", "Mexico", "Canada"]

# --- Hyperparameter Tuning ---
OPTUNA_N_TRIALS = 100
CV_N_SPLITS = 5

# --- Simulacion ---
MONTE_CARLO_SIMULATIONS = 10_000
