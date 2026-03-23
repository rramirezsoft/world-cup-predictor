"""
Calculo de forma reciente y rachas para cada equipo.
"""

from collections import defaultdict, deque
from model.config import FORM_WINDOW, STREAK_MAX


class FormTracker:
    """Rastrea la forma reciente de cada equipo con ventana deslizante."""

    def __init__(self, window=FORM_WINDOW):
        self.window = window
        self.history = {}
        self.streaks = {}
        self.unbeaten_streaks = {}
        self.last_match_date = {}
        self.home_record = {}
        self.away_record = {}

    def _get_history(self, team):
        if team not in self.history:
            self.history[team] = deque(maxlen=self.window)
        return self.history[team]

    def _get_home_record(self, team):
        if team not in self.home_record:
            self.home_record[team] = deque(maxlen=self.window)
        return self.home_record[team]

    def _get_away_record(self, team):
        if team not in self.away_record:
            self.away_record[team] = deque(maxlen=self.window)
        return self.away_record[team]

    def get_form(self, team):
        """
        Devuelve dict con features de forma para un equipo.
        Si no hay historial, devuelve valores neutros (0.33, 0.33, 0.33...).
        """
        hist = self._get_history(team)
        if len(hist) == 0:
            return {
                "form_wins": 1 / 3,
                "form_draws": 1 / 3,
                "form_losses": 1 / 3,
                "form_gf": 1.0,
                "form_gc": 1.0,
                "form_points": 0.5,
                "form_gd": 0.0,
            }

        n = len(hist)
        wins = sum(1 for r in hist if r[0] == "W")
        draws = sum(1 for r in hist if r[0] == "D")
        losses = sum(1 for r in hist if r[0] == "L")
        gf = sum(r[1] for r in hist)
        gc = sum(r[2] for r in hist)
        points = wins * 3 + draws

        return {
            "form_wins": wins / n,
            "form_draws": draws / n,
            "form_losses": losses / n,
            "form_gf": gf / n,
            "form_gc": gc / n,
            "form_points": points / (n * 3),
            "form_gd": (gf - gc) / n,
        }

    def get_streak(self, team):
        """Devuelve racha actual (positiva = victorias, negativa = derrotas)."""
        return self.streaks.get(team, 0)

    def get_unbeaten_streak(self, team):
        """Devuelve partidos seguidos sin perder."""
        return self.unbeaten_streaks.get(team, 0)

    def get_days_since_last_match(self, team, current_date):
        """Devuelve dias desde ultimo partido, o 30 si no hay historial."""
        if team not in self.last_match_date:
            return 30  # valor por defecto
        delta = (current_date - self.last_match_date[team]).days
        return min(delta, 365)  # cap a 1 año

    def get_clean_sheet_pct(self, team):
        """Porcentaje de porterias a cero en ultimos N partidos."""
        hist = self._get_history(team)
        if len(hist) == 0:
            return 0.0
        return sum(1 for r in hist if r[5]) / len(hist)

    def get_home_record(self, team):
        """Win rate jugando como LOCAL en ultimos N partidos como local."""
        rec = self._get_home_record(team)
        if len(rec) == 0:
            return 0.5
        return sum(rec) / len(rec)

    def get_away_record(self, team):
        """Win rate jugando como VISITANTE en ultimos N partidos como visitante."""
        rec = self._get_away_record(team)
        if len(rec) == 0:
            return 0.33
        return sum(rec) / len(rec)

    def update(self, team, result, goals_for, goals_against, date, was_home):
        """Actualiza historial tras un partido."""
        conceded_zero = goals_against == 0
        self._get_history(team).append((result, goals_for, goals_against, date, was_home, conceded_zero))
        self.last_match_date[team] = date

        # Actualizar rachas
        cur_streak = self.streaks.get(team, 0)
        cur_unbeaten = self.unbeaten_streaks.get(team, 0)
        if result == "W":
            self.streaks[team] = max(0, cur_streak) + 1
            self.unbeaten_streaks[team] = cur_unbeaten + 1
        elif result == "L":
            self.streaks[team] = min(0, cur_streak) - 1
            self.unbeaten_streaks[team] = 0
        else:  # Draw
            self.streaks[team] = 0
            self.unbeaten_streaks[team] = cur_unbeaten + 1

        # Clamp streaks
        self.streaks[team] = max(-STREAK_MAX, min(STREAK_MAX, self.streaks[team]))

        # Actualizar registro local/visitante
        win_val = 1.0 if result == "W" else (0.5 if result == "D" else 0.0)
        if was_home:
            self._get_home_record(team).append(win_val)
        else:
            self._get_away_record(team).append(win_val)
