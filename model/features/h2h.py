"""
Historial de enfrentamientos directos (Head-to-Head).
"""

from collections import defaultdict, deque
from model.config import H2H_WINDOW


class H2HTracker:
    """Rastrea enfrentamientos directos entre pares de equipos."""

    def __init__(self, window=H2H_WINDOW):
        self.window = window
        self.history = {}

    def _key(self, team1, team2):
        return tuple(sorted([team1, team2]))

    def get_h2h(self, home_team, away_team):
        """
        Devuelve features H2H desde la perspectiva del equipo local.
        """
        key = self._key(home_team, away_team)
        hist = self.history.get(key, deque(maxlen=self.window))

        if len(hist) == 0:
            return {
                "h2h_home_wins": 0.33,
                "h2h_away_wins": 0.33,
                "h2h_draws": 0.33,
                "h2h_home_goals": 1.0,
                "h2h_away_goals": 1.0,
                "h2h_dominance": 0.0,
            }

        n = len(hist)
        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = 0
        away_goals = 0

        for winner, g_team1, g_team2, team1, team2 in hist:
            # Determinar goles desde la perspectiva de home_team y away_team
            if team1 == home_team:
                hg, ag = g_team1, g_team2
            else:
                hg, ag = g_team2, g_team1

            home_goals += hg
            away_goals += ag

            if winner == home_team:
                home_wins += 1
            elif winner == away_team:
                away_wins += 1
            else:
                draws += 1

        return {
            "h2h_home_wins": home_wins / n,
            "h2h_away_wins": away_wins / n,
            "h2h_draws": draws / n,
            "h2h_home_goals": home_goals / n,
            "h2h_away_goals": away_goals / n,
            "h2h_dominance": (home_wins - away_wins) / n,
        }

    def update(self, home_team, away_team, home_score, away_score):
        """Registra un nuevo enfrentamiento."""
        key = self._key(home_team, away_team)

        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team
        else:
            winner = "draw"

        if key not in self.history:
            self.history[key] = deque(maxlen=self.window)
        self.history[key].append((winner, home_score, away_score, home_team, away_team))
