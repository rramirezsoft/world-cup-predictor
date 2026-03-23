"""
Sistema de rating ELO adaptado para futbol internacional.
"""

import numpy as np
from collections import defaultdict
from model.config import (
    ELO_K, ELO_INITIAL, ELO_HOME_ADV,
    TOURNAMENT_WEIGHTS, TOURNAMENT_WEIGHT_DEFAULT,
)


def get_tournament_weight(tournament):
    """Devuelve el peso del torneo para la actualizacion ELO."""
    return TOURNAMENT_WEIGHTS.get(tournament, TOURNAMENT_WEIGHT_DEFAULT)


class ELOSystem:
    """Sistema ELO adaptado para futbol internacional."""

    def __init__(self, k=ELO_K, initial=ELO_INITIAL, home_adv=ELO_HOME_ADV):
        self.k = k
        self.initial = initial
        self.home_adv = home_adv
        self.ratings = {}

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def get(self, team):
        """Devuelve el rating actual de un equipo."""
        return self.ratings.get(team, self.initial)

    def expected(self, ra, rb):
        """Probabilidad esperada de que A gane a B."""
        return 1.0 / (1.0 + 10 ** ((rb - ra) / 400))

    def _goal_multiplier(self, goal_diff):
        """Multiplicador basado en diferencia de goles."""
        diff = abs(goal_diff)
        if diff <= 1:
            return 1.0
        elif diff == 2:
            return 1.5
        elif diff == 3:
            return 1.75
        else:
            return 1.75 + (diff - 3) * 0.25

    def update(self, home_team, away_team, home_score, away_score,
               neutral=False, tournament="Friendly"):
        """
        Actualiza ratings tras un partido.
        Devuelve (nuevo_home_elo, nuevo_away_elo).
        """
        ra = self.ratings.get(home_team, self.initial)
        rb = self.ratings.get(away_team, self.initial)

        # Ajuste por campo local
        ra_adj = ra if neutral else ra + self.home_adv
        rb_adj = rb

        # Resultado esperado y real
        exp_home = self.expected(ra_adj, rb_adj)
        exp_away = 1 - exp_home

        if home_score > away_score:
            actual_home, actual_away = 1.0, 0.0
        elif home_score == away_score:
            actual_home, actual_away = 0.5, 0.5
        else:
            actual_home, actual_away = 0.0, 1.0

        # Multiplicadores
        goal_mult = self._goal_multiplier(home_score - away_score)
        weight = get_tournament_weight(tournament)

        # Actualizacion
        delta_home = self.k * weight * goal_mult * (actual_home - exp_home)
        delta_away = self.k * weight * goal_mult * (actual_away - exp_away)

        self.ratings[home_team] = ra + delta_home
        self.ratings[away_team] = rb + delta_away

        return self.ratings[home_team], self.ratings[away_team]

    def get_expected_home(self, home_team, away_team, neutral=False):
        """Calcula probabilidad esperada de victoria local sin actualizar."""
        ra = self.ratings.get(home_team, self.initial)
        rb = self.ratings.get(away_team, self.initial)
        ra_adj = ra if neutral else ra + self.home_adv
        return self.expected(ra_adj, rb)
