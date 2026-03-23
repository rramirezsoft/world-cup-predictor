"""
Servicio principal del predictor.
Carga el modelo y resultados pre-computados. Sirve predicciones y simulaciones.
"""

import json
import joblib
import numpy as np
from model.config import (
    WORLD_CUP_2026_GROUPS, TEAM_TO_CONFEDERATION, FEATURE_COLS,
    MODELS_DIR,
)
from model.simulation.simulator import WorldCupSimulator


class PredictorService:
    """
    Servicio singleton que gestiona el modelo y las simulaciones.
    Carga modelo + trackers + resultados pre-computados de Monte Carlo.
    """

    def __init__(self):
        self.model = None
        self.simulator = None
        self.elo_system = None
        self.form_tracker = None
        self.h2h_tracker = None
        self.major_exp = None
        self.conf_wins = None
        self.monte_carlo_results = None
        self.optimization_results = None
        self._ready = False

    @property
    def ready(self):
        return self._ready

    def initialize(self):
        """Carga modelo, trackers y resultados pre-computados."""
        model_path = MODELS_DIR / "best_model.joblib"
        trackers_path = MODELS_DIR / "trackers.joblib"
        mc_path = MODELS_DIR / "monte_carlo_results.json"
        opt_path = MODELS_DIR / "optimization_results.json"

        if not model_path.exists() or not trackers_path.exists():
            raise RuntimeError(
                "No hay modelo guardado. Ejecuta primero: "
                "venv\\Scripts\\python scripts/optimize_model.py"
            )

        print("[Predictor] Cargando modelo y trackers...")
        self.model = joblib.load(model_path)
        trackers = joblib.load(trackers_path)
        self.elo_system = trackers["elo_system"]
        self.form_tracker = trackers["form_tracker"]
        self.h2h_tracker = trackers["h2h_tracker"]
        self.major_exp = trackers["major_exp"]
        self.conf_wins = trackers["conf_wins"]

        # Cargar Monte Carlo pre-computado
        if mc_path.exists():
            with open(mc_path, "r", encoding="utf-8") as f:
                self.monte_carlo_results = json.load(f)
            print(f"[Predictor] Monte Carlo cargado ({self.monte_carlo_results['n_simulations']:,} sims)")
        else:
            print("[Predictor] AVISO: No hay monte_carlo_results.json")

        # Cargar resultados de optimizacion
        if opt_path.exists():
            with open(opt_path, "r", encoding="utf-8") as f:
                self.optimization_results = json.load(f)
            print(f"[Predictor] Mejor modelo: {self.optimization_results['best_model_name']}")

        # Crear simulador (sin scaler para tree-based models)
        self.simulator = WorldCupSimulator(
            model=self.model,
            elo_system=self.elo_system,
            form_tracker=self.form_tracker,
            h2h_tracker=self.h2h_tracker,
            major_exp=self.major_exp,
            conf_wins=self.conf_wins,
            scaler=None,
        )
        self._ready = True
        print("[Predictor] Listo.")

    def get_teams(self):
        """Devuelve los 48 equipos del mundial con su info."""
        teams = []
        for group, group_teams in sorted(WORLD_CUP_2026_GROUPS.items()):
            for team in group_teams:
                teams.append({
                    "name": team,
                    "group": group,
                    "elo": round(float(self.elo_system.get(team)), 1),
                    "confederation": TEAM_TO_CONFEDERATION.get(team, "UNKNOWN"),
                })
        return teams

    def predict_match(self, home_team, away_team, is_knockout=False):
        """Predice un partido individual."""
        probs = self.simulator.predict_match(
            home_team, away_team, is_knockout=int(is_knockout)
        )
        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_win_prob": round(float(probs["home_win_prob"]) * 100, 1),
            "draw_prob": round(float(probs["draw_prob"]) * 100, 1),
            "away_win_prob": round(float(probs["away_win_prob"]) * 100, 1),
            "home_elo": round(float(self.elo_system.get(home_team)), 1),
            "away_elo": round(float(self.elo_system.get(away_team)), 1),
        }

    def simulate_tournament(self, seed=None):
        """Simula un mundial completo."""
        rng = np.random.default_rng(seed)
        result = self.simulator.simulate_tournament(rng=rng)

        groups = {}
        for group_name, standings_df in result["group_standings"].items():
            groups[group_name] = {
                "teams": WORLD_CUP_2026_GROUPS[group_name],
                "standings": standings_df.to_dict("records"),
                "matches": result["group_matches"][group_name],
            }

        knockout = {}
        for round_name, matches in result["results"].items():
            knockout[round_name] = matches

        return {
            "groups": groups,
            "knockout": knockout,
            "champion": result["champion"],
            "runner_up": result["runner_up"],
        }

    def get_monte_carlo(self):
        """Devuelve los resultados pre-computados de Monte Carlo."""
        if not self.monte_carlo_results:
            return None
        return self.monte_carlo_results

    def get_model_info(self):
        """Devuelve info sobre el modelo y su rendimiento."""
        info = {
            "model_name": self.optimization_results.get("best_model_name", "Unknown") if self.optimization_results else "XGBoost",
            "n_features": len(FEATURE_COLS),
            "monte_carlo_simulations": self.monte_carlo_results["n_simulations"] if self.monte_carlo_results else 0,
        }
        if self.optimization_results:
            info["validation"] = {
                "accuracy": self.optimization_results.get("test_evaluation", {}).get("accuracy"),
                "log_loss": self.optimization_results.get("test_evaluation", {}).get("log_loss"),
            }
            info["wc2022"] = self.optimization_results.get("wc2022_evaluation")
            info["model_comparison"] = self.optimization_results.get("model_comparison_val")
        return info


# Singleton global
predictor = PredictorService()
