from datetime import date
from typing import List

import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams


# from nba_api.stats.endpoints import boxscoretraditionalv2
# box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id) this works

class NBADal:

    @staticmethod
    def get_team_by_name(name) -> List[dict]:
        nba_teams = teams.find_teams_by_full_name(name)
        return nba_teams

    @staticmethod
    def get_last_game():
        games = leaguegamefinder.LeagueGameFinder().get_data_frames()[0]
        #filter unfinished games
        games = games[games.apply(lambda x: x["WL"] is not None, axis=1)]
        last_game = games.iloc[0]
        return last_game


    @staticmethod
    def get_games(team_id: str) -> pd.DataFrame:
        game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
        games = game_finder.get_data_frames()
        if len(games) > 1:
            raise NotImplemented("got more then one df")
        games_df = games[0]
        return games_df

    @staticmethod
    def get_game(game_id: str) -> pd.Series:
        game_finder = leaguegamefinder.LeagueGameFinder(game_id_nullable=game_id)
        games = game_finder.get_data_frames()[0]
        game = games[games['GAME_ID'] == game_id]
        return game.iloc[0]

