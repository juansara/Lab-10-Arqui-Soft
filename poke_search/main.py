from fastapi import FastAPI, Request
import httpx, time
import pandas as pd
import os
import glob
from .logger import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

app = FastAPI()
logger = get_logger("poke_search")

# Cargar CSV una vez al inicio
poke_stats_df = pd.read_csv("data/poke_stats/pokemon.csv")

# Global retry counter for tracking
retry_count = 0

def before_retry_log(retry_state):
    global retry_count
    retry_count += 1
    logger.warning(f"API_RETRY attempt #{retry_count} for Pokemon API call - Previous attempt failed")

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_fixed(1),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.RequestError)),
    before=before_retry_log
)
async def get_pokeapi_data(name):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        res.raise_for_status()
        return res.json()

@app.post("/poke/search")
async def search_pokemon(payload: dict, request: Request):
    global retry_count
    retry_count = 0  # Reset retry counter for each request
    
    # Session start separator
    logger.info("=" * 30)
    logger.info(f"NEW SEARCH SESSION STARTED")
    logger.info("=" * 30)
    
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
        
        if retry_count > 0:
            logger.info(f"{request.url.path} API_CALL completed in {api_duration}ms - Status: SUCCESS (after {retry_count} retries)")
        else:
            logger.info(f"{request.url.path} API_CALL completed in {api_duration}ms - Status: SUCCESS")

        # --- 2. Search in CSV dataset ---
        csv_start = time.time()
        row = poke_stats_df[poke_stats_df['Name'].str.lower() == name]
        stats_csv = row.to_dict(orient="records")[0] if not row.empty else {}
        csv_duration = round((time.time() - csv_start) * 1000, 2)
        csv_status = "SUCCESS" if not row.empty else "NOT_FOUND"
        logger.info(f"{request.url.path} CSV_LOOKUP completed in {csv_duration}ms - Status: {csv_status}")

        # --- 3. Get all images from Pokemon folder ---
        image_start = time.time()
        image_folder = f"data/images/{name}"
        image_list = []
        
        if os.path.exists(image_folder):
            # Get all .jpg files in the folder, sorted by number
            image_files = glob.glob(f"{image_folder}/*.jpg")
            image_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            image_list = [f"/data/images/{name}/{os.path.basename(img)}" for img in image_files]
        
        image_duration = round((time.time() - image_start) * 1000, 2)
        image_count = len(image_list)
        image_status = f"FOUND_{image_count}_IMAGES" if image_count > 0 else "NO_IMAGES_FOUND"
        logger.info(f"{request.url.path} IMAGE_SCAN completed in {image_duration}ms - Status: {image_status}")

        # --- Final timing and summary ---
        total_duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | API: {api_duration}ms | CSV: {csv_duration}ms | IMG: {image_duration}ms | Retries: {retry_count}")
        
        # Session end separator
        logger.info("-" * 30)
        logger.info(f"SEARCH SESSION COMPLETED - {name.upper()} - {total_duration}ms")
        logger.info("-" * 30)

        return {
            "pokemon_info": {
                "name": name,
                "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "api_data": {
                "stats": stats_api,
                "sprite_image": image_api,
                "source": "pokeapi.co"
            },
            "csv_data": {
                "stats": stats_csv,
                "found": bool(stats_csv),
                "source": "local_dataset"
            },
            "local_assets": {
                "images": image_list,
                "image_count": image_count,
                "images_available": image_count > 0
            },
            "performance_metrics": {
                "total_duration_ms": total_duration,
                "breakdown": {
                    "api_call_ms": api_duration,
                    "csv_lookup_ms": csv_duration,
                    "image_scan_ms": image_duration
                },
                "retry_count": retry_count,
                "status": "success"
            }
        }

    except Exception as e:
        error_duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.url.path} search_pokemon ERROR after {error_duration}ms: {str(e)}")
        
        # Session end separator for errors
        logger.info("-" * 30)
        logger.error(f"SEARCH SESSION FAILED - {name.upper()} - {error_duration}ms")
        logger.info("-" * 30)
        
        return {
            "pokemon_info": {
                "name": name,
                "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "error": {
                "message": f"Failed to fetch data for {name}",
                "details": str(e)
            },
            "performance_metrics": {
                "total_duration_ms": error_duration,
                "retry_count": retry_count,
                "status": "failed"
            }
        }

