from collections.abc import AsyncGenerator
import uuid
from datetime import date, datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Enum, Uuid
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship


DATABASE_URL = "sqlite+aiosqlite:///.test.db"  # async sqlite connection


class Base(DeclarativeBase):
    pass


class Position(str, PyEnum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    OT = "OT"
    G = "G"
    C = "C"
    DE = "DE"
    DT = "DT"
    LB = "LB"
    CB = "CB"
    S = "S"
    K = "K"
    P = "P"


class Player(Base):
    __tablename__ = "players"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    position = Column(Enum(Position), nullable=False)
    team = Column(String, nullable=False)
    jersey_number = Column(Integer, nullable=True)
    height = Column(String, nullable=True)
    weight = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=True)
    college = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)

    season_stats = relationship(
        "PlayerSeasonStats",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    roster_players = relationship(
        "RosterPlayer",
        back_populates="player",
        cascade="all, delete-orphan",
    )


class PlayerSeasonStats(Base):
    __tablename__ = "player_season_stats"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    player_id = Column(Uuid, ForeignKey("players.id"), nullable=False)
    season = Column(Integer, nullable=False)

    # Passing stats
    passing_yards = Column(Integer, nullable=True)
    passing_tds = Column(Integer, nullable=True)
    interceptions = Column(Integer, nullable=True)

    # Rushing stats
    rushing_yards = Column(Integer, nullable=True)
    rushing_tds = Column(Integer, nullable=True)

    # Receiving stats
    receptions = Column(Integer, nullable=True)
    receiving_yards = Column(Integer, nullable=True)
    receiving_tds = Column(Integer, nullable=True)

    # Defensive stats
    sacks = Column(Integer, nullable=True)
    tackles = Column(Integer, nullable=True)
    forced_fumbles = Column(Integer, nullable=True)
    pass_deflections = Column(Integer, nullable=True)

    # Kicking stats
    field_goals = Column(Integer, nullable=True)
    extra_points = Column(Integer, nullable=True)

    player = relationship("Player", back_populates="season_stats")


class Roster(Base):
    __tablename__ = "rosters"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    players = relationship(
        "RosterPlayer",
        back_populates="roster",
        cascade="all, delete-orphan",
    )


class RosterPlayer(Base):
    __tablename__ = "roster_players"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    roster_id = Column(Uuid, ForeignKey("rosters.id"), nullable=False)
    player_id = Column(Uuid, ForeignKey("players.id"), nullable=False)
    slot = Column(String, nullable=False)

    roster = relationship("Roster", back_populates="players")
    player = relationship("Player", back_populates="roster_players")


# create the database
engine = create_async_engine(DATABASE_URL)
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session
    
