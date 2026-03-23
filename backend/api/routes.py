"""
Endpoints de la API del World Cup 2026 Predictor.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from backend.services.predictor import predictor

router = APIRouter(prefix="/api")


class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    is_knockout: bool = False


@router.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": predictor.ready}


@router.get("/teams")
def get_teams():
    """48 equipos del Mundial 2026 con grupo, ELO y confederacion."""
    if not predictor.ready:
        raise HTTPException(503, "Modelo no inicializado")
    return predictor.get_teams()


@router.get("/model-info")
def get_model_info():
    """Info del modelo: nombre, metricas, comparacion."""
    if not predictor.ready:
        raise HTTPException(503, "Modelo no inicializado")
    return predictor.get_model_info()


@router.post("/predict")
def predict_match(req: MatchRequest):
    """Predice probabilidades de un partido entre dos selecciones."""
    if not predictor.ready:
        raise HTTPException(503, "Modelo no inicializado")
    try:
        return predictor.predict_match(req.home_team, req.away_team, req.is_knockout)
    except Exception as e:
        raise HTTPException(400, f"Error en prediccion: {str(e)}")


@router.get("/simulation")
def simulate_tournament(seed: Optional[int] = Query(None)):
    """Simula un Mundial 2026 completo."""
    if not predictor.ready:
        raise HTTPException(503, "Modelo no inicializado")
    try:
        return predictor.simulate_tournament(seed=seed)
    except Exception as e:
        raise HTTPException(500, f"Error en simulacion: {str(e)}")


@router.get("/monte-carlo")
def get_stats():
    """Probabilidades pre-computadas de cada seleccion (10,000 simulaciones)."""
    if not predictor.ready:
        raise HTTPException(503, "Modelo no inicializado")
    results = predictor.get_monte_carlo()
    if not results:
        raise HTTPException(
            404,
            "No hay datos de estadisticas. Ejecuta: venv\\Scripts\\python scripts/run_monte_carlo.py",
        )
    return results
