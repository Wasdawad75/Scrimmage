# Defines the type of data we accept in our endpoints.
from datetime import date

from pydantic import BaseModel


class PlayerStats(BaseModel):
    passing_yards: int | None = None
    passing_tds: int | None = None
    interceptions: int | None = None
    rushing_yards: int | None = None
    rushing_tds: int | None = None
    receptions: int | None = None
    receiving_yards: int | None = None
    receiving_tds: int | None = None
    sacks: int | None = None
    tackles: int | None = None
    forced_fumbles: int | None = None
    pass_deflections: int | None = None
    field_goals: int | None = None
    extra_points: int | None = None


class PlayerCreate(BaseModel):
    first_name: str
    last_name: str
    position: str
    team: str
    jersey_number: int | None = None
    height: str | None = None
    weight: int | None = None
    photo_url: str | None = None
    college: str | None = None
    birth_date: date | None = None
    season: int = 2025
    stats: PlayerStats | None = None


class PlayerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None
    team: str | None = None
    jersey_number: int | None = None
    height: str | None = None
    weight: int | None = None
    photo_url: str | None = None
    college: str | None = None
    birth_date: date | None = None