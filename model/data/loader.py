"""
Carga y limpieza de los datasets de partidos internacionales.
"""

import pandas as pd
from model.config import DATA_DIR


def load_results():
    """Carga results.csv con tipos correctos y columnas derivadas."""
    df = pd.read_csv(DATA_DIR / "results.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["neutral"] = df["neutral"].astype(bool)

    # Variable objetivo
    df["result"] = df.apply(
        lambda r: 2 if r["home_score"] > r["away_score"]
        else (1 if r["home_score"] == r["away_score"] else 0),
        axis=1,
    )
    df["goal_diff"] = df["home_score"] - df["away_score"]

    return df.sort_values("date").reset_index(drop=True)


def load_goalscorers():
    """Carga goalscorers.csv."""
    df = pd.read_csv(DATA_DIR / "goalscorers.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_shootouts():
    """Carga shootouts.csv."""
    df = pd.read_csv(DATA_DIR / "shootouts.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_former_names():
    """Carga former_names.csv para mapear nombres historicos."""
    return pd.read_csv(DATA_DIR / "former_names.csv")


def load_all():
    """Carga todos los datasets y devuelve un diccionario."""
    return {
        "results": load_results(),
        "goalscorers": load_goalscorers(),
        "shootouts": load_shootouts(),
        "former_names": load_former_names(),
    }
