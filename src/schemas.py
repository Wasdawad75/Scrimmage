# Defines the type of data we accept in our endpoints.
from pydantic import BaseModel


class PlayerStats(BaseModel):
    passing_yards: int | None = None
    rushing_yards: int | None = None
    receptions: int | None = None
    receiving_yards: int | None = None
    touchdowns: int | None = None
    interceptions: int | None = None
    total_touchdowns: int | None = None


class PlayerCreate(BaseModel):
    id: int
    full_name: str
    position: str
    jersey_number: int
    team: str
    photo_url: str
    height: str
    weight: int
    stats: PlayerStats