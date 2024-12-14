from __future__ import annotations

import datetime
from typing import Optional

import numpy as np
import pandas as pd
from nba_api.stats.endpoints import boxscoreadvancedv2

from dal.nba_dal import NBADal
from nba.team import Team

_date_format = '%Y-%m-%d'

DATE_COL = "GAME_DATE"
MATCHUP_COL = "MATCHUP"
AWAY_COL = "AWAY_ABBRV"
ID_COL = "GAME_ID"


class Game:

    def __init__(self, game_id: str, game: Optional[pd.Series] = None):
        self.id = game_id
        if game is None:
            game = NBADal().get_game(game_id)
        self.game = game

    @classmethod
    def from_matchup(cls, home_team: Team, away_team: Team, date: datetime.datetime):
        games = NBADal().get_games(home_team.id)
        games = cls._filter_by_date(date, games)
        games = cls._filter_by_away(away_team, games)
        assert games.shape[0] == 1, "need to be more specific, multiple games were found"
        game = games.iloc[0]
        game_id = game[ID_COL]
        return cls(game_id, game)

    @classmethod
    def from_game(cls, game: pd.Series):
        game_id = game[ID_COL]
        return cls(game_id, game)

    @staticmethod
    def _filter_by_date(date: datetime.datetime, games: pd.DataFrame):
        games = games[games[DATE_COL] == date.strftime(_date_format)]
        return games


    @staticmethod
    def _filter_by_away(team: Team, games: pd.DataFrame):
        games[AWAY_COL] = games[MATCHUP_COL].apply(lambda match: match.split()[-1])
        games = games[games[AWAY_COL] == team.abbreviation]
        return games

    def as_dict(self):
        teams = self.game['MATCHUP'].split()
        return {"matchup": self.game["MATCHUP"],
                "whoWon": teams[0] if self.game['WL']=='W' else teams[-1],
                "lead_changes": self.lead_changes_per_q(),
                "points_margin": self.points_margin_per_q(),
                **{"total_points": self.points_tally()},
                **{"three_pointers": self.three_pointers()}}

    def three_pointers(self):
        from nba_api.stats.endpoints import BoxScoreTraditionalV2
        a = BoxScoreTraditionalV2(game_id=self.id).team_stats.get_data_frame()
        three_pointers = a[['TEAM_ABBREVIATION', 'FG3M']]
        return three_pointers.set_index('TEAM_ABBREVIATION')['FG3M'].to_dict()



    def points_tally(self):
        from nba_api.stats.endpoints import BoxScoreSummaryV2
        line_scores = BoxScoreSummaryV2(game_id=self.id).line_score.get_data_frame()
        points = line_scores[['TEAM_ABBREVIATION', 'PTS']]
        return points.set_index('TEAM_ABBREVIATION')['PTS'].to_dict()

    def points_margin_per_q(self):
        from nba_api.stats.endpoints import PlayByPlayV2
        a = PlayByPlayV2(game_id=self.id).get_data_frames()[0]
        b = a[['PERIOD', 'SCORE', 'SCOREMARGIN']].replace("TIE", 0).dropna().drop_duplicates(subset=['SCORE','SCOREMARGIN'])
        point_margins = {"1": 0, "2": 0, "3": 0, "4":0}
        for q in point_margins:
            period_margins = b[b['PERIOD'] == int(q)]
            point_margins[q] = period_margins['SCOREMARGIN'].iloc[-1]
        return point_margins



    def lead_changes_per_q(self):
        from nba_api.stats.endpoints import PlayByPlayV2
        a = PlayByPlayV2(game_id=self.id).get_data_frames()[0]
        b = a[['PERIOD','SCORE','SCOREMARGIN']].replace("TIE", 0).dropna().drop_duplicates(subset=['SCORE','SCOREMARGIN'])
        b['MARGINDIFF'] = b['SCOREMARGIN'].astype(int).apply(lambda x: np.sign(x))
        lead_changes = {"1": 0, "2": 0, "3": 0, "4":0}
        for q in lead_changes:
            period_margins = b[b['PERIOD'] == int(q)]
            prev_change = 0
            changes = 0
            for change in period_margins['MARGINDIFF'].to_list():
                if change != 0:
                    if change != prev_change:
                        changes += 1
                    prev_change = change

            lead_changes[q] = changes
        return lead_changes


