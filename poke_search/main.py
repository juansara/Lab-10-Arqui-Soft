from fastapi import FastAPI, Request
import httpx
import time
from .logger import get_logger

app = FastAPI()
logger = get_logger("poke_search")

@app.post("/poke/search")
async def search_pokemon(payload: dict, request: Request):
    start_time = time.time()
    name = payload.get("Pokemon_Name", "").lower()

    logger.info(f"{request.url.path} search_pokemon Request received: {payload}")

    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.raise_for_status()

        data = res.json()
        stats = data.get("stats", [])
        image = data["sprites"]["front_default"]

        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.url.path} search_pokemon Completed in {duration}ms")

        return {
            "name": name,
            "stats": stats,
            "image": image
        }

    except Exception as e:
        logger.error(f"{request.url.path} search_pokemon Error: {e}")
        return {"error": "Pokemon not found or API error"}
