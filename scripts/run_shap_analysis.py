"""
Analisis SHAP del modelo de prediccion.
Genera graficas de importancia de variables para la memoria del TFG.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model.config import FEATURE_COLS, OUTPUTS_DIR, MODELS_DIR
from model.data.loader import load_results
from model.features.engineering import build_features, prepare_splits, compute_sample_weights


def main():
    print("=" * 60)
    print("ANALISIS SHAP - World Cup 2026 Predictor")
    print("=" * 60)

    # 1. Cargar datos y construir features
    print("\n[1/5] Cargando datos y construyendo features...")
    df = load_results()
    df = build_features(df)
    splits = prepare_splits(df)

    # 2. Cargar modelo entrenado
    print("[2/5] Cargando modelo entrenado...")
    model_path = MODELS_DIR / "best_model.joblib"
    model = joblib.load(model_path)
    print(f"  Modelo: {type(model).__name__}")

    # Extraer el modelo base si esta calibrado
    if hasattr(model, 'estimator'):
        base_model = model.estimator
        print(f"  Modelo base (dentro de calibracion): {type(base_model).__name__}")
    elif hasattr(model, 'calibrated_classifiers_'):
        # CalibratedClassifierCV - extraer el primer estimador base
        base_model = model.calibrated_classifiers_[0].estimator
        print(f"  Modelo base (dentro de CalibratedCV): {type(base_model).__name__}")
    else:
        base_model = model

    # 3. Calcular SHAP values
    print("[3/5] Calculando SHAP values (esto puede tardar unos minutos)...")
    X_val = splits["X_val"]

    # Usar TreeExplainer con output_margin para evitar bugs con base_score multiclase
    try:
        explainer = shap.TreeExplainer(base_model, feature_perturbation="tree_path_dependent")
        shap_values = explainer.shap_values(X_val)
        print(f"  SHAP values calculados con TreeExplainer")
    except Exception as e1:
        print(f"  TreeExplainer fallo: {e1}")
        print("  Usando Explainer generico con muestra reducida...")
        X_sample = X_val.sample(min(200, len(X_val)), random_state=42)
        explainer = shap.Explainer(base_model.predict_proba, X_sample)
        shap_values_obj = explainer(X_sample)
        shap_values = [shap_values_obj.values[:, :, i] for i in range(3)]
        X_val = X_sample

    if isinstance(shap_values, list):
        print(f"  Clases: {len(shap_values)}, Shape por clase: {shap_values[0].shape}")
    elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        # Shape (n_samples, n_features, n_classes) -> convertir a lista
        shap_values = [shap_values[:, :, i] for i in range(shap_values.shape[2])]
        print(f"  Clases: {len(shap_values)}, Shape por clase: {shap_values[0].shape}")
    else:
        print(f"  Shape: {shap_values.shape}")

    # 4. Generar graficas
    print("[4/5] Generando graficas SHAP...")
    OUTPUTS_DIR.mkdir(exist_ok=True)

    # Nombres legibles para las features
    feature_names_map = {
        "home_elo": "ELO local",
        "away_elo": "ELO visitante",
        "elo_diff": "Diferencia ELO",
        "elo_expected_home": "Prob. esperada ELO",
        "home_form_wins": "Victorias recientes (L)",
        "home_form_draws": "Empates recientes (L)",
        "home_form_losses": "Derrotas recientes (L)",
        "home_form_gf": "Goles favor recientes (L)",
        "home_form_gc": "Goles contra recientes (L)",
        "home_form_points": "Puntos recientes (L)",
        "home_form_gd": "Dif. goles recientes (L)",
        "away_form_wins": "Victorias recientes (V)",
        "away_form_draws": "Empates recientes (V)",
        "away_form_losses": "Derrotas recientes (V)",
        "away_form_gf": "Goles favor recientes (V)",
        "away_form_gc": "Goles contra recientes (V)",
        "away_form_points": "Puntos recientes (V)",
        "away_form_gd": "Dif. goles recientes (V)",
        "h2h_home_wins": "H2H victorias local",
        "h2h_away_wins": "H2H victorias visitante",
        "h2h_draws": "H2H empates",
        "h2h_home_goals": "H2H goles local",
        "h2h_away_goals": "H2H goles visitante",
        "h2h_dominance": "H2H dominancia",
        "form_points_diff": "Dif. puntos forma",
        "form_gd_diff": "Dif. gol diferencia",
        "form_gf_diff": "Dif. goles favor",
        "neutral_int": "Campo neutral",
        "tournament_weight": "Peso del torneo",
        "is_competitive": "Partido competitivo",
        "home_conf_strength": "Fortaleza conf. local",
        "away_conf_strength": "Fortaleza conf. visitante",
        "is_inter_confederation": "Inter-confederacion",
        "home_streak": "Racha local",
        "away_streak": "Racha visitante",
        "home_unbeaten_streak": "Invicto local",
        "away_unbeaten_streak": "Invicto visitante",
        "home_days_rest": "Descanso local",
        "away_days_rest": "Descanso visitante",
        "rest_advantage": "Ventaja descanso",
        "home_clean_sheet_pct": "Porteria a cero (L)",
        "away_clean_sheet_pct": "Porteria a cero (V)",
        "is_knockout": "Fase eliminatoria",
        "home_major_tournament_exp": "Experiencia torneos (L)",
        "away_major_tournament_exp": "Experiencia torneos (V)",
        "home_home_record": "Rendimiento como local",
        "away_away_record": "Rendimiento como visitante",
        "home_fifa_rank": "Ranking FIFA local",
        "away_fifa_rank": "Ranking FIFA visitante",
        "fifa_rank_diff": "Dif. ranking FIFA",
    }

    display_names = [feature_names_map.get(f, f) for f in FEATURE_COLS]

    # Para multiclase, usar la clase "victoria local" (clase 2)
    if isinstance(shap_values, list) and len(shap_values) == 3:
        # Clase 0=derrota local, 1=empate, 2=victoria local
        sv_home_win = shap_values[2]
        sv_draw = shap_values[1]
        sv_away_win = shap_values[0]

        # SHAP medio absoluto por feature (global, sumando las 3 clases)
        mean_abs = np.mean([
            np.abs(shap_values[0]).mean(axis=0),
            np.abs(shap_values[1]).mean(axis=0),
            np.abs(shap_values[2]).mean(axis=0),
        ], axis=0)
    else:
        sv_home_win = shap_values
        mean_abs = np.abs(shap_values).mean(axis=0)

    # --- Grafica 1: Beeswarm plot (victoria local) ---
    print("  Generando beeswarm plot...")
    X_display = X_val.copy()
    X_display.columns = display_names

    fig, ax = plt.subplots(figsize=(10, 12), dpi=200)
    shap.summary_plot(
        sv_home_win, X_display,
        plot_type="dot",
        max_display=25,
        show=False,
        plot_size=None,
    )
    plt.title("Importancia de variables (SHAP) - Victoria local", fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "shap_beeswarm.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("    -> shap_beeswarm.png")

    # --- Grafica 2: Bar plot global (importancia media, 3 clases) ---
    print("  Generando bar plot de importancia global...")
    sorted_idx = np.argsort(mean_abs)[::-1][:20]

    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    y_pos = range(len(sorted_idx))
    ax.barh(y_pos, mean_abs[sorted_idx][::-1], color="#2563EB", alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([display_names[i] for i in sorted_idx][::-1], fontsize=9)
    ax.set_xlabel("Importancia media |SHAP|", fontsize=11)
    ax.set_title("Top 20 variables por importancia global (SHAP)", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "shap_global_importance.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("    -> shap_global_importance.png")

    # --- Grafica 3: Dependence plots de las 4 variables top ---
    print("  Generando dependence plots...")
    top4_idx = sorted_idx[:4]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=200)
    for ax_idx, feat_idx in enumerate(top4_idx):
        ax = axes[ax_idx // 2][ax_idx % 2]
        shap.dependence_plot(
            feat_idx, sv_home_win, X_val,
            feature_names=display_names,
            ax=ax,
            show=False,
        )
    plt.suptitle("Dependencia SHAP de las 4 variables principales", fontsize=12, y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "shap_dependence_top4.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("    -> shap_dependence_top4.png")

    # 5. Guardar datos SHAP para referencia
    print("[5/5] Guardando resumen de importancia...")
    importance_df = pd.DataFrame({
        "feature": FEATURE_COLS,
        "display_name": display_names,
        "mean_abs_shap": mean_abs,
    }).sort_values("mean_abs_shap", ascending=False)

    importance_df.to_csv(OUTPUTS_DIR / "shap_importance.csv", index=False)
    print("    -> shap_importance.csv")

    print("\n" + "=" * 60)
    print("Top 10 variables por importancia SHAP:")
    print("=" * 60)
    for i, row in importance_df.head(10).iterrows():
        print(f"  {row['display_name']:35s} {row['mean_abs_shap']:.4f}")

    print("\nAnalisis SHAP completado.")


if __name__ == "__main__":
    main()
