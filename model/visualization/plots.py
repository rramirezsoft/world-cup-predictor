"""
Modulo de visualizacion completo para el TFG World Cup 2026 Predictor.
Graficas profesionales para EDA, modelos y simulacion del Mundial.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.calibration import calibration_curve
from collections import defaultdict

from model.config import (
    OUTPUTS_DIR, TEAM_TO_CONFEDERATION, CONFEDERATIONS,
    WORLD_CUP_2026_GROUPS, FEATURE_COLS, TARGET,
)

# =============================================================================
# ESTILO GLOBAL
# =============================================================================

# Paleta profesional consistente
COLORS = {
    "primary": "#1a5276",
    "secondary": "#2e86c1",
    "accent": "#e74c3c",
    "success": "#27ae60",
    "warning": "#f39c12",
    "draw": "#95a5a6",
    "bg": "#fafafa",
    "grid": "#e0e0e0",
}

CONF_COLORS = {
    "UEFA": "#003399",
    "CONMEBOL": "#2ecc71",
    "CONCACAF": "#e74c3c",
    "CAF": "#f39c12",
    "AFC": "#9b59b6",
    "OFC": "#1abc9c",
}

RESULT_COLORS = ["#e74c3c", "#95a5a6", "#27ae60"]  # away, draw, home
RESULT_LABELS = ["Victoria Visitante", "Empate", "Victoria Local"]


def setup_style():
    """Configura el estilo global de graficos - profesional y limpio."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "#fafafa",
        "axes.grid": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.alpha": 0.3,
        "grid.color": "#cccccc",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "figure.figsize": (12, 6),
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#cccccc",
    })
    sns.set_style("whitegrid")


def save_fig(fig, filename):
    """Guarda figura en el directorio de outputs."""
    OUTPUTS_DIR.mkdir(exist_ok=True)
    fig.savefig(OUTPUTS_DIR / filename, bbox_inches="tight", dpi=200,
                facecolor="white", edgecolor="none")
    plt.close(fig)


# =============================================================================
# 1. EDA - OVERVIEW DEL DATASET
# =============================================================================

