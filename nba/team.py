from datetime import datetime

from dal.nba_dal import NBADal


class Team:

    def __init__(self, full_name: str, id: str, abbreviation: str, nickname: str, *args, **kwargs):
        self.name = full_name
        self.id = id
        self.abbreviation = abbreviation
        self.nickname = nickname

    @classmethod
    def from_name(cls, name: str):
        team_docs = NBADal().get_team_by_name(name)
        assert len(team_docs) == 1, "more then one team found, be more specific"
        return cls(**team_docs[0])


    def dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "abbreviation": self.abbreviation,
            "nickname": self.nickname
        }
