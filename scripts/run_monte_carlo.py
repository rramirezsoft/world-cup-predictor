"""
Genera monte_carlo_results.json usando el modelo ya entrenado.
Ejecutar: venv\\Scripts\\python scripts/run_monte_carlo.py
"""

import sys
import json
import time
import joblib
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model.config import MODELS_DIR, RANDOM_SEED
from model.simulation.simulator import WorldCupSimulator

N_SIMULATIONS = 10_000

print(f"Cargando modelo y trackers...")
model = joblib.load(MODELS_DIR / "best_model.joblib")
trackers = joblib.load(MODELS_DIR / "trackers.joblib")

simulator = WorldCupSimulator(
    model=model,
    elo_system=trackers["elo_system"],
    form_tracker=trackers["form_tracker"],
    h2h_tracker=trackers["h2h_tracker"],
    major_exp=trackers["major_exp"],
    conf_wins=trackers["conf_wins"],
    scaler=None,
)

print(f"Ejecutando {N_SIMULATIONS:,} simulaciones Monte Carlo...")
t0 = time.time()
mc_df = simulator.monte_carlo(n_simulations=N_SIMULATIONS, seed=RANDOM_SEED)
elapsed = time.time() - t0
print(f"Completado en {elapsed:.0f}s")

results = {
    "n_simulations": N_SIMULATIONS,
    "seed": RANDOM_SEED,
    "teams": [],
}
for _, row in mc_df.iterrows():
    results["teams"].append({
        "team": str(row["team"]),
        "champion_pct": float(row["champion_pct"]),
        "final_pct": float(row["final_pct"]),
        "sf_pct": float(row["sf_pct"]),
        "qf_pct": float(row["qf_pct"]),
        "r16_pct": float(row["r16_pct"]),
        "r32_pct": float(row["r32_pct"]),
        "elo": float(row["elo"]),
    })

output_path = MODELS_DIR / "monte_carlo_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nGuardado en {output_path}")
print(f"\nTop 10:")
for i, t in enumerate(results["teams"][:10], 1):
    print(f"  {i:2d}. {t['team']:20s} {t['champion_pct']:5.1f}%  (ELO {t['elo']:.0f})")
