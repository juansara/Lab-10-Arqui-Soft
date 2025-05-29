from fastapi import FastAPI, Request
import pandas as pd
import time
from .logger import get_logger

app = FastAPI(title="Pokemon Stats Service", version="1.0.0")
logger = get_logger("poke_stats")

# Load CSV once at startup
poke_stats_df = pd.read_csv("data/poke_stats/pokemon.csv")

@app.post("/stats/search")
async def get_pokemon_stats(payload: dict, request: Request):
    # Session start separator
    logger.info("=" * 30)
    logger.info(f"NEW STATS SESSION STARTED")
    logger.info("=" * 30)
    
    start_time = time.time()
    name = payload.get("Pokemon_Name", "").lower()
    logger.info(f"{request.url.path} stats_search Started for: {name}")

    try:
        # CSV lookup with timing
        csv_start = time.time()
        row = poke_stats_df[poke_stats_df['Name'].str.lower() == name]
        stats_csv = row.to_dict(orient="records")[0] if not row.empty else {}
        csv_duration = round((time.time() - csv_start) * 1000, 2)
        csv_status = "SUCCESS" if not row.empty else "NOT_FOUND"
        
        logger.info(f"{request.url.path} CSV_LOOKUP completed in {csv_duration}ms - Status: {csv_status}")
        
        # Total timing
        total_duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | CSV: {csv_duration}ms")
        
        # Session end separator
        logger.info("-" * 30)
        logger.info(f"STATS SESSION COMPLETED - {name.upper()} - {total_duration}ms")
        logger.info("-" * 30)

        return {
            "pokemon_info": {
                "name": name,
                "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "csv_data": {
                "stats": stats_csv,
                "found": bool(stats_csv),
                "source": "local_dataset"
            },
            "performance_metrics": {
                "total_duration_ms": total_duration,
                "csv_lookup_ms": csv_duration,
                "status": "success"
            }
        }

    except Exception as e:
        error_duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.url.path} stats_search ERROR after {error_duration}ms: {str(e)}")
        
        # Session end separator for errors
        logger.info("-" * 30)
        logger.error(f"STATS SESSION FAILED - {name.upper()} - {error_duration}ms")
        logger.info("-" * 30)
        
        return {
            "pokemon_info": {
                "name": name,
                "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "error": {
                "message": f"Failed to fetch stats for {name}",
                "details": str(e)
            },
            "performance_metrics": {
                "total_duration_ms": error_duration,
                "status": "failed"
            }
        } 