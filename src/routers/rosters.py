import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.schemas import DraftPlayer, RosterCreate
from src.scrimmage.db import Player, Roster, RosterPlayer, get_async_session


router = APIRouter(prefix="/rosters", tags=["rosters"])

NAMED_SLOTS = {"QB", "RB1", "RB2", "WR1", "WR2", "TE", "EDGE", "CB1"}
UNIT_ROOMS = {"OL_UNIT", "DL_UNIT", "LB_UNIT", "CB_UNIT", "S_UNIT"}
VALID_SLOTS = NAMED_SLOTS | UNIT_ROOMS


@router.post("")
async def create_roster(
    roster_data: RosterCreate,
    session: AsyncSession = Depends(get_async_session),
):
    roster = Roster(name=roster_data.name)
    session.add(roster)
    await session.commit()
    await session.refresh(roster)

    return {
        "id": str(roster.id),
        "name": roster.name,
        "created_at": roster.created_at.isoformat(),
    }


@router.get("")
async def get_rosters(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Roster).order_by(Roster.created_at.desc())
    )
    rosters = result.scalars().all()

    return [
        {
            "id": str(roster.id),
            "name": roster.name,
            "created_at": roster.created_at.isoformat(),
        }
        for roster in rosters
    ]


@router.post("/{roster_id}/draft")
async def draft_player(
    roster_id: str,
    draft_data: DraftPlayer,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        roster_uuid = uuid.UUID(roster_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roster_id format")

    roster_result = await session.execute(select(Roster).where(Roster.id == roster_uuid))
    if roster_result.scalars().first() is None:
        raise HTTPException(status_code=404, detail="Roster not found")

    try:
        player_uuid = uuid.UUID(draft_data.player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player_id format")

    player_result = await session.execute(select(Player).where(Player.id == player_uuid))
    if player_result.scalars().first() is None:
        raise HTTPException(status_code=404, detail="Player not found")

    if draft_data.slot not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail="Invalid slot")

    if draft_data.slot in NAMED_SLOTS:
        slot_result = await session.execute(
            select(RosterPlayer).where(
                RosterPlayer.roster_id == roster_uuid,
                RosterPlayer.slot == draft_data.slot,
            )
        )
        if slot_result.scalars().first() is not None:
            raise HTTPException(status_code=400, detail="Slot already filled")

    roster_player = RosterPlayer(
        roster_id=roster_uuid,
        player_id=player_uuid,
        slot=draft_data.slot,
    )
    session.add(roster_player)
    await session.commit()
    await session.refresh(roster_player)

    return {
        "id": str(roster_player.id),
        "roster_id": str(roster_player.roster_id),
        "player_id": str(roster_player.player_id),
        "slot": roster_player.slot,
    }


@router.delete("/{roster_id}/players/{roster_player_id}")
async def remove_player_from_roster(
    roster_id: str,
    roster_player_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        roster_uuid = uuid.UUID(roster_id)
        roster_player_uuid = uuid.UUID(roster_player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roster or roster player ID format")

    result = await session.execute(
        select(RosterPlayer).where(
            RosterPlayer.id == roster_player_uuid,
            RosterPlayer.roster_id == roster_uuid,
        )
    )
    roster_player = result.scalars().first()

    if roster_player is None:
        raise HTTPException(status_code=404, detail="Roster player not found")

    await session.delete(roster_player)
    await session.commit()

    return {
        "success": True,
        "message": "Player removed from roster",
    }


@router.get("/{roster_id}")
async def get_roster(roster_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        roster_uuid = uuid.UUID(roster_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roster_id format")

    result = await session.execute(
        select(Roster)
        .options(selectinload(Roster.players).selectinload(RosterPlayer.player))
        .where(Roster.id == roster_uuid)
    )
    roster = result.scalars().first()

    if roster is None:
        raise HTTPException(status_code=404, detail="Roster not found")

    return {
        "id": str(roster.id),
        "name": roster.name,
        "created_at": roster.created_at.isoformat(),
        "players": [
            {
                "id": str(roster_player.id),
                "slot": roster_player.slot,
                "player": {
                    "id": str(roster_player.player.id),
                    "first_name": roster_player.player.first_name,
                    "last_name": roster_player.player.last_name,
                    "position": roster_player.player.position.value,
                    "team": roster_player.player.team,
                },
            }
            for roster_player in roster.players
        ],
    }
