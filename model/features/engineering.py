"""
Orquestador de Feature Engineering.
Procesa el DataFrame de partidos y genera todas las features.
"""

import numpy as np
import pandas as pd
from collections import defaultdict

from model.config import (
    TEAM_TO_CONFEDERATION, MAJOR_TOURNAMENTS, KNOCKOUT_TOURNAMENTS,
    FEATURE_COLS, TARGET, TRAIN_START_YEAR,
)
from model.features.elo import ELOSystem, get_tournament_weight
from model.features.form import FormTracker
from model.features.h2h import H2HTracker


def _get_confederation(team):
    """Devuelve la confederacion de un equipo."""
    return TEAM_TO_CONFEDERATION.get(team, "UNKNOWN")


def _is_knockout_match(tournament, home_score, away_score, neutral):
    """
    Heuristica para detectar si un partido es de eliminatoria directa.
    En torneos principales, si es en campo neutral y no es clasificacion.
    """
    if tournament in KNOCKOUT_TOURNAMENTS and neutral:
        return 1
    return 0


def build_features(df):
    """
    Procesa todo el DataFrame de partidos cronologicamente y genera features.

    El procesamiento es secuencial porque cada partido actualiza el estado
    (ELO, forma, H2H) que se usa en partidos posteriores.

    Args:
        df: DataFrame con columnas date, home_team, away_team, home_score,
            away_score, tournament, neutral, result, year.

    Returns:
        DataFrame con todas las features añadidas.
    """
    df = df.sort_values("date").reset_index(drop=True)

    # Inicializar trackers
    elo = ELOSystem()
    form = FormTracker()
    h2h = H2HTracker()

    # Tracker de experiencia en grandes torneos
    major_exp = defaultdict(int)

    # Calcular fortaleza media por confederacion (se actualiza progresivamente)
    conf_wins = {}

    # Arrays para features (mas rapido que ir poniendo valores en df)
    n = len(df)
    features = {col: np.zeros(n) for col in FEATURE_COLS}

    for i, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hs = row["home_score"]
        as_ = row["away_score"]
        neutral = row["neutral"]
        tournament = row["tournament"]
        date = row["date"]
        result = row["result"]

        # ---- FEATURES ANTES del partido (lo que sabemos pre-match) ----

        # 1. ELO
        features["home_elo"][i] = elo.get(home)
        features["away_elo"][i] = elo.get(away)
        features["elo_diff"][i] = elo.get(home) - elo.get(away)
        features["elo_expected_home"][i] = elo.get_expected_home(home, away, neutral)

        # 2. Forma reciente
        home_form = form.get_form(home)
        away_form = form.get_form(away)
        for key, val in home_form.items():
            features[f"home_{key}"][i] = val
        for key, val in away_form.items():
            features[f"away_{key}"][i] = val

        # 3. Diferencias de forma
        features["form_points_diff"][i] = home_form["form_points"] - away_form["form_points"]
        features["form_gd_diff"][i] = home_form["form_gd"] - away_form["form_gd"]
        features["form_gf_diff"][i] = home_form["form_gf"] - away_form["form_gf"]

        # 4. Head-to-Head
        h2h_feats = h2h.get_h2h(home, away)
        for key, val in h2h_feats.items():
            features[key][i] = val

        # 5. Contextuales (originales)
        features["neutral_int"][i] = 1 if neutral else 0
        tw = get_tournament_weight(tournament)
        features["tournament_weight"][i] = tw
        features["is_competitive"][i] = 1 if tw >= 1.0 else 0

        # 6. Confederacion
        home_conf = _get_confederation(home)
        away_conf = _get_confederation(away)

        # Fortaleza de confederacion (win rate media)
        home_conf_data = conf_wins.get(home_conf, {"wins": 0, "matches": 0})
        away_conf_data = conf_wins.get(away_conf, {"wins": 0, "matches": 0})
        features["home_conf_strength"][i] = (
            home_conf_data["wins"] / max(home_conf_data["matches"], 1)
        )
        features["away_conf_strength"][i] = (
            away_conf_data["wins"] / max(away_conf_data["matches"], 1)
        )
        features["is_inter_confederation"][i] = 1 if home_conf != away_conf else 0

        # 7. Rachas
        features["home_streak"][i] = form.get_streak(home)
        features["away_streak"][i] = form.get_streak(away)
        features["home_unbeaten_streak"][i] = form.get_unbeaten_streak(home)
        features["away_unbeaten_streak"][i] = form.get_unbeaten_streak(away)

        # 8. Descanso entre partidos
        home_rest = form.get_days_since_last_match(home, date)
        away_rest = form.get_days_since_last_match(away, date)
        features["home_days_rest"][i] = home_rest
        features["away_days_rest"][i] = away_rest
        features["rest_advantage"][i] = home_rest - away_rest

        # 9. Clean sheets
        features["home_clean_sheet_pct"][i] = form.get_clean_sheet_pct(home)
        features["away_clean_sheet_pct"][i] = form.get_clean_sheet_pct(away)

        # 10. Fase de torneo (knockout heuristic)
        features["is_knockout"][i] = _is_knockout_match(tournament, hs, as_, neutral)

        # 11. Experiencia en grandes torneos
        features["home_major_tournament_exp"][i] = major_exp[home]
        features["away_major_tournament_exp"][i] = major_exp[away]

        # 12. Rendimiento local/visitante especifico
        features["home_home_record"][i] = form.get_home_record(home)
        features["away_away_record"][i] = form.get_away_record(away)

        # ---- ACTUALIZAR TRACKERS (despues del partido) ----

        # ELO
        elo.update(home, away, hs, as_, neutral, tournament)

        # Forma
        if hs > as_:
            home_result, away_result = "W", "L"
        elif hs == as_:
            home_result, away_result = "D", "D"
        else:
            home_result, away_result = "L", "W"

        form.update(home, home_result, hs, as_, date, was_home=True)
        form.update(away, away_result, as_, hs, date, was_home=False)

        # H2H
        h2h.update(home, away, hs, as_)

        # Experiencia en grandes torneos
        if tournament in MAJOR_TOURNAMENTS:
            major_exp[home] += 1
            major_exp[away] += 1

        # Fortaleza de confederacion (actualizar con resultado de este partido)
        if home_conf != "UNKNOWN":
            if home_conf not in conf_wins:
                conf_wins[home_conf] = {"wins": 0, "matches": 0}
            conf_wins[home_conf]["matches"] += 1
            if hs > as_:
                conf_wins[home_conf]["wins"] += 1
        if away_conf != "UNKNOWN":
            if away_conf not in conf_wins:
                conf_wins[away_conf] = {"wins": 0, "matches": 0}
            conf_wins[away_conf]["matches"] += 1
            if as_ > hs:
                conf_wins[away_conf]["wins"] += 1

    # Asignar todas las features al DataFrame
    for col in FEATURE_COLS:
        df[col] = features[col]

    # Guardar el sistema ELO final para predicciones futuras
    df.attrs["elo_system"] = elo
    df.attrs["form_tracker"] = form
    df.attrs["h2h_tracker"] = h2h
    df.attrs["major_exp"] = dict(major_exp)
    df.attrs["conf_wins"] = dict(conf_wins)

    return df


