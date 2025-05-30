from fastapi import FastAPI, Request
import httpx, time
from .logger import get_logger, log_request
from fastapi.responses import JSONResponse
from contextvars import ContextVar
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

app = FastAPI(title="Pokemon API Service", version="1.0.0")
logger = get_logger("poke_api")

retry_count_var: ContextVar[int] = ContextVar('retry_count', default=0)

def before_retry_log(retry_state):
    count = retry_count_var.get() + 1
    retry_count_var.set(count)
    log_request(
        logger=logger,
        service_name="poke_api",
        endpoint="/api/search",
        status_code=0,  # Retry doesn't have a status code yet
        latency_ms=0,   # Retry doesn't have latency yet
        message=f"Retry attempt #{count}"
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.RequestError),
    before=before_retry_log
)
async def get_pokeapi_data(name: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        res.raise_for_status()
        return res.json()

@app.post("/api/search")
async def get_pokemon_api_data(payload: dict, request: Request):
    name = payload.get("Pokemon_Name", "").lower()
    start = time.time()
    retry_count_var.set(0)

    try:
        data = await get_pokeapi_data(name)
        stats = data.get("stats", [])
        image = data["sprites"]["front_default"]
        duration = round((time.time() - start) * 1000, 2)
        retries = retry_count_var.get()

        log_request(
            logger=logger,
            service_name="poke_api",
            endpoint="/api/search",
            status_code=200,
            latency_ms=duration,
            message=f"Found {len(stats)} stats for {name} (retries: {retries})"
        )

        return {
            "name": name,
            "stats": stats,
            "image": image
        }

    except Exception as e:
        duration = round((time.time() - start) * 1000, 2)
        log_request(
            logger=logger,
            service_name="poke_api",
            endpoint="/api/search",
            status_code=500,
            latency_ms=duration,
            message=f"Error: {str(e)}"
        )
        return JSONResponse(status_code=500, content={"error": f"Failed to fetch data for {name}"})






# from fastapi import FastAPI, Request
# import httpx
# import time
# from contextvars import ContextVar
# from .logger import get_logger
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# from fastapi.responses import JSONResponse

# app = FastAPI(title="Pokemon API Service", version="1.0.0")
# logger = get_logger("poke_api")

# # Request-specific retry counter using ContextVar to avoid race conditions
# retry_count_var: ContextVar[int] = ContextVar('retry_count', default=0)

# def before_retry_log(retry_state):
#     current_count = retry_count_var.get() + 1
#     retry_count_var.set(current_count)
#     logger.warning(f"API_RETRY attempt #{current_count} for Pokemon API call - Previous attempt failed")

# @retry(
#     stop=stop_after_attempt(3), 
#     wait=wait_exponential(multiplier=1, min=1, max=10),  # Exponential backoff
#     retry=retry_if_exception_type((httpx.HTTPError, httpx.RequestError)),
#     before=before_retry_log
# )
# async def get_pokeapi_data(name):
#     async with httpx.AsyncClient() as client:
#         try:
#             res = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
#             res.raise_for_status()
#             return res.json()
#         except httpx.HTTPStatusError as e:
#             if e.response.status_code == 429:  # Rate limit exceeded
#                 logger.error(f"Rate limit exceeded for Pokemon API - {e.response.headers.get('Retry-After', 'unknown')} seconds")
#                 raise Exception("Pokemon API rate limit exceeded") from e
#             raise

# @app.post("/api/search")
# async def get_pokemon_api_data(payload: dict, request: Request):
#     # Reset retry counter for this specific request context
#     retry_count_var.set(0)
    
#     # Session start separator
#     logger.info("=" * 30)
#     logger.info(f"NEW API SESSION STARTED")
#     logger.info("=" * 30)
    
#     start_time = time.time()
#     name = payload.get("Pokemon_Name", "").lower()
#     logger.info(f"{request.url.path} api_search Started for: {name}")

#     try:
#         # API call with timing
#         api_start = time.time()
#         poke_data = await get_pokeapi_data(name)
#         stats_api = poke_data.get("stats", [])
#         image_api = poke_data["sprites"]["front_default"]
#         api_duration = round((time.time() - api_start) * 1000, 2)
        
#         current_retry_count = retry_count_var.get()
#         if current_retry_count > 0:
#             logger.info(f"{request.url.path} API_CALL completed in {api_duration}ms - Status: SUCCESS (after {current_retry_count} retries)")
#         else:
#             logger.info(f"{request.url.path} API_CALL completed in {api_duration}ms - Status: SUCCESS")
        
#         # Total timing
#         total_duration = round((time.time() - start_time) * 1000, 2)
#         logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | API: {api_duration}ms | Retries: {current_retry_count}")
        
#         # Session end separator
#         logger.info("-" * 30)
#         logger.info(f"API SESSION COMPLETED - {name.upper()} - {total_duration}ms")
#         logger.info("-" * 30)

#         return {
#             "pokemon_info": {
#                 "name": name,
#                 "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#             },
#             "api_data": {
#                 "stats": stats_api,
#                 "sprite_image": image_api,
#                 "source": "pokeapi.co",
#                 "pokemon_id": poke_data.get("id"),
#                 "height": poke_data.get("height"),
#                 "weight": poke_data.get("weight")
#             },
#             "performance_metrics": {
#                 "total_duration_ms": total_duration,
#                 "api_call_ms": api_duration,
#                 "retry_count": current_retry_count,
#                 "status": "success"
#             }
#         }

#     except Exception as e:
#         error_duration = round((time.time() - start_time) * 1000, 2)
#         current_retry_count = retry_count_var.get()
#         logger.error(f"{request.url.path} api_search ERROR after {error_duration}ms: {str(e)}")
        
#         # Session end separator for errors
#         logger.info("-" * 30)
#         logger.error(f"API SESSION FAILED - {name.upper()} - {error_duration}ms")
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
#                     "message": f"Failed to fetch API data for {name}",
#                     "details": str(e),
#                     "error_type": type(e).__name__
#                 },
#                 "performance_metrics": {
#                     "total_duration_ms": error_duration,
#                     "retry_count": current_retry_count,
#                     "status": "failed"
#                 }
#             }
#         ) 