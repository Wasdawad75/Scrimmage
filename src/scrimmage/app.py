from contextlib import asynccontextmanager
import uuid

from fastapi import Depends, FastAPI, Form, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.schemas import PlayerCreate, PlayerSeasonStatsCreate, PlayerUpdate
from src.scrimmage.db import Player, PlayerSeasonStats, Position, create_db_and_tables, get_async_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


def player_to_dict(player: Player) -> dict:
    return {
        "id": str(player.id),
        "first_name": player.first_name,
        "last_name": player.last_name,
        "position": player.position.value if player.position else None,
        "team": player.team,
        "jersey_number": player.jersey_number,
        "height": player.height,
        "weight": player.weight,
        "photo_url": player.photo_url,
        "college": player.college,
        "birth_date": player.birth_date.isoformat() if player.birth_date else None,
        "season_stats": [
            {
                "id": str(stats.id),
                "season": stats.season,
                "passing_yards": stats.passing_yards,
                "passing_tds": stats.passing_tds,
                "interceptions": stats.interceptions,
                "rushing_yards": stats.rushing_yards,
                "rushing_tds": stats.rushing_tds,
                "receptions": stats.receptions,
                "receiving_yards": stats.receiving_yards,
                "receiving_tds": stats.receiving_tds,
                "sacks": stats.sacks,
                "tackles": stats.tackles,
                "forced_fumbles": stats.forced_fumbles,
                "pass_deflections": stats.pass_deflections,
                "field_goals": stats.field_goals,
                "extra_points": stats.extra_points,
            }
            for stats in player.season_stats
        ],
    }


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

@app.post("/players/{player_id}/stats")
async def add_season_stats(
    player_id: str,
    stats_data: PlayerSeasonStatsCreate,
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

    season_stats = PlayerSeasonStats(
        player_id=player.id,
        season=stats_data.season,
        **stats_data.stats.model_dump(),
    )
    session.add(season_stats)
    await session.commit()
    await session.refresh(season_stats)

    return {
        "id": str(season_stats.id),
        "player_id": str(season_stats.player_id),
        "season": season_stats.season,
        **stats_data.stats.model_dump(),
    }


@app.post("/players")
async def create_player(player_data: PlayerCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        position = Position(player_data.position)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid position: {player_data.position}")

    player = Player(
        first_name=player_data.first_name,
        last_name=player_data.last_name,
        position=position,
        team=player_data.team,
        jersey_number=player_data.jersey_number,
        height=player_data.height,
        weight=player_data.weight,
        photo_url=player_data.photo_url,
        college=player_data.college,
        birth_date=player_data.birth_date,
    )
    session.add(player)
    await session.flush()

    if player_data.stats is not None:
        stats_payload = player_data.stats.model_dump()
        season_stats = PlayerSeasonStats(
            player_id=player.id,
            season=player_data.season,
            **stats_payload,
        )
        session.add(season_stats)

    await session.commit()
    await session.refresh(player, attribute_names=["season_stats"])

    return player_to_dict(player)


@app.get("/players/{player_id}/career-stats")
async def get_career_stats(player_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    player_result = await session.execute(select(Player.id).where(Player.id == player_uuid))
    if player_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Player not found")

    stat_columns = (
        "passing_yards",
        "passing_tds",
        "interceptions",
        "rushing_yards",
        "rushing_tds",
        "receptions",
        "receiving_yards",
        "receiving_tds",
        "sacks",
        "tackles",
        "forced_fumbles",
        "pass_deflections",
        "field_goals",
        "extra_points",
    )
    aggregate_columns = [func.count(PlayerSeasonStats.id).label("season_count")]
    for column_name in stat_columns:
        column = getattr(PlayerSeasonStats, column_name)
        aggregate_columns.extend(
            (
                func.coalesce(func.sum(column), 0).label(f"{column_name}_total"),
                func.avg(column).label(f"{column_name}_average"),
            )
        )

    result = await session.execute(
        select(*aggregate_columns).where(PlayerSeasonStats.player_id == player_uuid)
    )
    aggregates = result.mappings().one()

    return {
        "player_id": str(player_uuid),
        "season_count": aggregates["season_count"],
        "totals": {
            column_name: aggregates[f"{column_name}_total"]
            for column_name in stat_columns
        },
        "averages": {
            column_name: aggregates[f"{column_name}_average"]
            for column_name in stat_columns
        },
    }


@app.get("/players")
async def get_players(
    position: str | None = Query(default=None, min_length=1, description="Filter by player position"),
    team: str | None = Query(default=None, min_length=1, description="Filter by team name"),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Player).options(selectinload(Player.season_stats))

    if position is not None:
        try:
            normalized_position = Position(position)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid position: {position}")
        query = query.where(Player.position == normalized_position)

    if team is not None:
        query = query.where(Player.team.ilike(f"%{team}%"))

    query = query.order_by(Player.last_name.asc(), Player.first_name.asc())
    result = await session.execute(query)
    players = result.scalars().all()

    players_data = []
    for player in players:
        players_data.append(player_to_dict(player))

    return players_data


@app.get("/players/{player_id}")
async def get_player_by_id(player_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    result = await session.execute(
        select(Player)
        .options(selectinload(Player.season_stats))
        .where(Player.id == player_uuid)
    )
    player = result.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player_to_dict(player)


@app.get("/players/compare")
async def compare_players(
    id1: str = Query(..., description="First player UUID"),
    id2: str = Query(..., description="Second player UUID"),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        player1_uuid = uuid.UUID(id1)
        player2_uuid = uuid.UUID(id2)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    result1 = await session.execute(
        select(Player)
        .options(selectinload(Player.season_stats))
        .where(Player.id == player1_uuid)
    )
    player1 = result1.scalars().first()

    result2 = await session.execute(
        select(Player)
        .options(selectinload(Player.season_stats))
        .where(Player.id == player2_uuid)
    )
    player2 = result2.scalars().first()

    if not player1:
        raise HTTPException(status_code=404, detail="Player 1 not found")
    if not player2:
        raise HTTPException(status_code=404, detail="Player 2 not found")

    return {
        "player_1": player_to_dict(player1),
        "player_2": player_to_dict(player2),
    }


@app.put("/players/{player_id}")
async def update_player(
    player_id: str,
    player_update: PlayerUpdate,
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

    if player_update.first_name is not None:
        player.first_name = player_update.first_name
    if player_update.last_name is not None:
        player.last_name = player_update.last_name
    if player_update.position is not None:
        try:
            player.position = Position(player_update.position)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid position: {player_update.position}")
    if player_update.team is not None:
        player.team = player_update.team
    if player_update.jersey_number is not None:
        player.jersey_number = player_update.jersey_number
    if player_update.height is not None:
        player.height = player_update.height
    if player_update.weight is not None:
        player.weight = player_update.weight
    if player_update.photo_url is not None:
        player.photo_url = player_update.photo_url
    if player_update.college is not None:
        player.college = player_update.college
    if player_update.birth_date is not None:
        player.birth_date = player_update.birth_date

    await session.commit()
    await session.refresh(player, attribute_names=["season_stats"])

    return player_to_dict(player)


@app.delete("/players/{player_id}")
async def delete_player(player_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    result = await session.execute(select(Player).where(Player.id == player_uuid))
    player = result.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    await session.delete(player)
    await session.commit()

    return {"success": True, "message": "Player successfully deleted"}
