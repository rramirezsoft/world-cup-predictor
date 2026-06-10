"""
Optimizacion de hiperparametros con Optuna + Monte Carlo simulation.
Ejecutar desde la raiz del proyecto:
    venv\\Scripts\\python scripts\\optimize_model.py
"""

import sys
import time
import json
import joblib
import numpy as np
import pandas as pd
import optuna
from pathlib import Path
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import lightgbm as lgb

# Asegurar que model.* sea importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model.data.loader import load_results
from model.features.engineering import build_features, prepare_splits, compute_sample_weights
from model.models.training import evaluate_on_test, save_model, TARGET_NAMES
from model.config import (
    MODELS_DIR, RANDOM_SEED, FEATURE_COLS, TARGET,
    MONTE_CARLO_SIMULATIONS,
)
from model.simulation.simulator import WorldCupSimulator

# Silenciar logs de Optuna (solo mostrar progreso)
optuna.logging.set_verbosity(optuna.logging.WARNING)


def numpy_to_python(obj):
    """Convierte tipos numpy a tipos nativos de Python para JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: numpy_to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [numpy_to_python(v) for v in obj]
    return obj


# =============================================================================
# 1. CARGAR DATOS Y CONSTRUIR FEATURES
# =============================================================================
print("=" * 70)
print("WORLD CUP 2026 PREDICTOR — Optimizacion con Optuna")
print("=" * 70)

t_total = time.time()

print("\n[1/8] Cargando datos...")
df = load_results()
print(f"      {len(df):,} partidos cargados")

print("\n[2/8] Construyendo features...")
t0 = time.time()
df = build_features(df)
print(f"      {len(FEATURE_COLS)} features construidas ({time.time()-t0:.0f}s)")

# =============================================================================
# 2. PREPARAR SPLITS
# =============================================================================
print("\n[3/8] Preparando splits temporales...")
splits = prepare_splits(df)
sample_weights = compute_sample_weights(splits["df_train"], splits["y_train"])

X_train = splits["X_train"]
y_train = splits["y_train"]
X_val = splits["X_val"]
y_val = splits["y_val"]
X_test = splits["X_test"]
y_test = splits["y_test"]
X_wc2022 = splits["X_wc2022"]
y_wc2022 = splits["y_wc2022"]

print(f"      Train: {len(X_train):,} | Val: {len(X_val):,} | "
      f"Test: {len(X_test):,} | WC2022: {len(X_wc2022):,}")


# =============================================================================
# 3. OPTUNA — XGBoost (50 trials)
# =============================================================================
print("\n[4/8] Optimizando XGBoost con Optuna (50 trials)...")
print("      Objetivo: minimizar validation log_loss")
t0 = time.time()

N_TRIALS = 50


def xgb_objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 20),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.001, 10.0, log=True),
        "gamma": trial.suggest_float("gamma", 0.0, 5.0),
        "random_state": RANDOM_SEED,
        "verbosity": 0,
        "eval_metric": "mlogloss",
    }
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train, sample_weight=sample_weights)
    y_proba = model.predict_proba(X_val)
    return log_loss(y_val, y_proba)


xgb_study = optuna.create_study(direction="minimize", study_name="xgb_optimization")
xgb_study.optimize(xgb_objective, n_trials=N_TRIALS, show_progress_bar=True)

xgb_best_params = xgb_study.best_params
xgb_best_params["random_state"] = RANDOM_SEED
xgb_best_params["verbosity"] = 0
xgb_best_params["eval_metric"] = "mlogloss"

print(f"      Mejor log_loss (val): {xgb_study.best_value:.4f}")
print(f"      Tiempo: {time.time()-t0:.0f}s")
print(f"      Mejores params: {xgb_best_params}")


# =============================================================================
# 4. OPTUNA — LightGBM (50 trials)
# =============================================================================
print("\n[5/8] Optimizando LightGBM con Optuna (50 trials)...")
print("      Objetivo: minimizar validation log_loss")
t0 = time.time()


def lgbm_objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 60),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.001, 10.0, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 15, 63),
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "verbosity": -1,
    }
    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train, sample_weight=sample_weights)
    y_proba = model.predict_proba(X_val)
    return log_loss(y_val, y_proba)


lgbm_study = optuna.create_study(direction="minimize", study_name="lgbm_optimization")
lgbm_study.optimize(lgbm_objective, n_trials=N_TRIALS, show_progress_bar=True)

lgbm_best_params = lgbm_study.best_params
lgbm_best_params["class_weight"] = "balanced"
lgbm_best_params["random_state"] = RANDOM_SEED
lgbm_best_params["verbosity"] = -1

print(f"      Mejor log_loss (val): {lgbm_study.best_value:.4f}")
print(f"      Tiempo: {time.time()-t0:.0f}s")
print(f"      Mejores params: {lgbm_best_params}")


# =============================================================================
# 5. ENTRENAR MEJORES MODELOS Y STACKING ENSEMBLE
# =============================================================================
print("\n[6/8] Entrenando mejores modelos y stacking ensemble...")

# Entrenar XGBoost con mejores hiperparametros
best_xgb = xgb.XGBClassifier(**xgb_best_params)
best_xgb.fit(X_train, y_train, sample_weight=sample_weights)
xgb_val_pred = best_xgb.predict(X_val)
xgb_val_proba = best_xgb.predict_proba(X_val)
xgb_val_acc = accuracy_score(y_val, xgb_val_pred)
xgb_val_ll = log_loss(y_val, xgb_val_proba)
print(f"      XGBoost  — Val Acc: {xgb_val_acc:.4f} | Val LogLoss: {xgb_val_ll:.4f}")

# Entrenar LightGBM con mejores hiperparametros
best_lgbm = lgb.LGBMClassifier(**lgbm_best_params)
best_lgbm.fit(X_train, y_train, sample_weight=sample_weights)
lgbm_val_pred = best_lgbm.predict(X_val)
lgbm_val_proba = best_lgbm.predict_proba(X_val)
lgbm_val_acc = accuracy_score(y_val, lgbm_val_pred)
lgbm_val_ll = log_loss(y_val, lgbm_val_proba)
print(f"      LightGBM — Val Acc: {lgbm_val_acc:.4f} | Val LogLoss: {lgbm_val_ll:.4f}")

# Stacking ensemble con los mejores modelos optimizados
print("      Entrenando Stacking Ensemble...")
stacking = StackingClassifier(
    estimators=[
        ("xgb", xgb.XGBClassifier(**xgb_best_params)),
        ("lgbm", lgb.LGBMClassifier(**lgbm_best_params)),
        ("rf", RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_split=30,
            min_samples_leaf=15, random_state=RANDOM_SEED,
            n_jobs=-1, class_weight="balanced",
        )),
    ],
    final_estimator=LogisticRegression(
        max_iter=1000, random_state=RANDOM_SEED, C=1.0,
    ),
    cv=5,
    stack_method="predict_proba",
    n_jobs=-1,
)
stacking.fit(X_train, y_train, sample_weight=sample_weights)
stack_val_pred = stacking.predict(X_val)
stack_val_proba = stacking.predict_proba(X_val)
stack_val_acc = accuracy_score(y_val, stack_val_pred)
stack_val_ll = log_loss(y_val, stack_val_proba)
print(f"      Stacking — Val Acc: {stack_val_acc:.4f} | Val LogLoss: {stack_val_ll:.4f}")

# Seleccionar el mejor modelo por log_loss (mejor para clasificacion 3 clases)
candidates = [
    ("XGBoost (Optuna)", best_xgb, xgb_val_acc, xgb_val_ll),
    ("LightGBM (Optuna)", best_lgbm, lgbm_val_acc, lgbm_val_ll),
    ("Stacking Ensemble", stacking, stack_val_acc, stack_val_ll),
]

candidates.sort(key=lambda x: x[3])  # sort by log_loss ascending (lower is better)
best_name, best_model, best_val_acc, best_val_ll = candidates[0]

print(f"\n      >>> Mejor modelo (sin calibrar): {best_name}")
print(f"          Val Accuracy: {best_val_acc:.4f} | Val LogLoss: {best_val_ll:.4f}")

# Calibrar probabilidades (suaviza predicciones extremas)
print("\n      Calibrando probabilidades (isotonic)...")
from sklearn.calibration import CalibratedClassifierCV
calibrated = CalibratedClassifierCV(best_model, method="isotonic", cv=5)
calibrated.fit(X_train, y_train, sample_weight=sample_weights)

cal_val_pred = calibrated.predict(X_val)
cal_val_proba = calibrated.predict_proba(X_val)
cal_val_acc = accuracy_score(y_val, cal_val_pred)
cal_val_ll = log_loss(y_val, cal_val_proba)
print(f"      Calibrado — Val Acc: {cal_val_acc:.4f} | Val LogLoss: {cal_val_ll:.4f}")

# Usar el calibrado si mejora log_loss, si no usar el original
if cal_val_ll < best_val_ll:
    best_model = calibrated
    best_name = f"{best_name} + Calibrated"
    best_val_acc = cal_val_acc
    best_val_ll = cal_val_ll
    print(f"      >>> Calibracion mejora el modelo. Usando version calibrada.")
else:
    print(f"      >>> Calibracion no mejora. Manteniendo modelo original.")

print(f"\n      >>> Mejor modelo final: {best_name}")
print(f"          Val Accuracy: {best_val_acc:.4f} | Val LogLoss: {best_val_ll:.4f}")


# =============================================================================
# 6. EVALUACION EN TEST Y WC2022
# =============================================================================
print("\n[7/8] Evaluacion del mejor modelo...")

# Evaluacion en Test (2023+)
print("\n--- Evaluacion en Test (2023+) ---")
test_results = evaluate_on_test(best_model, X_test, y_test, dataset_name="Test (2023+)")

# Evaluacion en World Cup 2022
print("\n--- Evaluacion en World Cup 2022 ---")
wc2022_results = evaluate_on_test(best_model, X_wc2022, y_wc2022, dataset_name="World Cup 2022")


# =============================================================================
# 7. GUARDAR MODELO, TRACKERS Y RESULTADOS
# =============================================================================
print("\n[8/8] Guardando resultados...")

MODELS_DIR.mkdir(exist_ok=True)

# Guardar mejor modelo
save_model(best_model, "best_model.joblib")

# Guardar trackers
trackers = {
    "elo_system": df.attrs["elo_system"],
    "form_tracker": df.attrs["form_tracker"],
    "h2h_tracker": df.attrs["h2h_tracker"],
    "major_exp": df.attrs["major_exp"],
    "conf_wins": df.attrs["conf_wins"],
    "scaler": splits["scaler"],
}
trackers_path = MODELS_DIR / "trackers.joblib"
joblib.dump(trackers, trackers_path)
print(f"      Trackers guardados en {trackers_path}")

# Guardar resumen de resultados
optimization_results = {
    "best_model_name": best_name,
    "n_trials_per_model": N_TRIALS,
    "xgboost": {
        "best_params": numpy_to_python(xgb_best_params),
        "best_val_logloss": float(xgb_study.best_value),
        "val_accuracy": float(xgb_val_acc),
        "val_logloss": float(xgb_val_ll),
    },
    "lightgbm": {
        "best_params": numpy_to_python(lgbm_best_params),
        "best_val_logloss": float(lgbm_study.best_value),
        "val_accuracy": float(lgbm_val_acc),
        "val_logloss": float(lgbm_val_ll),
    },
    "stacking_ensemble": {
        "val_accuracy": float(stack_val_acc),
        "val_logloss": float(stack_val_ll),
    },
    "test_evaluation": {
        "accuracy": float(test_results["accuracy"]),
        "log_loss": float(test_results["log_loss"]),
    },
    "wc2022_evaluation": {
        "accuracy": float(wc2022_results["accuracy"]),
        "log_loss": float(wc2022_results["log_loss"]),
    },
    "model_comparison_val": [
        {"name": name, "val_accuracy": float(acc), "val_logloss": float(ll)}
        for name, _, acc, ll in candidates
    ],
}

results_path = MODELS_DIR / "optimization_results.json"
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(optimization_results, f, indent=2, ensure_ascii=False)
print(f"      Resultados guardados en {results_path}")


# =============================================================================
# 8. SIMULACION MONTE CARLO (10,000 iteraciones)
# =============================================================================
print("\n" + "=" * 70)
print("SIMULACION MONTE CARLO — 10,000 iteraciones")
print("=" * 70)

t0 = time.time()

# XGBoost no necesita scaler (solo modelos lineales)
simulator = WorldCupSimulator(
    model=best_model,
    elo_system=df.attrs["elo_system"],
    form_tracker=df.attrs["form_tracker"],
    h2h_tracker=df.attrs["h2h_tracker"],
    major_exp=df.attrs["major_exp"],
    conf_wins=df.attrs["conf_wins"],
    scaler=None,
)

mc_df = simulator.monte_carlo(n_simulations=10_000, seed=RANDOM_SEED)
print(f"      Tiempo simulacion: {time.time()-t0:.0f}s")

# Convertir a JSON-serializable dict con tipos nativos de Python
mc_results = {
    "n_simulations": 10_000,
    "seed": RANDOM_SEED,
    "teams": []
}
for _, row in mc_df.iterrows():
    mc_results["teams"].append({
        "team": str(row["team"]),
        "champion_pct": float(row["champion_pct"]),
        "final_pct": float(row["final_pct"]),
        "sf_pct": float(row["sf_pct"]),
        "qf_pct": float(row["qf_pct"]),
        "r16_pct": float(row["r16_pct"]),
        "r32_pct": float(row["r32_pct"]),
        "elo": float(row["elo"]),
    })

mc_path = MODELS_DIR / "monte_carlo_results.json"
with open(mc_path, "w", encoding="utf-8") as f:
    json.dump(mc_results, f, indent=2, ensure_ascii=False)
print(f"      Resultados Monte Carlo guardados en {mc_path}")


# =============================================================================
# RESUMEN FINAL
# =============================================================================
elapsed = time.time() - t_total
print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
print(f"  Mejor modelo:        {best_name}")
print(f"  Val Accuracy:        {best_val_acc:.4f} ({best_val_acc*100:.1f}%)")
print(f"  Val LogLoss:         {best_val_ll:.4f}")
print(f"  Test Accuracy:       {test_results['accuracy']:.4f} ({test_results['accuracy']*100:.1f}%)")
print(f"  Test LogLoss:        {test_results['log_loss']:.4f}")
print(f"  WC2022 Accuracy:     {wc2022_results['accuracy']:.4f} ({wc2022_results['accuracy']*100:.1f}%)")
print(f"  WC2022 LogLoss:      {wc2022_results['log_loss']:.4f}")
print(f"  Monte Carlo sims:    10,000")
print(f"  Tiempo total:        {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"\nArchivos guardados en {MODELS_DIR}/:")
print(f"  - best_model.joblib")
print(f"  - trackers.joblib")
print(f"  - optimization_results.json")
print(f"  - monte_carlo_results.json")
print("\nListo!")
