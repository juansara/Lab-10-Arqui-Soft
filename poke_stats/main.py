from fastapi import FastAPI, Request
import pandas as pd
import time
from .logger import get_logger, log_request
from fastapi.responses import JSONResponse

app = FastAPI(title="Pokemon Stats Service", version="1.0.0")
logger = get_logger("poke_stats")

# Cargar CSV y limpiar
df = pd.read_csv("data/poke_stats/pokemon.csv").fillna('')
lookup = {str(row['Name']).lower(): row.to_dict() for _, row in df.iterrows()}

@app.post("/stats/search")
async def get_pokemon_stats(payload: dict, request: Request):
    name = payload.get("Pokemon_Name", "").lower()
    start = time.time()

    try:
        stats = lookup.get(name)
        duration = round((time.time() - start) * 1000, 2)

        if stats:
            log_request(
                logger=logger,
                service_name="poke_stats",
                endpoint="/stats/search",
                status_code=200,
                latency_ms=duration,
                message=f"Found stats for {name}"
            )
            return {"name": name, "stats": stats}
        else:
            log_request(
                logger=logger,
                service_name="poke_stats",
                endpoint="/stats/search",
                status_code=404,
                latency_ms=duration,
                message=f"Stats not found for {name}"
            )
            return JSONResponse(status_code=404, content={"error": f"{name} not found"})

    except Exception as e:
        duration = round((time.time() - start) * 1000, 2)
        log_request(
            logger=logger,
            service_name="poke_stats",
            endpoint="/stats/search",
            status_code=500,
            latency_ms=duration,
            message=f"Error: {str(e)}"
        )
        return JSONResponse(status_code=500, content={"error": f"Failed to get stats for {name}"})




# from fastapi import FastAPI, Request
# import pandas as pd
# import time
# import json
# import threading
# from .logger import get_logger
# from fastapi.responses import JSONResponse

# app = FastAPI(title="Pokemon Stats Service", version="1.0.0")
# logger = get_logger("poke_stats")

# # Load CSV once at startup and clean NaN values
# poke_stats_df = pd.read_csv("data/poke_stats/pokemon.csv")

# # Fill NaN values with appropriate defaults
# poke_stats_df = poke_stats_df.fillna({
#     'Type 2': '',  # Empty string for missing Type 2
#     'Name': '',
#     'Type 1': '',
#     'Total': 0,
#     'HP': 0,
#     'Attack': 0,
#     'Defense': 0,
#     'Sp. Atk': 0,
#     'Sp. Def': 0,
#     'Speed': 0,
#     'Generation': 0,
#     'Legendary': False
# })

# def safe_json_serialize(data):
#     """Convert pandas/numpy data types to JSON-safe types"""
#     if isinstance(data, dict):
#         return {k: safe_json_serialize(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [safe_json_serialize(item) for item in data]
#     elif pd.isna(data):
#         return None
#     elif hasattr(data, 'item'):  # numpy/pandas scalar
#         value = data.item()
#         return None if pd.isna(value) else value
#     else:
#         return data

# # Build a fast lookup dictionary from the DataFrame at startup
# pokemon_lookup = {}
# for _, row in poke_stats_df.iterrows():
#     name_key = str(row['Name']).lower()
#     # Convert row to dict and clean it
#     row_dict = safe_json_serialize(row.to_dict())
#     pokemon_lookup[name_key] = row_dict

# logger.info(f"Loaded {len(pokemon_lookup)} Pokemon records into memory for fast lookup")

# @app.post("/stats/search")
# async def get_pokemon_stats(payload: dict, request: Request):
#     # Session start separator
#     logger.info("=" * 30)
#     logger.info(f"NEW STATS SESSION STARTED")
#     logger.info("=" * 30)
    
#     start_time = time.time()
#     name = payload.get("Pokemon_Name", "").lower()
#     logger.info(f"{request.url.path} stats_search Started for: {name}")

#     try:
#         # Fast dictionary lookup instead of DataFrame operations
#         csv_start = time.time()
        
#         # Direct dictionary lookup - much faster and thread-safe
#         stats_csv = pokemon_lookup.get(name, {})
        
#         csv_duration = round((time.time() - csv_start) * 1000, 2)
#         csv_status = "SUCCESS" if stats_csv else "NOT_FOUND"
        
#         logger.info(f"{request.url.path} CSV_LOOKUP completed in {csv_duration}ms - Status: {csv_status}")
        
#         # Total timing
#         total_duration = round((time.time() - start_time) * 1000, 2)
#         logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | CSV: {csv_duration}ms")
        
#         # Session end separator
#         logger.info("-" * 30)
#         logger.info(f"STATS SESSION COMPLETED - {name.upper()} - {total_duration}ms")
#         logger.info("-" * 30)

#         return {
#             "pokemon_info": {
#                 "name": name,
#                 "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#             },
#             "csv_data": {
#                 "stats": stats_csv,
#                 "found": bool(stats_csv),
#                 "source": "local_dataset"
#             },
#             "performance_metrics": {
#                 "total_duration_ms": total_duration,
#                 "csv_lookup_ms": csv_duration,
#                 "status": "success"
#             }
#         }

#     except Exception as e:
#         error_duration = round((time.time() - start_time) * 1000, 2)
#         logger.error(f"{request.url.path} stats_search ERROR after {error_duration}ms: {str(e)}")
        
#         # Session end separator for errors
#         logger.info("-" * 30)
#         logger.error(f"STATS SESSION FAILED - {name.upper()} - {error_duration}ms")
#         logger.info("-" * 30)
        
#         # Return error response with 500 status code
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "pokemon_info": {
#                     "name": name,
#                     "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#                 },
#                 "error": {
#                     "message": f"Failed to fetch stats for {name}",
#                     "details": str(e),
#                     "error_type": type(e).__name__
#                 },
#                 "performance_metrics": {
#                     "total_duration_ms": error_duration,
#                     "status": "failed"
#                 }
#             }
#         ) 