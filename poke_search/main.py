from fastapi import FastAPI, Request
import httpx, time
import pandas as pd
import os
import glob
from .logger import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

app = FastAPI()
logger = get_logger("poke_search")

@app.post("/poke/search")
async def search_pokemon(payload: dict, request: Request):
    logger.info("=" * 30)
    logger.info("NEW SEARCH SESSION STARTED")
    logger.info("=" * 30)

    start_time = time.time()
    name = payload.get("Pokemon_Name", "").lower()
    logger.info(f"{request.url.path} search_pokemon Started for: {name}")

    results = {
        "pokemon_info": {
            "name": name,
            "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "api_data": {},
        "csv_data": {},
        "local_assets": {},
        "performance_metrics": {
            "total_duration_ms": None,
            "breakdown": {},
            "status": "success"
        }
    }

    async with httpx.AsyncClient(base_url=str(request.base_url)) as client:
        # --- Call /api/search ---
        try:
            api_start = time.time()
            res_api = await client.post("http://127.0.0.1:8003/api/search", json={"Pokemon_Name": name})
            api_duration = round((time.time() - api_start) * 1000, 2)
            api_json = res_api.json()
            results["api_data"] = api_json.get("api_data", {})
            results["performance_metrics"]["breakdown"]["api_call_ms"] = api_duration
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            results["performance_metrics"]["breakdown"]["api_call_ms"] = None
            results["api_data"]["error"] = str(e)
            results["performance_metrics"]["status"] = "partial"

        # --- Call /stats/search ---
        try:
            stats_start = time.time()
            res_stats = await client.post("http://127.0.0.1:8001/stats/search", json={"Pokemon_Name": name})
            stats_duration = round((time.time() - stats_start) * 1000, 2)
            stats_json = res_stats.json()
            results["csv_data"] = stats_json.get("csv_data", {})
            results["performance_metrics"]["breakdown"]["csv_lookup_ms"] = stats_duration
        except Exception as e:
            logger.error(f"CSV stats call failed: {str(e)}")
            results["performance_metrics"]["breakdown"]["csv_lookup_ms"] = None
            results["csv_data"]["error"] = str(e)
            results["performance_metrics"]["status"] = "partial"

        # --- Call /images/search ---
        try:
            img_start = time.time()
            res_img = await client.post("http://127.0.0.1:8002/images/search", json={"Pokemon_Name": name})
            img_duration = round((time.time() - img_start) * 1000, 2)
            img_json = res_img.json()
            results["local_assets"] = img_json.get("local_assets", {})
            results["performance_metrics"]["breakdown"]["image_scan_ms"] = img_duration
        except Exception as e:
            logger.error(f"Image scan failed: {str(e)}")
            results["performance_metrics"]["breakdown"]["image_scan_ms"] = None
            results["local_assets"]["error"] = str(e)
            results["performance_metrics"]["status"] = "partial"

    total_duration = round((time.time() - start_time) * 1000, 2)
    results["performance_metrics"]["total_duration_ms"] = total_duration

    logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms")
    logger.info("-" * 30)
    logger.info(f"SEARCH SESSION COMPLETED - {name.upper()} - {total_duration}ms")
    logger.info("-" * 30)

    return results