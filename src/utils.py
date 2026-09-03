from src.scrimmage.db import Player


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
