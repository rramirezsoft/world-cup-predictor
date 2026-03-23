"""
Entrenamiento, evaluacion y comparacion de modelos.
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, log_loss, classification_report,
    confusion_matrix, brier_score_loss,
)
import xgboost as xgb
import lightgbm as lgb

from model.config import RANDOM_SEED, MODELS_DIR, FEATURE_COLS


TARGET_NAMES = ["Victoria Visitante", "Empate", "Victoria Local"]


def get_default_models():
    """Devuelve diccionario con modelos por defecto para comparacion."""
    return {
        "Baseline (siempre Local)": DummyClassifier(
            strategy="most_frequent", random_state=RANDOM_SEED
        ),
        "Regresion Logistica": LogisticRegression(
            max_iter=1000, random_state=RANDOM_SEED, C=1.0,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_split=30,
            min_samples_leaf=15, random_state=RANDOM_SEED,
            n_jobs=-1, class_weight="balanced",
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=RANDOM_SEED, verbosity=0, eval_metric="mlogloss",
        ),
        "LightGBM": lgb.LGBMClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_samples=30,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=RANDOM_SEED, verbosity=-1,
        ),
    }


def train_and_evaluate(name, model, X_train, y_train, X_val, y_val,
                       sample_weight=None):
    """
    Entrena un modelo y devuelve metricas de evaluacion.

    Returns:
        dict con: model, train_acc, val_acc, val_logloss, y_val_pred, y_val_proba
    """
    if sample_weight is not None:
        model.fit(X_train, y_train, sample_weight=sample_weight)
    else:
        model.fit(X_train, y_train)

    y_pred_train = model.predict(X_train)
    y_pred_val = model.predict(X_val)
    y_proba_val = model.predict_proba(X_val)

    train_acc = accuracy_score(y_train, y_pred_train)
    val_acc = accuracy_score(y_val, y_pred_val)
    val_ll = log_loss(y_val, y_proba_val)

    return {
        "name": name,
        "model": model,
        "train_acc": train_acc,
        "val_acc": val_acc,
        "val_logloss": val_ll,
        "y_val_pred": y_pred_val,
        "y_val_proba": y_proba_val,
    }


def compare_models(X_train, y_train, X_val, y_val, X_train_sc, X_val_sc,
                   sample_weight=None, models=None):
    """
    Entrena y compara todos los modelos.

    Returns:
        list de dicts con resultados, ordenados por val_acc descendente.
    """
    if models is None:
        models = get_default_models()

    results = []
    for name, model in models.items():
        # Usar features escaladas solo para regresion logistica
        use_scaled = "Logistica" in name or "Logistic" in name
        Xtr = X_train_sc if use_scaled else X_train
        Xv = X_val_sc if use_scaled else X_val

        # DummyClassifier no acepta sample_weight
        sw = None if "Baseline" in name or "Dummy" in name else sample_weight

        result = train_and_evaluate(name, model, Xtr, y_train, Xv, y_val, sw)
        results.append(result)
        print(f"  {name:35s} | Train: {result['train_acc']:.4f} | "
              f"Val: {result['val_acc']:.4f} | LogLoss: {result['val_logloss']:.4f}")

    results.sort(key=lambda x: x["val_acc"], reverse=True)
    return results


def build_stacking_ensemble(X_train, y_train, X_val, y_val, sample_weight=None):
    """
    Construye un ensemble por stacking con los mejores modelos.

    Base models: LightGBM, XGBoost, RandomForest
    Meta-learner: LogisticRegression

    Returns:
        dict con resultados del ensemble.
    """
    estimators = [
        ("lgbm", lgb.LGBMClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_samples=30,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=RANDOM_SEED, verbosity=-1,
        )),
        ("xgb", xgb.XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=RANDOM_SEED, verbosity=0, eval_metric="mlogloss",
        )),
        ("rf", RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_split=30,
            min_samples_leaf=15, random_state=RANDOM_SEED,
            n_jobs=-1, class_weight="balanced",
        )),
    ]

    stacking = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(
            max_iter=1000, random_state=RANDOM_SEED, C=1.0,
        ),
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
    )

    result = train_and_evaluate(
        "Stacking Ensemble", stacking, X_train, y_train, X_val, y_val,
        sample_weight=sample_weight,
    )
    print(f"\n  {'Stacking Ensemble':35s} | Train: {result['train_acc']:.4f} | "
          f"Val: {result['val_acc']:.4f} | LogLoss: {result['val_logloss']:.4f}")

    return result


def calibrate_model(model, X_train, y_train, method="isotonic", cv=5):
    """
    Calibra las probabilidades de un modelo.

    Returns:
        CalibratedClassifierCV ajustado.
    """
    calibrated = CalibratedClassifierCV(
        model, method=method, cv=cv, n_jobs=-1,
    )
    calibrated.fit(X_train, y_train)
    return calibrated


def evaluate_on_test(model, X_test, y_test, dataset_name="Test"):
    """Evalua un modelo en un conjunto de test."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    ll = log_loss(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n=== Evaluacion en {dataset_name} ===")
    print(f"Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print(f"Log Loss: {ll:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=TARGET_NAMES, zero_division=0))

    return {
        "accuracy": acc,
        "log_loss": ll,
        "confusion_matrix": cm,
        "y_pred": y_pred,
        "y_proba": y_proba,
    }


def save_model(model, filename="best_model.joblib"):
    """Guarda modelo en disco."""
    MODELS_DIR.mkdir(exist_ok=True)
    path = MODELS_DIR / filename
    joblib.dump(model, path)
    print(f"Modelo guardado en {path}")
    return path


def load_model(filename="best_model.joblib"):
    """Carga modelo desde disco."""
    path = MODELS_DIR / filename
    return joblib.load(path)
