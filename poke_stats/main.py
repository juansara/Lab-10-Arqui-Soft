from ..poke_search.main import app, poke_stats_df
from .logger import get_logger
from fastapi import Request

logger = get_logger("poke_stats")

@app.get("/poke/stats/{pokemon_name}")
async def get_pokemon_stats(pokemon_name: str, request: Request):
    try:
        poke_stats_df = poke_stats_df[poke_stats_df["Name"].str.lower() == pokemon_name.lower()]
        if poke_stats_df.empty:
            logger.error(f"Pokemon {pokemon_name} not found in local dataset")
            return {"error": f"Pokemon {pokemon_name} not found in local dataset"}
        stats = poke_stats_df.to_dict(orient="records")[0]
        return {
            "pokemon_name": pokemon_name,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Error fetching stats for {pokemon_name}: {str(e)}")
        return {"error": f"Failed to fetch stats for {pokemon_name}"}