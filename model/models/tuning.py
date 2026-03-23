"""
Hyperparameter tuning con Optuna.
"""

import optuna
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
import xgboost as xgb
import lightgbm as lgb

from model.config import RANDOM_SEED, OPTUNA_N_TRIALS, CV_N_SPLITS

# Silenciar logs de Optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)


def _lgbm_objective(trial, X, y, sample_weight=None):
    """Objetivo de Optuna para LightGBM."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 60),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 15, 63),
        "class_weight": "balanced",
        "random_state": RANDOM_SEED,
        "verbosity": -1,
    }

    tscv = TimeSeriesSplit(n_splits=CV_N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_v = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_v = y.iloc[train_idx], y.iloc[val_idx]

        model = lgb.LGBMClassifier(**params)
        sw = sample_weight[train_idx] if sample_weight is not None else None
        model.fit(X_tr, y_tr, sample_weight=sw)

        y_proba = model.predict_proba(X_v)
        scores.append(log_loss(y_v, y_proba))

    return np.mean(scores)


def _xgb_objective(trial, X, y, sample_weight=None):
    """Objetivo de Optuna para XGBoost."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        "gamma": trial.suggest_float("gamma", 1e-3, 5.0, log=True),
        "random_state": RANDOM_SEED,
        "verbosity": 0,
        "eval_metric": "mlogloss",
    }

    tscv = TimeSeriesSplit(n_splits=CV_N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_v = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_v = y.iloc[train_idx], y.iloc[val_idx]

        model = xgb.XGBClassifier(**params)
        sw = sample_weight[train_idx] if sample_weight is not None else None
        model.fit(X_tr, y_tr, sample_weight=sw)

        y_proba = model.predict_proba(X_v)
        scores.append(log_loss(y_v, y_proba))

    return np.mean(scores)


def tune_lightgbm(X_train, y_train, sample_weight=None, n_trials=OPTUNA_N_TRIALS):
    """
    Optimiza hiperparametros de LightGBM con Optuna.

    Returns:
        (best_params, best_model)
    """
    print(f"Optimizando LightGBM con {n_trials} trials...")

    study = optuna.create_study(direction="minimize", study_name="lgbm_tuning")
    study.optimize(
        lambda trial: _lgbm_objective(trial, X_train, y_train, sample_weight),
        n_trials=n_trials,
        show_progress_bar=True,
    )

    best_params = study.best_params
    best_params["class_weight"] = "balanced"
    best_params["random_state"] = RANDOM_SEED
    best_params["verbosity"] = -1

    print(f"  Mejor log_loss CV: {study.best_value:.4f}")
    print(f"  Mejores parametros: {best_params}")

    best_model = lgb.LGBMClassifier(**best_params)
    if sample_weight is not None:
        best_model.fit(X_train, y_train, sample_weight=sample_weight)
    else:
        best_model.fit(X_train, y_train)

    return best_params, best_model


def tune_xgboost(X_train, y_train, sample_weight=None, n_trials=OPTUNA_N_TRIALS):
    """
    Optimiza hiperparametros de XGBoost con Optuna.

    Returns:
        (best_params, best_model)
    """
    print(f"Optimizando XGBoost con {n_trials} trials...")

    study = optuna.create_study(direction="minimize", study_name="xgb_tuning")
    study.optimize(
        lambda trial: _xgb_objective(trial, X_train, y_train, sample_weight),
        n_trials=n_trials,
        show_progress_bar=True,
    )

    best_params = study.best_params
    best_params["random_state"] = RANDOM_SEED
    best_params["verbosity"] = 0
    best_params["eval_metric"] = "mlogloss"

    print(f"  Mejor log_loss CV: {study.best_value:.4f}")
    print(f"  Mejores parametros: {best_params}")

    best_model = xgb.XGBClassifier(**best_params)
    if sample_weight is not None:
        best_model.fit(X_train, y_train, sample_weight=sample_weight)
    else:
        best_model.fit(X_train, y_train)

    return best_params, best_model
