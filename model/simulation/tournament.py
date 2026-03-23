"""
Estructura del torneo FIFA World Cup 2026.
48 equipos, 12 grupos de 4, formato con 32 clasificados.
"""

import numpy as np
import pandas as pd
from model.config import WORLD_CUP_2026_GROUPS, FEATURE_COLS


# Bracket del Mundial 2026 (R32)
# Los 2 primeros de cada grupo + 8 mejores terceros = 32 equipos
# Emparejamientos R32 oficiales FIFA:
# Match 49: 1A vs 3C/D/E    Match 50: 2A vs 2C
# Match 51: 1B vs 3A/D/E/F  Match 52: 2B vs 2D
# Match 53: 1C vs 3B/F/G    Match 54: 2E vs 2G
# Match 55: 1D vs 3A/B/F    Match 56: 2F vs 2H
# Match 57: 1E vs 3B/G/H    Match 58: 2I vs 2K
# Match 59: 1F vs 3I/J/K    Match 60: 2J vs 2L
# Match 61: 1G vs 3H/I/J    Match 62: 1J vs 3G/H/I/L
# Match 63: 1H vs 3A/C/D    Match 64: 1K vs 3E/F/J/K
# Match 65: 1I vs 2L         Match 66: 1L vs 3C/D/K/L (simplified)
#
# Simplificacion: usamos el bracket estandar FIFA publicado

R32_BRACKET = [
    # (team_slot_1, team_slot_2) -> R16 pairings from R32 winners
    # Mitad superior
    ("1A", "3C/D/E"),
    ("2C", "2A"),
    ("1B", "3A/D/E/F"),
    ("2D", "2B"),
    ("1E", "3B/G/H"),
    ("2G", "2E"),
    ("1F", "3I/J/K"),
    ("2H", "2F"),
    # Mitad inferior
    ("1C", "3B/F/G"),
    ("2A_alt", "2C_alt"),  # placeholder
    ("1D", "3A/B/F"),
    ("2B_alt", "2D_alt"),
    ("1G", "3H/I/J"),
    ("2I", "2K"),
    ("1H", "3A/C/D"),
    ("2J", "2L"),
]


def get_group_matches(groups=None):
    """
    Genera todos los partidos de fase de grupos.
    Cada equipo juega contra los otros 3 de su grupo.

    Returns:
        Lista de (group, home_team, away_team)
    """
    if groups is None:
        groups = WORLD_CUP_2026_GROUPS

    matches = []
    for group_name, teams in groups.items():
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                matches.append((group_name, teams[i], teams[j]))
    return matches


def compute_group_standings(group_results):
    """
    Calcula la clasificacion de un grupo basandose en los resultados.

    Args:
        group_results: lista de dicts con keys:
            home_team, away_team, home_score, away_score

    Returns:
        DataFrame ordenado con la clasificacion del grupo.
    """
    standings = {}

    for match in group_results:
        home = match["home_team"]
        away = match["away_team"]
        hs = match["home_score"]
        as_ = match["away_score"]

        for team in [home, away]:
            if team not in standings:
                standings[team] = {
                    "team": team, "played": 0, "wins": 0, "draws": 0,
                    "losses": 0, "gf": 0, "gc": 0, "gd": 0, "points": 0,
                }

        standings[home]["played"] += 1
        standings[away]["played"] += 1
        standings[home]["gf"] += hs
        standings[home]["gc"] += as_
        standings[away]["gf"] += as_
        standings[away]["gc"] += hs

        if hs > as_:
            standings[home]["wins"] += 1
            standings[home]["points"] += 3
            standings[away]["losses"] += 1
        elif hs == as_:
            standings[home]["draws"] += 1
            standings[home]["points"] += 1
            standings[away]["draws"] += 1
            standings[away]["points"] += 1
        else:
            standings[away]["wins"] += 1
            standings[away]["points"] += 3
            standings[home]["losses"] += 1

    for team in standings:
        standings[team]["gd"] = standings[team]["gf"] - standings[team]["gc"]

    df = pd.DataFrame(standings.values())
    # Ordenar por: puntos, diferencia de goles, goles a favor
    df = df.sort_values(
        ["points", "gd", "gf"], ascending=[False, False, False]
    ).reset_index(drop=True)
    df["position"] = range(1, len(df) + 1)

    return df


