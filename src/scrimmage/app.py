from fastapi import FastAPI, HTTPException
from src.schemas import PlayerCreate

app = FastAPI()

players_ = [
    {
        "id": 3139477,
        "full_name": "Patrick Mahomes",
        "position": "Quarterback",
        "jersey_number": 15,
        "team": "Kansas City Chiefs",
        "photo_url": "https://espncdn.com",
        "height": "6-2",
        "weight": 225,
        "stats": {
            "passing_yards": 4183,
            "touchdowns": 27,
            "interceptions": 14
        }
    },
    {
        "id": 3916387,
        "full_name": "Lamar Jackson",
        "position": "Quarterback",
        "jersey_number": 8,
        "team": "Baltimore Ravens",
        "photo_url": "https://espncdn.com",
        "height": "6-2",
        "weight": 215,
        "stats": {
            "passing_yards": 3678,
            "rushing_yards": 821,
            "touchdowns": 29
        }
    },
    {
        "id": 4262921,
        "full_name": "Justin Jefferson",
        "position": "Wide Receiver",
        "jersey_number": 18,
        "team": "Minnesota Vikings",
        "photo_url": "https://espncdn.com",
        "height": "6-1",
        "weight": 195,
        "stats": {
            "receptions": 68,
            "receiving_yards": 1074,
            "touchdowns": 5
        }
    },
    {
        "id": 3117251,
        "full_name": "Christian McCaffrey",
        "position": "Running Back",
        "jersey_number": 23,
        "team": "San Francisco 49ers",
        "photo_url": "https://espncdn.com",
        "height": "5-11",
        "weight": 210,
        "stats": {
            "rushing_yards": 1459,
            "receiving_yards": 564,
            "total_touchdowns": 21
        }
    },
    {
        "id": 4360310,
        "full_name": "Amon-Ra St. Brown",
        "position": "Wide Receiver",
        "jersey_number": 14,
        "team": "Detroit Lions",
        "photo_url": "https://espncdn.com",
        "height": "6-0",
        "weight": 202,
        "stats": {
            "receptions": 119,
            "receiving_yards": 1515,
            "touchdowns": 10
        }
    }
]


@app.get("/players")

def get_all_players(limit: int = None):
    return players_

@app.get("/players/{id}")

def get_player(id: int):
    for player in players_:
        if player["id"] == id:
            return player
    raise HTTPException(status_code=404, detail="Player Not Found")


#Goal is to make a CRUD application. create, redo, update, and delete


#Creating NEW DATA With POST
@app.post("/posts")
def create_post(post: PlayerCreate):
    new_player = post.model_dump()
    players_.append(new_player)
    return new_player