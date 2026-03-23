"""
Backend FastAPI del World Cup 2026 Predictor.

Ejecutar desde la raiz del proyecto:
    uvicorn backend.main:app --reload --port 8000
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar root del proyecto en path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.api.routes import router
from backend.services.predictor import predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa el modelo al arrancar el servidor."""
    print("=" * 50)
    print("World Cup 2026 Predictor — Backend")
    print("=" * 50)
    predictor.initialize()
    yield
    print("Servidor cerrado.")


app = FastAPI(
    title="World Cup 2026 Predictor API",
    description="API para predecir y simular el Mundial de Futbol 2026",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permitir frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