def select_best_third_placed(all_group_standings):
    """
    Selecciona los 8 mejores terceros de los 12 grupos.

    Args:
        all_group_standings: dict {group_name: standings_df}

    Returns:
        Lista de los 8 mejores terceros (team names).
    """
    thirds = []
    for group_name, standings in all_group_standings.items():
        if len(standings) >= 3:
            third = standings.iloc[2]  # posicion 3 (indice 2)
            thirds.append({
                "team": third["team"],
                "group": group_name,
                "points": third["points"],
                "gd": third["gd"],
                "gf": third["gf"],
            })

    thirds_df = pd.DataFrame(thirds)
    thirds_df = thirds_df.sort_values(
        ["points", "gd", "gf"], ascending=[False, False, False]
    ).reset_index(drop=True)

    return thirds_df.head(8)["team"].tolist()


def build_r32_bracket(all_group_standings, best_thirds):
    """
    Construye el bracket de R32 a partir de las clasificaciones de grupo.

    32 equipos = 24 (1ros y 2dos de 12 grupos) + 8 mejores terceros.
    16 partidos de R32 -> 16 ganadores pasan a R16 -> QF -> SF -> Final.

    Emparejamientos simplificados (basados en formato FIFA):
    Cada 1ro de grupo juega contra un 3ro clasificado.
    Cada 2do de grupo juega contra otro 2do de un grupo diferente.

    Args:
        all_group_standings: dict {group_name: standings_df}
        best_thirds: lista de 8 terceros clasificados

    Returns:
        Lista de 16 tuplas (team1, team2) para R32.
    """
    firsts = {}
    seconds = {}
    for group_name, standings in all_group_standings.items():
        firsts[group_name] = standings.iloc[0]["team"]
        seconds[group_name] = standings.iloc[1]["team"]

    # Bracket de R32: 16 partidos
    # Mitad 1 (genera 8 ganadores -> 4 R16 -> 2 QF -> 1 SF)
    bracket = [
        (firsts["A"], best_thirds[0]),       # M49: 1A vs 3ro
        (seconds["A"], seconds["C"]),        # M50: 2A vs 2C
        (firsts["B"], best_thirds[1]),       # M51: 1B vs 3ro
        (seconds["B"], seconds["D"]),        # M52: 2B vs 2D
        (firsts["E"], best_thirds[2]),       # M53: 1E vs 3ro
        (seconds["E"], seconds["G"]),        # M54: 2E vs 2G
        (firsts["F"], best_thirds[3]),       # M55: 1F vs 3ro
        (seconds["F"], seconds["H"]),        # M56: 2F vs 2H
        # Mitad 2 (genera 8 ganadores -> 4 R16 -> 2 QF -> 1 SF)
        (firsts["C"], best_thirds[4]),       # M57: 1C vs 3ro
        (firsts["I"], seconds["L"]),         # M58: 1I vs 2L
        (firsts["D"], best_thirds[5]),       # M59: 1D vs 3ro
        (firsts["L"], seconds["J"]),         # M60: 1L vs 2J
        (firsts["G"], best_thirds[6]),       # M61: 1G vs 3ro
        (seconds["I"], seconds["K"]),        # M62: 2I vs 2K
        (firsts["H"], best_thirds[7]),       # M63: 1H vs 3ro
        (firsts["J"], firsts["K"]),          # M64: 1J vs 1K
    ]

    return bracket


def build_knockout_rounds(r32_winners):
    """
    Dado los 16 ganadores de R32, genera R16 -> QF -> SF -> Final.

    Args:
        r32_winners: lista de 16 equipos (en orden de bracket)

    Returns:
        Lista de tuplas (team1, team2) para R16.
    """
    # R16: emparejamos 1v2, 3v4, 5v6, etc.
    r16_matches = []
    for i in range(0, len(r32_winners), 2):
        if i + 1 < len(r32_winners):
            r16_matches.append((r32_winners[i], r32_winners[i + 1]))
    return r16_matches