def plot_dataset_overview(df, filename="eda_01_dataset_overview.png"):
    """
    Panel resumen del dataset: volumen temporal, distribucion de resultados,
    partidos por tipo de torneo y cobertura geografica.
    """
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

    # --- 1. Partidos por año (linea temporal) ---
    ax1 = fig.add_subplot(gs[0, 0:2])
    yearly = df.groupby("year").size()
    ax1.fill_between(yearly.index, yearly.values, alpha=0.3, color=COLORS["secondary"])
    ax1.plot(yearly.index, yearly.values, color=COLORS["primary"], linewidth=2)
    ax1.set_title("Partidos internacionales por año (1872–2025)")
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Nº de partidos")
    # Marcar mundiales
    wc_years = [1930, 1950, 1970, 1990, 2010, 2022]
    for y in wc_years:
        if y in yearly.index:
            ax1.axvline(x=y, color=COLORS["accent"], alpha=0.3, linestyle="--", linewidth=0.8)
    ax1.annotate(f"Total: {len(df):,} partidos", xy=(0.02, 0.92),
                 xycoords="axes fraction", fontsize=12, fontweight="bold",
                 color=COLORS["primary"])

    # --- 2. Distribucion de resultados (donut) ---
    ax2 = fig.add_subplot(gs[0, 2])
    counts = df["result"].value_counts().sort_index()
    wedges, texts, autotexts = ax2.pie(
        counts.values, labels=RESULT_LABELS, colors=RESULT_COLORS,
        autopct="%1.1f%%", startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    )
    for t in autotexts:
        t.set_fontweight("bold")
        t.set_fontsize(10)
    ax2.set_title("Distribucion de resultados")

    # --- 3. Top 15 torneos por nº de partidos ---
    ax3 = fig.add_subplot(gs[1, 0])
    top_tournaments = df["tournament"].value_counts().head(15)
    colors_t = [COLORS["primary"] if "World Cup" in t or "Euro" in t or "Copa" in t
                else COLORS["secondary"] for t in top_tournaments.index]
    ax3.barh(range(len(top_tournaments)), top_tournaments.values, color=colors_t, alpha=0.85)
    ax3.set_yticks(range(len(top_tournaments)))
    ax3.set_yticklabels(top_tournaments.index, fontsize=9)
    ax3.invert_yaxis()
    ax3.set_title("Top 15 competiciones")
    ax3.set_xlabel("Nº de partidos")

    # --- 4. Partidos por continente (confederacion) ---
    ax4 = fig.add_subplot(gs[1, 1])
    home_confs = df["home_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")
    away_confs = df["away_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")
    all_confs = pd.concat([home_confs, away_confs])
    conf_series = all_confs.value_counts()
    conf_series = conf_series[conf_series.index != "Otro"]

    bars = ax4.bar(conf_series.index, conf_series.values,
                   color=[CONF_COLORS.get(c, "#999") for c in conf_series.index],
                   alpha=0.85, edgecolor="white", linewidth=1.5)
    ax4.set_title("Participaciones por confederacion")
    ax4.set_ylabel("Nº de participaciones")
    ax4.tick_params(axis="x", rotation=0)
    for bar, v in zip(bars, conf_series.values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                 f"{v:,}", ha="center", fontsize=9, fontweight="bold")

    # --- 5. Equipos unicos por decada ---
    ax5 = fig.add_subplot(gs[1, 2])
    df_copy = df.copy()
    df_copy["decade"] = (df_copy["year"] // 10) * 10
    teams_per_decade = df_copy.groupby("decade").apply(
        lambda x: len(set(x["home_team"]).union(set(x["away_team"])))
    )
    ax5.bar(teams_per_decade.index.astype(str), teams_per_decade.values,
            color=COLORS["secondary"], alpha=0.85, edgecolor="white", linewidth=1.5)
    ax5.set_title("Selecciones activas por decada")
    ax5.set_ylabel("Nº de equipos")
    ax5.tick_params(axis="x", rotation=45)

    fig.suptitle("EXPLORACION DEL DATASET — Partidos Internacionales de Futbol",
                 fontsize=16, fontweight="bold", y=1.01)
    save_fig(fig, filename)


def plot_goals_analysis(df, filename="eda_02_analisis_goles.png"):
    """
    Analisis profundo de goles: distribucion, tendencia historica,
    por tipo de torneo y diferencia de goles.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    df_copy = df.copy()
    df_copy["total_goals"] = df_copy["home_score"] + df_copy["away_score"]

    # --- 1. Distribucion de goles por partido ---
    ax = axes[0, 0]
    goal_counts = df_copy["total_goals"].value_counts().sort_index()
    goal_counts = goal_counts[goal_counts.index <= 12]
    bars = ax.bar(goal_counts.index, goal_counts.values, color=COLORS["secondary"],
                  alpha=0.85, edgecolor="white", linewidth=1)
    mean_goals = df_copy["total_goals"].mean()
    ax.axvline(x=mean_goals, color=COLORS["accent"], linestyle="--", linewidth=2,
               label=f"Media: {mean_goals:.2f} goles")
    ax.set_title("Distribucion de goles por partido")
    ax.set_xlabel("Goles totales")
    ax.set_ylabel("Nº de partidos")
    ax.legend(fontsize=11)
    # Highlight most common
    max_idx = goal_counts.idxmax()
    bars_list = list(bars)
    for i, b in enumerate(bars_list):
        if goal_counts.index[i] == max_idx:
            b.set_color(COLORS["accent"])

    # --- 2. Media de goles por decada ---
    ax = axes[0, 1]
    df_copy["decade"] = (df_copy["year"] // 10) * 10
    decade_goals = df_copy[df_copy["decade"] >= 1900].groupby("decade").agg(
        avg_goals=("total_goals", "mean"),
        avg_home=("home_score", "mean"),
        avg_away=("away_score", "mean"),
    )
    ax.plot(decade_goals.index, decade_goals["avg_goals"], "o-",
            color=COLORS["primary"], linewidth=2.5, markersize=8, label="Total", zorder=3)
    ax.fill_between(decade_goals.index, decade_goals["avg_home"],
                    decade_goals["avg_goals"], alpha=0.3, color=COLORS["success"],
                    label="Goles local")
    ax.fill_between(decade_goals.index, 0, decade_goals["avg_home"],
                    alpha=0.3, color=COLORS["accent"], label="Goles visitante")
    ax.set_title("Evolucion de la media de goles por decada")
    ax.set_xlabel("Decada")
    ax.set_ylabel("Goles por partido")
    ax.legend(fontsize=10)

    # --- 3. Goles por tipo de competicion (top 10) ---
    ax = axes[1, 0]
    top_tourn = df_copy["tournament"].value_counts().head(10).index
    tourn_goals = df_copy[df_copy["tournament"].isin(top_tourn)].groupby("tournament")["total_goals"].mean()
    tourn_goals = tourn_goals.sort_values(ascending=True)
    colors_bar = [COLORS["accent"] if "World Cup" in t else COLORS["secondary"]
                  for t in tourn_goals.index]
    ax.barh(range(len(tourn_goals)), tourn_goals.values, color=colors_bar, alpha=0.85)
    ax.set_yticks(range(len(tourn_goals)))
    ax.set_yticklabels(tourn_goals.index, fontsize=9)
    ax.set_title("Media de goles por competicion")
    ax.set_xlabel("Goles por partido")
    ax.axvline(x=mean_goals, color="gray", linestyle="--", alpha=0.5)
    for i, v in enumerate(tourn_goals.values):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=9)

    # --- 4. Heatmap goles local vs visitante ---
    ax = axes[1, 1]
    max_g = 6
    hs_clip = df_copy["home_score"].clip(upper=max_g).astype(int)
    as_clip = df_copy["away_score"].clip(upper=max_g).astype(int)
    heatmap_data = np.zeros((max_g + 1, max_g + 1))
    for hs_val, as_val in zip(hs_clip.values, as_clip.values):
        heatmap_data[hs_val, as_val] += 1
    heatmap_pct = heatmap_data / heatmap_data.sum() * 100

    sns.heatmap(heatmap_pct, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax,
                xticklabels=list(range(max_g)) + [f"{max_g}+"],
                yticklabels=list(range(max_g)) + [f"{max_g}+"],
                cbar_kws={"label": "% de partidos"}, linewidths=0.5, linecolor="white")
    ax.set_title("Frecuencia de marcadores (%)")
    ax.set_xlabel("Goles visitante")
    ax.set_ylabel("Goles local")

    fig.suptitle("ANALISIS DE GOLES — Patrones y Tendencias",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_home_advantage(df, filename="eda_03_ventaja_local.png"):
    """
    Evolucion historica de la ventaja de jugar en casa.
    Incluye: tasa de victoria local por decada, campo neutral vs local,
    y analisis por confederacion.
    """
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    df_copy = df.copy()

    # --- 1. Ventaja local por decada ---
    ax = axes[0]
    df_copy["decade"] = (df_copy["year"] // 10) * 10
    decade_results = df_copy[df_copy["decade"] >= 1900].groupby("decade")["result"].value_counts(normalize=True).unstack(fill_value=0)
    decade_results.columns = ["Visitante", "Empate", "Local"]

    ax.stackplot(decade_results.index,
                 decade_results["Visitante"] * 100,
                 decade_results["Empate"] * 100,
                 decade_results["Local"] * 100,
                 labels=["Victoria visitante", "Empate", "Victoria local"],
                 colors=RESULT_COLORS, alpha=0.8)
    ax.set_title("Evolucion de resultados por decada")
    ax.set_xlabel("Decada")
    ax.set_ylabel("Porcentaje (%)")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 100)

    # --- 2. Local vs neutral ---
    ax = axes[1]
    local_data = df_copy[~df_copy["neutral"]]
    neutral_data = df_copy[df_copy["neutral"]]

    categories = ["Campo local", "Campo neutral"]
    home_wins = [
        (local_data["result"] == 2).mean() * 100,
        (neutral_data["result"] == 2).mean() * 100,
    ]
    draws = [
        (local_data["result"] == 1).mean() * 100,
        (neutral_data["result"] == 1).mean() * 100,
    ]
    away_wins = [
        (local_data["result"] == 0).mean() * 100,
        (neutral_data["result"] == 0).mean() * 100,
    ]

    x = np.arange(len(categories))
    width = 0.25
    ax.bar(x - width, home_wins, width, label="Victoria local", color=RESULT_COLORS[2])
    ax.bar(x, draws, width, label="Empate", color=RESULT_COLORS[1])
    ax.bar(x + width, away_wins, width, label="Victoria visitante", color=RESULT_COLORS[0])
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Porcentaje (%)")
    ax.set_title("Impacto del factor campo")
    ax.legend(fontsize=9)
    for bars_group in [home_wins, draws, away_wins]:
        for i, v in enumerate(bars_group):
            offset = [-width, 0, width][[home_wins, draws, away_wins].index(bars_group)]
            ax.text(i + offset, v + 0.5, f"{v:.1f}%", ha="center", fontsize=9)

    # --- 3. Ventaja local por confederacion ---
    ax = axes[2]
    df_notneutral = df_copy[~df_copy["neutral"]].copy()
    df_notneutral["home_conf"] = df_notneutral["home_team"].map(TEAM_TO_CONFEDERATION)
    conf_home_wr = df_notneutral.groupby("home_conf")["result"].apply(
        lambda x: (x == 2).mean() * 100
    ).sort_values(ascending=True)
    conf_home_wr = conf_home_wr[conf_home_wr.index.isin(CONF_COLORS.keys())]

    bars = ax.barh(range(len(conf_home_wr)), conf_home_wr.values,
                   color=[CONF_COLORS.get(c, "#999") for c in conf_home_wr.index],
                   alpha=0.85, edgecolor="white", linewidth=1.5)
    ax.set_yticks(range(len(conf_home_wr)))
    ax.set_yticklabels(conf_home_wr.index)
    ax.set_title("Victoria local por confederacion")
    ax.set_xlabel("% de victorias en casa")
    ax.axvline(x=50, color="gray", linestyle="--", alpha=0.5)
    for i, v in enumerate(conf_home_wr.values):
        ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=10, fontweight="bold")

    fig.suptitle("VENTAJA DE JUGAR EN CASA — Analisis Historico",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_confederation_analysis(df, filename="eda_04_confederaciones.png"):
    """
    Analisis de rendimiento por confederacion: win rates,
    enfrentamientos inter-confederacion, fortaleza relativa.
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    df_copy = df[df["year"] >= 2000].copy()
    df_copy["home_conf"] = df_copy["home_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")
    df_copy["away_conf"] = df_copy["away_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")
    main_confs = list(CONF_COLORS.keys())

    # --- 1. Win rate general por confederacion ---
    ax = axes[0, 0]
    conf_stats = {}
    for conf in main_confs:
        home_mask = df_copy["home_conf"] == conf
        away_mask = df_copy["away_conf"] == conf
        wins_home = (df_copy.loc[home_mask, "result"] == 2).sum()
        wins_away = (df_copy.loc[away_mask, "result"] == 0).sum()
        total = home_mask.sum() + away_mask.sum()
        draws_home = (df_copy.loc[home_mask, "result"] == 1).sum()
        draws_away = (df_copy.loc[away_mask, "result"] == 1).sum()
        conf_stats[conf] = {
            "win_rate": (wins_home + wins_away) / max(total, 1) * 100,
            "draw_rate": (draws_home + draws_away) / max(total, 1) * 100,
            "matches": total,
        }

    confs_sorted = sorted(conf_stats.keys(), key=lambda c: conf_stats[c]["win_rate"], reverse=True)
    wr = [conf_stats[c]["win_rate"] for c in confs_sorted]
    dr = [conf_stats[c]["draw_rate"] for c in confs_sorted]
    lr = [100 - w - d for w, d in zip(wr, dr)]

    x = np.arange(len(confs_sorted))
    ax.bar(x, wr, label="Victoria", color=COLORS["success"], alpha=0.85)
    ax.bar(x, dr, bottom=wr, label="Empate", color=COLORS["draw"], alpha=0.85)
    ax.bar(x, lr, bottom=[w + d for w, d in zip(wr, dr)], label="Derrota",
           color=COLORS["accent"], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(confs_sorted)
    ax.set_ylabel("Porcentaje (%)")
    ax.set_title("Rendimiento global por confederacion (2000+)")
    ax.legend(loc="upper right", fontsize=9)
    for i, w in enumerate(wr):
        ax.text(i, w / 2, f"{w:.1f}%", ha="center", va="center",
                fontweight="bold", fontsize=10, color="white")

    # --- 2. Heatmap inter-confederacion ---
    ax = axes[0, 1]
    inter_conf = df_copy[
        (df_copy["home_conf"].isin(main_confs)) &
        (df_copy["away_conf"].isin(main_confs)) &
        (df_copy["home_conf"] != df_copy["away_conf"])
    ].copy()

    matrix = pd.DataFrame(0.0, index=main_confs, columns=main_confs)
    count_matrix = pd.DataFrame(0, index=main_confs, columns=main_confs)
    # Vectorizado: contar victorias y partidos por par de confederaciones
    home_wins = inter_conf[inter_conf["result"] == 2]
    away_wins = inter_conf[inter_conf["result"] == 0]
    for (hc, ac), cnt in home_wins.groupby(["home_conf", "away_conf"]).size().items():
        matrix.loc[hc, ac] += cnt
    for (hc, ac), cnt in away_wins.groupby(["home_conf", "away_conf"]).size().items():
        matrix.loc[ac, hc] += cnt
    for (hc, ac), cnt in inter_conf.groupby(["home_conf", "away_conf"]).size().items():
        count_matrix.loc[hc, ac] += cnt
        count_matrix.loc[ac, hc] += cnt

    # Win rate de fila vs columna
    wr_matrix = matrix / count_matrix.replace(0, np.nan) * 100
    mask = np.eye(len(main_confs), dtype=bool)
    sns.heatmap(wr_matrix, annot=True, fmt=".0f", cmap="RdYlGn", center=50,
                ax=ax, mask=mask, linewidths=1, linecolor="white",
                cbar_kws={"label": "% de victorias"}, vmin=20, vmax=80)
    ax.set_title("Enfrentamientos inter-confederacion\n(% victoria fila vs columna, 2000+)")

    # --- 3. Top 20 selecciones por win rate (minimo 50 partidos, 2010+) ---
    ax = axes[1, 0]
    df_recent = df[df["year"] >= 2010].copy()
    team_stats = {}
    all_teams = set(df_recent["home_team"]).union(set(df_recent["away_team"]))
    for team in all_teams:
        home_mask = df_recent["home_team"] == team
        away_mask = df_recent["away_team"] == team
        wins = (df_recent.loc[home_mask, "result"] == 2).sum() + (df_recent.loc[away_mask, "result"] == 0).sum()
        total = home_mask.sum() + away_mask.sum()
        if total >= 50:
            team_stats[team] = {"win_rate": wins / total * 100, "matches": total}

    top20 = sorted(team_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)[:20]
    teams_names = [t[0] for t in top20]
    teams_wr = [t[1]["win_rate"] for t in top20]
    teams_confs = [TEAM_TO_CONFEDERATION.get(t, "Otro") for t in teams_names]

    bars = ax.barh(range(len(teams_names)), teams_wr,
                   color=[CONF_COLORS.get(c, "#999") for c in teams_confs],
                   alpha=0.85, edgecolor="white", linewidth=1)
    ax.set_yticks(range(len(teams_names)))
    ax.set_yticklabels(teams_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_title("Top 20 selecciones por win rate (2010+, min 50 partidos)")
    ax.set_xlabel("Win rate (%)")
    for i, v in enumerate(teams_wr):
        ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)

    # Leyenda de confederaciones
    handles = [mpatches.Patch(color=c, label=l) for l, c in CONF_COLORS.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=8, ncol=2)

    # --- 4. Evolucion de fortaleza por confederacion (rolling 5 años) ---
    ax = axes[1, 1]
    df_all = df[df["year"] >= 1970].copy()
    df_all["home_conf"] = df_all["home_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")
    df_all["away_conf"] = df_all["away_team"].map(TEAM_TO_CONFEDERATION).fillna("Otro")

    years_range = range(1975, df_all["year"].max() + 1)
    for conf in ["UEFA", "CONMEBOL", "CONCACAF", "CAF", "AFC"]:
        wr_evolution = []
        for yr in years_range:
            mask_yr = (df_all["year"] >= yr - 4) & (df_all["year"] <= yr)
            sub = df_all[mask_yr]
            home_m = sub["home_conf"] == conf
            away_m = sub["away_conf"] == conf
            wins = (sub.loc[home_m, "result"] == 2).sum() + (sub.loc[away_m, "result"] == 0).sum()
            total = home_m.sum() + away_m.sum()
            wr_evolution.append(wins / max(total, 1) * 100)
        ax.plot(list(years_range), wr_evolution, label=conf,
                color=CONF_COLORS[conf], linewidth=2, alpha=0.85)

    ax.set_title("Evolucion de fortaleza por confederacion\n(win rate rolling 5 años)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Win rate (%)")
    ax.legend(fontsize=9)
    ax.axhline(y=50, color="gray", linestyle="--", alpha=0.3)

    fig.suptitle("ANALISIS POR CONFEDERACION — Rendimiento y Tendencias",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_elo_analysis(df, filename="eda_05_analisis_elo.png"):
    """
    Analisis ELO: evolucion de los favoritos, distribucion actual,
    ELO de los participantes del WC2026.
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    # --- 1. Evolucion ELO top selecciones ---
    ax = axes[0, 0]
    top_teams = ["Spain", "Argentina", "France", "Brazil", "England",
                 "Germany", "Netherlands", "Portugal", "Italy", "Belgium"]
    cmap = plt.cm.tab10
    df_recent = df[df["year"] >= 2000].copy()

    for idx, team in enumerate(top_teams):
        # Combinar datos como local y visitante
        home_data = df_recent.loc[df_recent["home_team"] == team, ["date", "home_elo"]].rename(
            columns={"home_elo": "elo"})
        away_data = df_recent.loc[df_recent["away_team"] == team, ["date", "away_elo"]].rename(
            columns={"away_elo": "elo"})
        team_data = pd.concat([home_data, away_data]).sort_values("date")
        if len(team_data) > 5:
            # Smooth con rolling
            team_data["elo_smooth"] = team_data["elo"].rolling(5, min_periods=1).mean()
            ax.plot(team_data["date"], team_data["elo_smooth"],
                    label=team, color=cmap(idx), linewidth=1.8, alpha=0.85)

    ax.set_title("Evolucion ELO — Top 10 selecciones (2000–presente)")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Rating ELO")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.axhline(y=1500, color="gray", linestyle="--", alpha=0.3)

    # --- 2. Distribucion ELO actual (todas las selecciones) ---
    ax = axes[0, 1]
    # Obtener ultimo ELO de cada equipo (vectorizado)
    df_recent_elo = df[df["year"] >= 2020].sort_values("date")
    home_elos = df_recent_elo.groupby("home_team")["home_elo"].last()
    away_elos = df_recent_elo.groupby("away_team")["away_elo"].last()
    latest_elos = {**home_elos.to_dict(), **away_elos.to_dict()}
    elo_values = list(latest_elos.values())

    ax.hist(elo_values, bins=40, color=COLORS["secondary"], alpha=0.7,
            edgecolor="white", linewidth=1)
    ax.axvline(x=np.mean(elo_values), color=COLORS["accent"], linestyle="--",
               linewidth=2, label=f"Media: {np.mean(elo_values):.0f}")
    ax.axvline(x=np.median(elo_values), color=COLORS["success"], linestyle="--",
               linewidth=2, label=f"Mediana: {np.median(elo_values):.0f}")
    ax.set_title("Distribucion de ratings ELO actuales")
    ax.set_xlabel("Rating ELO")
    ax.set_ylabel("Nº de selecciones")
    ax.legend(fontsize=10)

    # --- 3. ELO de los 48 participantes del WC2026 ---
    ax = axes[1, 0]
    wc_teams = []
    for group, teams in WORLD_CUP_2026_GROUPS.items():
        for team in teams:
            elo = latest_elos.get(team, 1500)
            conf = TEAM_TO_CONFEDERATION.get(team, "Otro")
            wc_teams.append({"team": team, "elo": elo, "group": group, "conf": conf})
    wc_df = pd.DataFrame(wc_teams).sort_values("elo", ascending=True)

    bars = ax.barh(range(len(wc_df)), wc_df["elo"].values,
                   color=[CONF_COLORS.get(c, "#999") for c in wc_df["conf"]],
                   alpha=0.85, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(wc_df)))
    ax.set_yticklabels(wc_df["team"].values, fontsize=7)
    ax.set_title("ELO de los 48 participantes — Mundial 2026")
    ax.set_xlabel("Rating ELO")
    ax.axvline(x=1500, color="gray", linestyle="--", alpha=0.3)

    handles = [mpatches.Patch(color=c, label=l) for l, c in CONF_COLORS.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=8, ncol=2)

    # --- 4. Fortaleza media por grupo WC2026 ---
    ax = axes[1, 1]
    group_elos = {}
    for group, teams in sorted(WORLD_CUP_2026_GROUPS.items()):
        elos = [latest_elos.get(t, 1500) for t in teams]
        group_elos[group] = {
            "mean": np.mean(elos),
            "max": max(elos),
            "min": min(elos),
            "std": np.std(elos),
        }

    groups = sorted(group_elos.keys())
    means = [group_elos[g]["mean"] for g in groups]
    maxs = [group_elos[g]["max"] for g in groups]
    mins = [group_elos[g]["min"] for g in groups]

    x = np.arange(len(groups))
    ax.bar(x, means, color=COLORS["secondary"], alpha=0.7, label="Media", edgecolor="white")
    ax.errorbar(x, means,
                yerr=[np.array(means) - np.array(mins), np.array(maxs) - np.array(means)],
                fmt="none", color=COLORS["primary"], capsize=5, linewidth=2)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Grupo {g}" for g in groups], rotation=45, fontsize=9)
    ax.set_ylabel("Rating ELO")
    ax.set_title("Fortaleza por grupo — Mundial 2026\n(media + rango)")
    ax.axhline(y=1500, color="gray", linestyle="--", alpha=0.3)

    # Colorear el grupo mas fuerte y mas debil
    strongest = groups[np.argmax(means)]
    weakest = groups[np.argmin(means)]
    ax.annotate(f"Mas fuerte", xy=(groups.index(strongest), max(means) + 10),
                ha="center", fontsize=9, color=COLORS["success"], fontweight="bold")

    fig.suptitle("SISTEMA ELO — Ratings y Analisis de Fortaleza",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_world_cup_history(df, filename="eda_06_mundiales_historicos.png"):
    """
    Analisis historico de Copas del Mundo: goles, resultados,
    ventaja de sede, evolucion.
    """
    wc = df[df["tournament"] == "FIFA World Cup"].copy()
    wc["total_goals"] = wc["home_score"] + wc["away_score"]

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    # --- 1. Goles por edicion del Mundial ---
    ax = axes[0, 0]
    wc_editions = wc.groupby("year").agg(
        total_goals=("total_goals", "sum"),
        avg_goals=("total_goals", "mean"),
        n_matches=("total_goals", "count"),
    ).reset_index()

    ax2 = ax.twinx()
    ax.bar(wc_editions["year"], wc_editions["total_goals"],
           color=COLORS["secondary"], alpha=0.6, width=3, label="Goles totales")
    ax2.plot(wc_editions["year"], wc_editions["avg_goals"], "o-",
             color=COLORS["accent"], linewidth=2, markersize=6, label="Media/partido")
    ax.set_xlabel("Año")
    ax.set_ylabel("Goles totales", color=COLORS["secondary"])
    ax2.set_ylabel("Media de goles/partido", color=COLORS["accent"])
    ax.set_title("Goles en cada Copa del Mundo")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    # --- 2. Resultados en mundiales (area chart) ---
    ax = axes[0, 1]
    wc_results = wc.groupby("year")["result"].value_counts(normalize=True).unstack(fill_value=0)
    if 0 in wc_results.columns and 1 in wc_results.columns and 2 in wc_results.columns:
        ax.stackplot(wc_results.index,
                     wc_results[0] * 100, wc_results[1] * 100, wc_results[2] * 100,
                     labels=RESULT_LABELS, colors=RESULT_COLORS, alpha=0.8)
    ax.set_title("Distribucion de resultados por Mundial")
    ax.set_xlabel("Año")
    ax.set_ylabel("Porcentaje (%)")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 100)

    # --- 3. Partidos en campo neutral vs no neutral en mundiales ---
    ax = axes[1, 0]
    wc_neutral = wc.groupby("year")["neutral"].mean() * 100
    ax.bar(wc_neutral.index, wc_neutral.values, width=3,
           color=COLORS["primary"], alpha=0.7)
    ax.set_title("% de partidos en campo neutral (por edicion)")
    ax.set_xlabel("Año")
    ax.set_ylabel("% campo neutral")
    ax.set_ylim(0, 105)

    # --- 4. Los equipos con mas partidos mundialistas ---
    ax = axes[1, 1]
    home_counts = wc["home_team"].value_counts()
    away_counts = wc["away_team"].value_counts()
    team_wc_total = home_counts.add(away_counts, fill_value=0).astype(int).sort_values(ascending=False)
    top_wc = list(team_wc_total.head(20).items())
    teams_n = [t[0] for t in top_wc]
    matches_n = [t[1] for t in top_wc]
    confs_n = [TEAM_TO_CONFEDERATION.get(t, "Otro") for t in teams_n]

    bars = ax.barh(range(len(teams_n)), matches_n,
                   color=[CONF_COLORS.get(c, "#999") for c in confs_n],
                   alpha=0.85, edgecolor="white", linewidth=1)
    ax.set_yticks(range(len(teams_n)))
    ax.set_yticklabels(teams_n, fontsize=9)
    ax.invert_yaxis()
    ax.set_title("Top 20 selecciones con mas partidos mundialistas")
    ax.set_xlabel("Nº de partidos")

    fig.suptitle("COPAS DEL MUNDO — Analisis Historico",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_feature_distributions(df, filename="eda_07_feature_distributions.png"):
    """
    Distribucion de las features mas importantes segmentadas por resultado.
    Violin plots para ver como se separan las clases.
    """
    key_features = [
        ("elo_diff", "Diferencia de ELO"),
        ("form_points_diff", "Diferencia de puntos forma"),
        ("home_elo", "ELO local"),
        ("h2h_dominance", "Dominancia H2H"),
        ("home_streak", "Racha local"),
        ("elo_expected_home", "Prob. esperada ELO"),
        ("home_conf_strength", "Fortaleza conf. local"),
        ("rest_advantage", "Ventaja descanso"),
        ("home_clean_sheet_pct", "% porteria imbatida local"),
    ]

    n_feats = len(key_features)
    cols = 3
    rows = (n_feats + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(18, 5 * rows))
    axes_flat = axes.flatten()

    df_plot = df[df["year"] >= 2000].copy()
    df_plot["resultado"] = df_plot["result"].map(
        {0: "Visitante", 1: "Empate", 2: "Local"}
    )

    for idx, (feat, title) in enumerate(key_features):
        ax = axes_flat[idx]
        if feat in df_plot.columns:
            sns.violinplot(data=df_plot, x="resultado", y=feat, ax=ax,
                           palette={"Visitante": RESULT_COLORS[0],
                                    "Empate": RESULT_COLORS[1],
                                    "Local": RESULT_COLORS[2]},
                           order=["Visitante", "Empate", "Local"],
                           inner="quartile", alpha=0.8)
            ax.set_title(title)
            ax.set_xlabel("")
            ax.set_ylabel(feat)

    for idx in range(n_feats, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fig.suptitle("DISTRIBUCION DE FEATURES CLAVE — Por Resultado",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_correlation_matrix(df, feature_cols, filename="eda_08_correlacion_matrix.png"):
    """
    Heatmap de correlacion completa entre features + target.
    """
    df_corr = df[df["year"] >= 2000][feature_cols + [TARGET]].corr()

    fig, ax = plt.subplots(figsize=(20, 18))
    mask = np.triu(np.ones_like(df_corr, dtype=bool), k=1)
    sns.heatmap(df_corr, mask=mask, annot=False, cmap="RdBu_r", center=0,
                ax=ax, square=True, linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Correlacion", "shrink": 0.8},
                vmin=-1, vmax=1)
    ax.set_title("Matriz de correlacion — 47 features + target",
                 fontsize=16, fontweight="bold", pad=20)
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)

    fig.tight_layout()
    save_fig(fig, filename)


def plot_feature_target_correlation(df, feature_cols, target,
                                     filename="eda_09_correlacion_target.png"):
    """Correlacion de cada feature con el target, coloreada por signo."""
    df_model = df[df["year"] >= 2000]
    correlations = df_model[feature_cols + [target]].corr()[target].drop(target).sort_values()

    fig, ax = plt.subplots(figsize=(12, max(10, len(feature_cols) * 0.3)))
    colors = [COLORS["success"] if v > 0 else COLORS["accent"] for v in correlations.values]
    bars = ax.barh(range(len(correlations)), correlations.values, color=colors, alpha=0.85,
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(correlations)))
    ax.set_yticklabels(correlations.index, fontsize=9)
    ax.set_title("Correlacion de features con el resultado",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Coeficiente de correlacion")
    ax.axvline(x=0, color="black", linewidth=0.8)

    # Highlight top 5
    top5_pos = correlations.nlargest(5).index
    top5_neg = correlations.nsmallest(5).index
    for i, feat in enumerate(correlations.index):
        if feat in top5_pos or feat in top5_neg:
            ax.text(correlations.values[i], i,
                    f" {correlations.values[i]:.3f}", va="center", fontsize=8,
                    fontweight="bold")

    fig.tight_layout()
    save_fig(fig, filename)


def plot_wc2026_groups_preview(df, filename="eda_10_wc2026_grupos.png"):
    """
    Preview visual de los 12 grupos del Mundial 2026.
    Muestra ELO de cada equipo con barras coloreadas por confederacion.
    """
    fig, axes = plt.subplots(3, 4, figsize=(22, 16))
    axes_flat = axes.flatten()

    # Obtener ELOs actuales (vectorizado)
    df_recent_elo = df[df["year"] >= 2020].sort_values("date")
    home_elos = df_recent_elo.groupby("home_team")["home_elo"].last()
    away_elos = df_recent_elo.groupby("away_team")["away_elo"].last()
    latest_elos = {**home_elos.to_dict(), **away_elos.to_dict()}

    for idx, (group_name, teams) in enumerate(sorted(WORLD_CUP_2026_GROUPS.items())):
        ax = axes_flat[idx]
        elos = [latest_elos.get(t, 1500) for t in teams]
        confs = [TEAM_TO_CONFEDERATION.get(t, "Otro") for t in teams]
        colors = [CONF_COLORS.get(c, "#999") for c in confs]

        # Ordenar por ELO descendente
        sorted_data = sorted(zip(teams, elos, colors), key=lambda x: x[1], reverse=True)
        teams_s, elos_s, colors_s = zip(*sorted_data)

        bars = ax.barh(range(len(teams_s)), elos_s, color=colors_s,
                       alpha=0.85, edgecolor="white", linewidth=1.5)
        ax.set_yticks(range(len(teams_s)))
        ax.set_yticklabels(teams_s, fontsize=10, fontweight="bold")
        ax.set_title(f"Grupo {group_name}", fontsize=13, fontweight="bold")
        ax.set_xlim(1200, max(max(elos) + 150, 1900))
        ax.axvline(x=1500, color="gray", linestyle="--", alpha=0.3)

        # Avg ELO del grupo
        avg = np.mean(elos_s)
        ax.text(0.95, 0.05, f"Media: {avg:.0f}",
                transform=ax.transAxes, fontsize=9, ha="right",
                color=COLORS["primary"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        for bar, elo in zip(bars, elos_s):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                    f"{elo:.0f}", va="center", fontsize=9, fontweight="bold")

    # Leyenda global
    handles = [mpatches.Patch(color=c, label=l) for l, c in CONF_COLORS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=6, fontsize=11,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("MUNDIAL 2026 — Grupos y Rating ELO de Participantes",
                 fontsize=18, fontweight="bold", y=1.01)
    fig.tight_layout()
    save_fig(fig, filename)


# =============================================================================
# 2. MODELO - EVALUACION Y DIAGNOSTICO
# =============================================================================

def plot_model_comparison(results, filename="model_01_comparacion.png"):
    """Compara accuracy y log loss de los modelos entrenados."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    names = [r["name"] for r in results]
    train_accs = [r["train_acc"] for r in results]
    val_accs = [r["val_acc"] for r in results]
    val_lls = [r["val_logloss"] for r in results]

    # --- Accuracy ---
    ax = axes[0]
    x = np.arange(len(names))
    width = 0.35
    b1 = ax.bar(x - width/2, train_accs, width, label="Train",
                color=COLORS["secondary"], alpha=0.85, edgecolor="white")
    b2 = ax.bar(x + width/2, val_accs, width, label="Validation",
                color=COLORS["success"], alpha=0.85, edgecolor="white")
    ax.set_title("Accuracy por modelo")
    ax.set_ylabel("Accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0.3, 0.75)
    # Valores sobre barras
    for bars in [b1, b2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f"{bar.get_height():.3f}", ha="center", fontsize=8)

    # --- Log Loss ---
    ax = axes[1]
    colors_ll = [COLORS["accent"] if v == min(val_lls) else COLORS["secondary"]
                 for v in val_lls]
    bars = ax.barh(names, val_lls, color=colors_ll, alpha=0.85,
                   edgecolor="white", linewidth=1.5)
    ax.set_title("Log Loss en Validation (menor = mejor)")
    ax.set_xlabel("Log Loss")
    for bar, v in zip(bars, val_lls):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f"{v:.4f}", va="center", fontsize=10, fontweight="bold")

    fig.suptitle("COMPARACION DE MODELOS", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


def plot_confusion_matrix(y_true, y_pred, title="", filename="model_02_confusion.png"):
    """Matriz de confusion normalizada y absoluta."""
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[0],
                xticklabels=RESULT_LABELS, yticklabels=RESULT_LABELS,
                linewidths=1, linecolor="white")
    axes[0].set_title(f"Matriz de confusion (absoluta) {title}")
    axes[0].set_ylabel("Real")
    axes[0].set_xlabel("Predicho")

    sns.heatmap(cm_norm, annot=True, fmt=".1%", cmap="Blues", ax=axes[1],
                xticklabels=RESULT_LABELS, yticklabels=RESULT_LABELS,
                linewidths=1, linecolor="white")
    axes[1].set_title(f"Matriz de confusion (normalizada) {title}")
    axes[1].set_ylabel("Real")
    axes[1].set_xlabel("Predicho")

    fig.tight_layout()
    save_fig(fig, filename)


def plot_feature_importance(model, feature_cols, top_n=25,
                            filename="model_03_feature_importance.png"):
    """Importancia de features con barras horizontales profesionales."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).mean(axis=0)
    else:
        print("El modelo no tiene feature_importances_ ni coef_")
        return

    idx = np.argsort(importances)[-top_n:]
    top_feats = [feature_cols[i] for i in idx]
    top_imps = importances[idx]

    fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.4)))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, top_n))
    bars = ax.barh(range(len(idx)), top_imps, color=colors,
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels(top_feats, fontsize=10)
    ax.set_title(f"Top {top_n} features mas importantes",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Importancia (gain)")

    # Porcentaje relativo
    total_imp = importances.sum()
    for bar, imp in zip(bars, top_imps):
        pct = imp / total_imp * 100
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f"{pct:.1f}%", va="center", fontsize=9)

    fig.tight_layout()
    save_fig(fig, filename)


def plot_calibration(y_true, y_proba, class_names=None,
                     filename="model_04_calibracion.png"):
    """Diagrama de fiabilidad (calibracion) por clase."""
    if class_names is None:
        class_names = RESULT_LABELS

    n_classes = y_proba.shape[1]
    fig, axes = plt.subplots(1, n_classes, figsize=(6 * n_classes, 6))

    for i in range(n_classes):
        ax = axes[i]
        y_binary = (y_true == i).astype(int)
        prob_true, prob_pred = calibration_curve(
            y_binary, y_proba[:, i], n_bins=10, strategy="uniform"
        )
        ax.plot(prob_pred, prob_true, "s-", label="Modelo",
                color=RESULT_COLORS[i], linewidth=2, markersize=8)
        ax.plot([0, 1], [0, 1], "--", color="gray", label="Calibracion perfecta")
        ax.fill_between(prob_pred, prob_true, prob_pred, alpha=0.15,
                        color=RESULT_COLORS[i])
        ax.set_title(f"Calibracion: {class_names[i]}")
        ax.set_xlabel("Probabilidad predicha")
        ax.set_ylabel("Frecuencia real")
        ax.legend(fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    fig.suptitle("DIAGRAMAS DE FIABILIDAD — Calibracion del Modelo",
                 fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, filename)


# =============================================================================
# 3. MUNDIAL 2026 - SIMULACION
# =============================================================================

def plot_monte_carlo_results(mc_results, n_simulations=10000, top_n=20,
                             filename="wc_01_probabilidades_campeon.png"):
    """Probabilidades de ser campeon — grafica principal del TFG."""
    top = mc_results.head(top_n)

    fig, ax = plt.subplots(figsize=(14, 10))

    # Gradiente de colores
    colors = plt.cm.RdYlGn(np.linspace(0.15, 0.95, top_n))[::-1]
    confs = [TEAM_TO_CONFEDERATION.get(t, "Otro") for t in top["team"]]
    bar_colors = [CONF_COLORS.get(c, "#999") for c in confs]

    bars = ax.barh(range(top_n), top["champion_pct"], color=bar_colors,
                   alpha=0.9, edgecolor="white", linewidth=1.5, height=0.7)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top["team"], fontsize=11, fontweight="bold")
    ax.set_xlabel("Probabilidad de ser campeon (%)", fontsize=12)
    ax.invert_yaxis()

    for bar, pct in zip(bars, top["champion_pct"]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f"{pct:.1f}%", va="center", fontweight="bold", fontsize=11)

    # Leyenda de confederaciones
    handles = [mpatches.Patch(color=c, label=l) for l, c in CONF_COLORS.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=10, ncol=2)

    ax.set_title(f"PREDICCION MUNDIAL 2026 — Probabilidad de ser Campeon\n"
                 f"Basado en {n_simulations:,} simulaciones Monte Carlo",
                 fontsize=15, fontweight="bold", pad=15)

    fig.tight_layout()
    save_fig(fig, filename)


def plot_tournament_progression(mc_results, top_n=20,
                                filename="wc_02_progresion_torneo.png"):
    """Heatmap de probabilidad de llegar a cada ronda."""
    top = mc_results.head(top_n)

    rounds = ["r32_pct", "r16_pct", "qf_pct", "sf_pct", "final_pct", "champion_pct"]
    round_names = ["R32", "R16", "Cuartos", "Semis", "Final", "Campeon"]

    available = [r for r in rounds if r in top.columns]
    available_names = [round_names[rounds.index(r)] for r in available]
    data = top[available].values

    fig, ax = plt.subplots(figsize=(12, max(10, top_n * 0.5)))
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(available_names)))
    ax.set_xticklabels(available_names, fontsize=12, fontweight="bold")
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top["team"], fontsize=10, fontweight="bold")

    for i in range(top_n):
        for j in range(len(available)):
            val = data[i, j]
            text = f"{val:.1f}%"
            color = "white" if val > 50 else "black"
            ax.text(j, i, text, ha="center", va="center", color=color,
                    fontsize=9, fontweight="bold" if val > 30 else "normal")

    ax.set_title("Probabilidad de alcanzar cada ronda — Mundial 2026",
                 fontsize=14, fontweight="bold", pad=15)
    fig.colorbar(im, ax=ax, label="Probabilidad (%)", shrink=0.8)

    fig.tight_layout()
    save_fig(fig, filename)


def plot_group_predictions(group_standings, filename="wc_03_prediccion_grupos.png"):
    """Prediccion de fase de grupos con diseño profesional."""
    n_groups = len(group_standings)
    cols = 4
    rows = (n_groups + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(24, 5 * rows))
    axes_flat = axes.flatten() if n_groups > 1 else [axes]

    for idx, (group_name, standings) in enumerate(sorted(group_standings.items())):
        ax = axes_flat[idx]
        teams = standings["team"].tolist()
        points = standings["points"].tolist()
        gd = standings["gd"].tolist()
        confs = [TEAM_TO_CONFEDERATION.get(t, "Otro") for t in teams]

        # Verde = clasifica (top 2), naranja = posible 3ro, rojo = eliminado
        bar_colors = [
            COLORS["success"] if i < 2 else
            (COLORS["warning"] if i == 2 else COLORS["accent"])
            for i in range(len(teams))
        ]

        bars = ax.barh(range(len(teams)), points, color=bar_colors,
                       alpha=0.85, edgecolor="white", linewidth=2, height=0.6)
        ax.set_yticks(range(len(teams)))
        ax.set_yticklabels(teams, fontsize=10, fontweight="bold")
        ax.set_title(f"Grupo {group_name}", fontsize=13, fontweight="bold",
                     pad=10)
        ax.set_xlabel("Puntos")
        ax.invert_yaxis()
        ax.set_xlim(0, 10)

        for i, (bar, pt, gd_val) in enumerate(zip(bars, points, gd)):
            ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
                    f"{pt}pts (GD:{gd_val:+d})", va="center", fontsize=9,
                    fontweight="bold")

    for idx in range(n_groups, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fig.suptitle("PREDICCION FASE DE GRUPOS — Mundial 2026\n"
                 "Verde = clasifica | Naranja = posible 3er clasificado | Rojo = eliminado",
                 fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_fig(fig, filename)


# =============================================================================
# FUNCION PRINCIPAL: GENERAR TODO EL EDA
# =============================================================================

def generate_full_eda(df, feature_cols=None, target=None):
    """
    Genera todas las graficas EDA de una sola vez.

    Args:
        df: DataFrame con features ya construidas (output de build_features)
        feature_cols: lista de columnas de features (default: FEATURE_COLS)
        target: nombre de la columna target (default: TARGET)
    """
    if feature_cols is None:
        feature_cols = FEATURE_COLS
    if target is None:
        target = TARGET

    setup_style()

    print("Generando EDA completo...")
    print("  [1/10] Dataset overview...")
    plot_dataset_overview(df)
    print("  [2/10] Analisis de goles...")
    plot_goals_analysis(df)
    print("  [3/10] Ventaja de local...")
    plot_home_advantage(df)
    print("  [4/10] Analisis por confederacion...")
    plot_confederation_analysis(df)
    print("  [5/10] Analisis ELO...")
    plot_elo_analysis(df)
    print("  [6/10] Mundiales historicos...")
    plot_world_cup_history(df)
    print("  [7/10] Distribucion de features...")
    plot_feature_distributions(df)
    print("  [8/10] Matriz de correlacion...")
    plot_correlation_matrix(df, feature_cols)
    print("  [9/10] Correlacion con target...")
    plot_feature_target_correlation(df, feature_cols, target)
    print("  [10/10] Preview grupos WC2026...")
    plot_wc2026_groups_preview(df)
    print("EDA completo! 10 graficas generadas en outputs/")
