# World Cup 2026 Predictor

Sistema de predicción del Mundial de Fútbol FIFA 2026 basado en Machine Learning. Incluye un modelo predictivo entrenado con más de 49,000 partidos internacionales históricos, simulación Monte Carlo del torneo completo y una aplicación web interactiva para visualizar los resultados.

**Trabajo Fin de Grado** — Grado en Ingeniería del Software, Universidad Europea de Madrid.

## Qué hace

1. **Modelo predictivo**: Clasifica el resultado de un partido (victoria local / empate / victoria visitante) a partir de 47 features extraídas de datos históricos.
2. **Simulación Monte Carlo**: Simula 10,000 veces el Mundial completo (104 partidos) para calcular la probabilidad de cada selección de ganar el torneo, llegar a la final, semifinales, etc.
3. **Aplicación web**: Frontend interactivo que muestra simulaciones del torneo paso a paso (fase de grupos → eliminatorias → campeón) y una pantalla de estadísticas con las probabilidades de cada equipo comparadas con casas de apuestas.

## Estructura del proyecto

```
world-cup-predictor/
├── model/                      # Paquete Python del modelo ML
│   ├── config.py               # Configuración central (features, grupos, constantes)
│   ├── data/loader.py          # Carga de datasets CSV
│   ├── features/               # Ingeniería de features
│   │   ├── elo.py              # Sistema ELO con K diferenciados por competición
│   │   ├── form.py             # Forma reciente (últimos N partidos)
│   │   ├── h2h.py              # Historial de enfrentamientos directos
│   │   └── engineering.py      # Pipeline completo + train/val/test splits
│   ├── models/                 # Entrenamiento y optimización
│   │   ├── training.py         # Entrenamiento, evaluación, comparación de modelos
│   │   └── tuning.py           # Optimización de hiperparámetros con Optuna
│   ├── simulation/             # Simulación del torneo
│   │   ├── tournament.py       # Estructura del Mundial 2026 (48 equipos, 12 grupos)
│   │   └── simulator.py        # Simulador de partidos + Monte Carlo
│   └── visualization/plots.py  # Gráficas EDA para el documento del TFG
├── backend/                    # API REST (FastAPI)
│   ├── main.py                 # Aplicación FastAPI con lifespan
│   ├── api/routes.py           # Endpoints de la API
│   └── services/predictor.py   # Servicio que carga el modelo y sirve predicciones
├── frontend/                   # Aplicación web (Next.js + TypeScript)
│   └── app/
│       ├── page.tsx            # Página principal
│       └── components/         # GroupTable, KnockoutBracket, StatsView, Flag, Confetti
├── data/                       # Datasets CSV (49,071 partidos internacionales)
├── saved_models/               # Modelo entrenado + resultados Monte Carlo (generados)
├── scripts/                    # Scripts de ejecución
│   ├── optimize_model.py       # Optimización con Optuna + entrenamiento + Monte Carlo
│   └── run_monte_carlo.py      # Genera Monte Carlo con modelo ya entrenado
├── notebooks/main.ipynb        # Análisis exploratorio de datos
└── requirements.txt            # Dependencias Python
```

## Features del modelo (47 variables)

| Categoría | Variables | Descripción |
|-----------|-----------|-------------|
| ELO | 6 | Rating ELO propio con K diferenciados (K=60 Mundial, K=20 amistoso) |
| Forma reciente | 14 | Victorias, empates, derrotas, goles en últimos 5/10/20 partidos |
| Enfrentamientos directos | 6 | Historial H2H, dominancia, goles en enfrentamientos previos |
| Experiencia | 8 | Participaciones en Mundiales y torneos continentales |
| Contextuales | 13 | Campo neutral, confederación, tipo de competición, rachas |

## Instalación y ejecución

### Requisitos

- Python 3.11+
- Node.js 18+

### 1. Entorno Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. Entrenar modelo y generar predicciones

```bash
# Optimización completa (Optuna + entrenamiento + Monte Carlo) — ~15 min
python scripts/optimize_model.py

# O solo Monte Carlo si ya tienes el modelo entrenado — ~5 min
python scripts/run_monte_carlo.py
```

Esto genera en `saved_models/`:
- `best_model.joblib` — Modelo XGBoost optimizado
- `trackers.joblib` — Estado del sistema ELO, forma y H2H
- `optimization_results.json` — Métricas y comparación de modelos
- `monte_carlo_results.json` — Probabilidades de las 48 selecciones

### 3. Backend

```bash
python -m uvicorn backend.main:app --reload --port 8001
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Abrir http://localhost:3000

## API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Estado del servidor |
| `/api/teams` | GET | 48 equipos con grupo, ELO y confederación |
| `/api/simulation?seed=N` | GET | Simula un Mundial completo |
| `/api/monte-carlo` | GET | Probabilidades pre-computadas (10,000 sims) |
| `/api/predict` | POST | Predice un partido individual |
| `/api/model-info` | GET | Información del modelo y métricas |

## Tecnologías

**Modelo**: Python, pandas, NumPy, scikit-learn, XGBoost, LightGBM, Optuna

**Backend**: FastAPI, uvicorn

**Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, Framer Motion

## Datos

Dataset de [Mart Jürisoo en Kaggle](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) — 49,071 partidos internacionales de selecciones nacionales desde 1872 hasta 2024.
