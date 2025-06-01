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