def prepare_splits(df):
    """
    Divide el DataFrame en train/val/test con split temporal.

    Returns:
        dict con keys: X_train, y_train, X_val, y_val, X_test, y_test,
                       X_wc2022, y_wc2022, df_train, df_val, df_test, df_wc2022
    """
    from sklearn.preprocessing import StandardScaler
    from model.config import TRAIN_END_YEAR, VAL_YEAR, TEST_START_YEAR

    df_model = df[df["year"] >= TRAIN_START_YEAR].copy()

    wc2022_mask = (
        (df_model["tournament"] == "FIFA World Cup") & (df_model["year"] == 2022)
    )
    train_mask = df_model["year"] <= TRAIN_END_YEAR
    val_mask = (df_model["year"] == VAL_YEAR) & (~wc2022_mask)
    test_mask = df_model["year"] >= TEST_START_YEAR

    splits = {}
    for name, mask in [("train", train_mask), ("val", val_mask),
                       ("test", test_mask), ("wc2022", wc2022_mask)]:
        splits[f"X_{name}"] = df_model.loc[mask, FEATURE_COLS].copy()
        splits[f"y_{name}"] = df_model.loc[mask, TARGET].copy()
        splits[f"df_{name}"] = df_model.loc[mask].copy()

    # Scaler para modelos lineales
    scaler = StandardScaler()
    splits["X_train_sc"] = pd.DataFrame(
        scaler.fit_transform(splits["X_train"]),
        columns=FEATURE_COLS,
        index=splits["X_train"].index,
    )
    for name in ["val", "test", "wc2022"]:
        splits[f"X_{name}_sc"] = pd.DataFrame(
            scaler.transform(splits[f"X_{name}"]),
            columns=FEATURE_COLS,
            index=splits[f"X_{name}"].index,
        )
    splits["scaler"] = scaler
    splits["df_model"] = df_model

    return splits


def compute_sample_weights(df_train, y_train):
    """
    Calcula pesos por muestra: partidos recientes y competitivos pesan mas.
    weight = tournament_weight * exp(-years_ago * 0.1)
    """
    max_year = df_train["year"].max()
    years_ago = max_year - df_train["year"]
    time_weight = np.exp(-years_ago * 0.1)
    tournament_w = df_train["tournament_weight"] if "tournament_weight" in df_train.columns else 1.0
    weights = time_weight * tournament_w
    # Normalizar para que media sea 1
    weights = weights / weights.mean()
    return weights.values
