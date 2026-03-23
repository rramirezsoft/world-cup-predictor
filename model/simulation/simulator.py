"""
Simulador Monte Carlo del Mundial FIFA 2026.
"""

import numpy as np
import pandas as pd
from collections import defaultdict

from model.config import (
    WORLD_CUP_2026_GROUPS, FEATURE_COLS, RANDOM_SEED,
    MONTE_CARLO_SIMULATIONS, TEAM_TO_CONFEDERATION,
)
from model.features.elo import get_tournament_weight
from model.simulation.tournament import (
    get_group_matches, compute_group_standings,
    select_best_third_placed, build_r32_bracket, build_knockout_rounds,
)


class WorldCupSimulator:
    """
    Simula el Mundial 2026 completo usando un modelo entrenado.
    """

    def __init__(self, model, elo_system, form_tracker, h2h_tracker,
                 major_exp, conf_wins, scaler=None):
        """
        Args:
            model: modelo entrenado con predict_proba
            elo_system: ELOSystem con ratings actuales
            form_tracker: FormTracker con forma actual
            h2h_tracker: H2HTracker con historial H2H
            major_exp: dict {team: num_major_matches}
            conf_wins: dict de fortaleza por confederacion
            scaler: StandardScaler si el modelo lo necesita (None para tree-based)
        """
        self.model = model
        self.elo = elo_system
        self.form = form_tracker
        self.h2h = h2h_tracker
        self.major_exp = major_exp if major_exp else {}
        self.conf_wins = conf_wins if conf_wins else {}
        self.scaler = scaler

    def _build_match_features(self, home_team, away_team, is_knockout=0):
        """
        Construye el vector de features para un partido del Mundial.
        Devuelve numpy array directamente (sin crear DataFrame) para velocidad.
        """
        home_form = self.form.get_form(home_team)
        away_form = self.form.get_form(away_team)
        h2h_feats = self.h2h.get_h2h(home_team, away_team)

        home_elo = self.elo.get(home_team)
        away_elo = self.elo.get(away_team)

        home_conf = TEAM_TO_CONFEDERATION.get(home_team, "UNKNOWN")
        away_conf = TEAM_TO_CONFEDERATION.get(away_team, "UNKNOWN")
        home_conf_data = self.conf_wins.get(home_conf, {"wins": 0, "matches": 1})
        away_conf_data = self.conf_wins.get(away_conf, {"wins": 0, "matches": 1})
        if isinstance(home_conf_data, dict):
            hcs = home_conf_data.get("wins", 0) / max(home_conf_data.get("matches", 1), 1)
            acs = away_conf_data.get("wins", 0) / max(away_conf_data.get("matches", 1), 1)
        else:
            hcs, acs = 0.4, 0.4

        # Build array in FEATURE_COLS order directly
        row = np.array([
            home_elo, away_elo, home_elo - away_elo,
            self.elo.get_expected_home(home_team, away_team, neutral=True),
            home_form["form_wins"], home_form["form_draws"], home_form["form_losses"],
            home_form["form_gf"], home_form["form_gc"], home_form["form_points"], home_form["form_gd"],
            away_form["form_wins"], away_form["form_draws"], away_form["form_losses"],
            away_form["form_gf"], away_form["form_gc"], away_form["form_points"], away_form["form_gd"],
            h2h_feats["h2h_home_wins"], h2h_feats["h2h_away_wins"], h2h_feats["h2h_draws"],
            h2h_feats["h2h_home_goals"], h2h_feats["h2h_away_goals"], h2h_feats["h2h_dominance"],
            home_form["form_points"] - away_form["form_points"],
            home_form["form_gd"] - away_form["form_gd"],
            home_form["form_gf"] - away_form["form_gf"],
            1, 1.5, 1,  # neutral, tournament_weight, is_competitive
            hcs, acs, 1 if home_conf != away_conf else 0,
            self.form.get_streak(home_team), self.form.get_streak(away_team),
            self.form.get_unbeaten_streak(home_team), self.form.get_unbeaten_streak(away_team),
            4, 4, 0,  # days_rest home, away, advantage
            self.form.get_clean_sheet_pct(home_team), self.form.get_clean_sheet_pct(away_team),
            is_knockout,
            self.major_exp.get(home_team, 0), self.major_exp.get(away_team, 0),
            self.form.get_home_record(home_team), self.form.get_away_record(away_team),
        ], dtype=np.float64).reshape(1, -1)

        if self.scaler is not None:
            row = self.scaler.transform(pd.DataFrame(row, columns=FEATURE_COLS))
            return row
        return row

    def predict_match(self, home_team, away_team, is_knockout=0):
        """
        Predice las probabilidades de un partido.

        Returns:
            dict con: home_win_prob, draw_prob, away_win_prob
        """
        X = self._build_match_features(home_team, away_team, is_knockout)
        proba = self.model.predict_proba(X)[0]

        return {
            "away_win_prob": proba[0],  # class 0
            "draw_prob": proba[1],      # class 1
            "home_win_prob": proba[2],  # class 2
        }

    def simulate_match(self, home_team, away_team, is_knockout=0, rng=None):
        """
        Simula un partido usando las probabilidades del modelo.

        Para fase de grupos: puede haber empate.
        Para eliminatorias: si hay empate, se decide por penaltis.

        Returns:
            dict con: home_team, away_team, home_score, away_score, winner
        """
        if rng is None:
            rng = np.random.default_rng()

        probs = self.predict_match(home_team, away_team, is_knockout)

        # Normalizar probabilidades (floating point precision)
        p = np.array([probs["away_win_prob"], probs["draw_prob"], probs["home_win_prob"]])
        p = np.clip(p, 0, 1)
        p = p / p.sum()

        # Samplear resultado basado en probabilidades
        outcome = rng.choice([0, 1, 2], p=p)

        # Generar marcador aproximado
        if outcome == 2:  # Home win
            home_score = rng.choice([1, 2, 3], p=[0.45, 0.35, 0.20])
            away_score = rng.choice([0, 1], p=[0.60, 0.40])
            if away_score >= home_score:
                away_score = home_score - 1
            winner = home_team
        elif outcome == 0:  # Away win
            away_score = rng.choice([1, 2, 3], p=[0.45, 0.35, 0.20])
            home_score = rng.choice([0, 1], p=[0.60, 0.40])
            if home_score >= away_score:
                home_score = away_score - 1
            winner = away_team
        else:  # Draw
            score = rng.choice([0, 1, 2], p=[0.35, 0.45, 0.20])
            home_score = away_score = score
            winner = "draw"

        # En eliminatoria, el empate se resuelve por penaltis
        if is_knockout and winner == "draw":
            # Decidir penaltis: equipo con mayor ELO tiene ligera ventaja
            home_elo = self.elo.get(home_team)
            away_elo = self.elo.get(away_team)
            elo_diff = home_elo - away_elo
            # Probabilidad base 50-50, ajustada ligeramente por ELO
            home_penalty_prob = 0.5 + np.clip(elo_diff / 2000, -0.15, 0.15)
            if rng.random() < home_penalty_prob:
                winner = home_team
            else:
                winner = away_team

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_score": max(0, int(home_score)),
            "away_score": max(0, int(away_score)),
            "winner": winner,
        }

    def simulate_group_stage(self, rng=None):
        """
        Simula toda la fase de grupos.

        Returns:
            tuple (all_standings, all_matches)
            - all_standings: dict {group_name: standings_df}
            - all_matches: dict {group_name: [match_dicts]}
        """
        if rng is None:
            rng = np.random.default_rng()

        group_matches = get_group_matches()
        all_standings = {}
        all_matches = {}

        for group_name in WORLD_CUP_2026_GROUPS:
            group_results = []
            for g, home, away in group_matches:
                if g == group_name:
                    result = self.simulate_match(home, away, is_knockout=0, rng=rng)
                    group_results.append(result)

            standings = compute_group_standings(group_results)
            all_standings[group_name] = standings
            all_matches[group_name] = group_results

        return all_standings, all_matches

    def simulate_knockout_stage(self, all_standings, rng=None):
        """
        Simula las eliminatorias desde R32 hasta la final.

        Returns:
            dict con champion, runner_up, y resultados por ronda.
        """
        if rng is None:
            rng = np.random.default_rng()

        # Seleccionar mejores terceros
        best_thirds = select_best_third_placed(all_standings)

        # Construir bracket R32
        r32_bracket = build_r32_bracket(all_standings, best_thirds)

        results = {"r32": [], "r16": [], "qf": [], "sf": [], "final": []}

        # Simular R32
        r32_winners = []
        for team1, team2 in r32_bracket:
            match = self.simulate_match(team1, team2, is_knockout=1, rng=rng)
            results["r32"].append(match)
            r32_winners.append(match["winner"])

        # R16
        r16_matches = build_knockout_rounds(r32_winners)
        r16_winners = []
        for team1, team2 in r16_matches:
            match = self.simulate_match(team1, team2, is_knockout=1, rng=rng)
            results["r16"].append(match)
            r16_winners.append(match["winner"])

        # Cuartos de final
        qf_matches = build_knockout_rounds(r16_winners)
        qf_winners = []
        for team1, team2 in qf_matches:
            match = self.simulate_match(team1, team2, is_knockout=1, rng=rng)
            results["qf"].append(match)
            qf_winners.append(match["winner"])

        # Semifinales
        sf_matches = build_knockout_rounds(qf_winners)
        sf_winners = []
        for team1, team2 in sf_matches:
            match = self.simulate_match(team1, team2, is_knockout=1, rng=rng)
            results["sf"].append(match)
            sf_winners.append(match["winner"])

        # Final
        if len(sf_winners) >= 2:
            final = self.simulate_match(sf_winners[0], sf_winners[1], is_knockout=1, rng=rng)
            results["final"].append(final)
            champion = final["winner"]
            runner_up = sf_winners[1] if champion == sf_winners[0] else sf_winners[0]
        else:
            champion = sf_winners[0] if sf_winners else "Unknown"
            runner_up = "Unknown"

        return {
            "champion": champion,
            "runner_up": runner_up,
            "results": results,
        }

    def simulate_tournament(self, rng=None):
        """Simula un torneo completo (grupos + eliminatorias)."""
        if rng is None:
            rng = np.random.default_rng()

        group_standings, group_matches = self.simulate_group_stage(rng=rng)
        knockout_results = self.simulate_knockout_stage(group_standings, rng=rng)

        return {
            "group_standings": group_standings,
            "group_matches": group_matches,
            **knockout_results,
        }

    def monte_carlo(self, n_simulations=MONTE_CARLO_SIMULATIONS, seed=RANDOM_SEED):
        """
        Ejecuta N simulaciones Monte Carlo del torneo completo.

        Returns:
            DataFrame con probabilidades por equipo:
            - champion_pct: % de veces campeon
            - final_pct: % de veces en la final
            - sf_pct: % de veces en semifinales
            - qf_pct: % de veces en cuartos
            - r16_pct: % de veces en R16
            - group_exit_pct: % de veces eliminado en grupos
        """
        print(f"Ejecutando {n_simulations:,} simulaciones Monte Carlo...")

        all_teams = []
        for teams in WORLD_CUP_2026_GROUPS.values():
            all_teams.extend(teams)

        # Contadores
        champion_count = defaultdict(int)
        final_count = defaultdict(int)
        sf_count = defaultdict(int)
        qf_count = defaultdict(int)
        r16_count = defaultdict(int)
        r32_count = defaultdict(int)

        rng = np.random.default_rng(seed)

        for sim in range(n_simulations):
            if (sim + 1) % (n_simulations // 10) == 0:
                print(f"  Simulacion {sim + 1:,}/{n_simulations:,}")

            try:
                result = self.simulate_tournament(rng=rng)

                champion_count[result["champion"]] += 1
                final_count[result["champion"]] += 1
                final_count[result["runner_up"]] += 1

                # Contar avance por ronda
                for match in result["results"].get("sf", []):
                    sf_count[match["home_team"]] += 1
                    sf_count[match["away_team"]] += 1
                for match in result["results"].get("qf", []):
                    qf_count[match["home_team"]] += 1
                    qf_count[match["away_team"]] += 1
                for match in result["results"].get("r16", []):
                    r16_count[match["home_team"]] += 1
                    r16_count[match["away_team"]] += 1
                for match in result["results"].get("r32", []):
                    r32_count[match["home_team"]] += 1
                    r32_count[match["away_team"]] += 1

            except Exception:
                continue

        # Construir DataFrame de resultados
        rows = []
        for team in all_teams:
            rows.append({
                "team": team,
                "champion_pct": champion_count[team] / n_simulations * 100,
                "final_pct": final_count[team] / n_simulations * 100,
                "sf_pct": sf_count[team] / n_simulations * 100,
                "qf_pct": qf_count[team] / n_simulations * 100,
                "r16_pct": r16_count[team] / n_simulations * 100,
                "r32_pct": r32_count[team] / n_simulations * 100,
                "elo": self.elo.get(team),
            })

        df = pd.DataFrame(rows).sort_values("champion_pct", ascending=False).reset_index(drop=True)

        print(f"\nSimulacion completada. Top 10 favoritos:")
        print(f"{'Pos':>4s}  {'Equipo':25s} {'Campeon%':>9s} {'Final%':>8s} {'Semi%':>7s} {'ELO':>6s}")
        print("-" * 65)
        for i, row in df.head(10).iterrows():
            print(f"{i+1:4d}  {row['team']:25s} {row['champion_pct']:8.1f}% "
                  f"{row['final_pct']:7.1f}% {row['sf_pct']:6.1f}% {row['elo']:6.0f}")

        return df
