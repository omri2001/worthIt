from datetime import datetime

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from dal.nba_dal import NBADal
from nba.game import Game
from nba.team import Team

app = FastAPI()


class WorthItInput(BaseModel):
    home_team: str
    away_team: str
    date: str


@app.post("/worth_it")
def is_it_worth_it():
    last_game = NBADal.get_last_game()
    game = Game.from_game(last_game)
    return game.as_dict()


@app.get("/team/info/{name}")
def team_info(name: str) -> dict:
    return Team.from_name(name).dict()


if __name__ == '__main__':
    uvicorn.run("app:app", port=8080, reload=True)
