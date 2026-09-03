from contextlib import asynccontextmanager
import uuid

from fastapi import Depends, FastAPI, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers import players
from src.routers import rosters
from src.scrimmage.db import Player, create_db_and_tables, get_async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(players.router)
app.include_router(rosters.router)


@app.post("/upload")
async def upload_player_photo(
    player_id: str = Form(...),
    photo_url: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    result = await session.execute(select(Player).where(Player.id == player_uuid))
    player = result.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player.photo_url = photo_url
    await session.commit()
    await session.refresh(player)

    return {
        "id": str(player.id),
        "first_name": player.first_name,
        "last_name": player.last_name,
        "photo_url": player.photo_url,
    }
