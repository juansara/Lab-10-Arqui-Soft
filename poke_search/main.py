from fastapi import FastAPI, Request
import httpx, time
import pandas as pd
import os
from .logger import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed

app = FastAPI()
logger = get_logger("poke_search")

# Cargar CSV una vez al inicio
poke_stats_df = pd.read_csv("data/poke_stats/pokemon.csv")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_pokeapi_data(name):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        res.raise_for_status()
        return res.json()

@app.post("/poke/search")
async def search_pokemon(payload: dict, request: Request):
    start_time = time.time()
    name = payload.get("Pokemon_Name", "").lower()
    logger.info(f"{request.url.path} search_pokemon Started for: {name}")

    try:
        # --- 1. Call POKE_API ---
        api_start = time.time()
        poke_data = await get_pokeapi_data(name)
        stats_api = poke_data.get("stats", [])
        image_api = poke_data["sprites"]["front_default"]
        api_duration = round((time.time() - api_start) * 1000, 2)
        logger.info(f"{request.url.path} API_CALL completed in {api_duration}ms - Status: SUCCESS")

        # --- 2. Search in CSV dataset ---
        csv_start = time.time()
        row = poke_stats_df[poke_stats_df['Name'].str.lower() == name]
        stats_csv = row.to_dict(orient="records")[0] if not row.empty else {}
        csv_duration = round((time.time() - csv_start) * 1000, 2)
        csv_status = "SUCCESS" if not row.empty else "NOT_FOUND"
        logger.info(f"{request.url.path} CSV_LOOKUP completed in {csv_duration}ms - Status: {csv_status}")

        # --- 3. Get image path (simulate as local asset or host URL) ---
        image_start = time.time()
        image_filename = "0.jpg"
        image_path = f"/data/images/{name}/{image_filename}"
        image_exists = os.path.exists(f"data/images/{name}/{image_filename}")
        image_duration = round((time.time() - image_start) * 1000, 2)
        image_status = "FOUND" if image_exists else "NOT_FOUND"
        logger.info(f"{request.url.path} IMAGE_CHECK completed in {image_duration}ms - Status: {image_status}")

        # --- Final timing and summary ---
        total_duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | API: {api_duration}ms | CSV: {csv_duration}ms | IMG: {image_duration}ms")

        return {
            "name": name,
            "image_api": image_api,
            "image_local": image_path if image_exists else None,
            "stats_api": stats_api,
            "stats_csv": stats_csv,
            "performance": {
                "total_ms": total_duration,
                "api_ms": api_duration,
                "csv_ms": csv_duration,
                "image_ms": image_duration
            }
        }

    except Exception as e:
        error_duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.url.path} search_pokemon ERROR after {error_duration}ms: {str(e)}")
        return {"error": f"Failed to fetch data for {name}", "duration_ms": error_duration}



# @app.post("/poke/search")
# async def search_pokemon(payload: dict, request: Request):
#     start_time = time.time()
#     name = payload.get("Pokemon_Name", "").lower()

#     logger.info(f"{request.url.path} search_pokemon Request received: {payload}")

#     try:
#         url = f"https://pokeapi.co/api/v2/pokemon/{name}"
#         async with httpx.AsyncClient() as client:
#             res = await client.get(url)
#         res.raise_for_status()

#         data = res.json()
#         stats = data.get("stats", [])
#         image = data["sprites"]["front_default"]

#         duration = round((time.time() - start_time) * 1000, 2)
#         logger.info(f"{request.url.path} search_pokemon Completed in {duration}ms")

#         return {
#             "name": name,
#             "stats": stats,
#             "image": image
#         }

#     except Exception as e:
#         logger.error(f"{request.url.path} search_pokemon Error: {e}")
#         return {"error": "Pokemon not found or API error"}
