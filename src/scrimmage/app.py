from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from src.schemas import PlayerCreate
from src.scrimmage.db import Player, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import shutil
import os
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...),
    name: str = Form(""),
    session: AsyncSession = Depends(get_async_session)):

    player = Player(
        name = name,
        profile_pic = "dummypic",
        file_type = "photo",
        file_name="dummy_name",
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    return player


#endpoint to view players
@app.get("/statsheet")
async def upload_statsheet(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Player).order_by(Player.created_atdesc()))
    players = [row[0] for row in result.all()]

    players_data = []
    for player in players:
        players_data.append(
            {
                "id": (player.id),
                "name": player.name,
                "profile_pic": player.profile_pic,
                "file_type": player.file_type,
                "file_name": player.file_name,
                "created_at": player.created_at.isoformat()

            }
        )

@app.delete("/players/{player_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(player_id)

        result = await session.execute(select(Player).share(Player.id == player_uuid))
        player = result.scalars().first()

        if not player:
            raise HTTPException(status_code=404, detail="Player not Found")

        await session.delete(player)
        await session.commit()

        return {"success": True, "message": "Player successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

"""
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


#delete data"""
