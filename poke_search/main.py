from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx, time
from .logger import get_logger

app = FastAPI()
logger = get_logger("poke_search")

@app.post("/poke/search")
async def search_pokemon(payload: dict, request: Request):
    name = payload.get("Pokemon_Name", "").lower()
    logger.info(f"Start - name={name}", extra={"service": "poke_search", "path": "/poke/search"})

    results = {"name": name}
    success = 0
    total = 3

    async with httpx.AsyncClient() as client:
        # --- /api/search ---
        try:
            res_api = await client.post("http://127.0.0.1:8003/api/search", json={"Pokemon_Name": name})
            res_api.raise_for_status()
            results["api_data"] = res_api.json()
            logger.info("api/search - success", extra={"service": "poke_search", "path": "/poke/search"})
            success += 1
        except Exception as e:
            results["api_data"] = {"error": str(e)}
            logger.error(f"api/search - error - {type(e).__name__}: {str(e)}", extra={"service": "poke_search", "path": "/poke/search"})

        # --- /stats/search ---
        try:
            res_stats = await client.post("http://127.0.0.1:8001/stats/search", json={"Pokemon_Name": name})
            res_stats.raise_for_status()
            results["stats_data"] = res_stats.json()
            logger.info("stats/search - success", extra={"service": "poke_search", "path": "/poke/search"})
            success += 1
        except Exception as e:
            results["stats_data"] = {"error": str(e)}
            logger.error(f"stats/search - error - {type(e).__name__}: {str(e)}", extra={"service": "poke_search", "path": "/poke/search"})

        # --- /images/search ---
        try:
            res_img = await client.post("http://127.0.0.1:8002/images/search", json={"Pokemon_Name": name})
            res_img.raise_for_status()
            results["images"] = res_img.json()
            logger.info("images/search - success", extra={"service": "poke_search", "path": "/poke/search"})
            success += 1
        except Exception as e:
            results["images"] = {"error": str(e)}
            logger.error(f"images/search - error - {type(e).__name__}: {str(e)}", extra={"service": "poke_search", "path": "/poke/search"})

    # --- Final status ---
    if success == total:
        logger.info("Status - success", extra={"service": "poke_search", "path": "/poke/search"})
        return results
    elif success > 0:
        logger.info("Status - partial", extra={"service": "poke_search", "path": "/poke/search"})
        return JSONResponse(content=results, status_code=207)
    else:
        logger.info("Status - failure", extra={"service": "poke_search", "path": "/poke/search"})
        return JSONResponse(content=results, status_code=500)








# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import JSONResponse
# import httpx, time
# import pandas as pd
# import os
# import glob
# from .logger import get_logger
# from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# app = FastAPI()
# logger = get_logger("poke_search")

# @app.post("/poke/search")
# async def search_pokemon(payload: dict, request: Request):
#     logger.info("=" * 30)
#     logger.info("NEW SEARCH SESSION STARTED")
#     logger.info("=" * 30)

#     start_time = time.time()
#     name = payload.get("Pokemon_Name", "").lower()
#     logger.info(f"{request.url.path} search_pokemon Started for: {name}")

#     # Track failures for detailed error reporting
#     failures = []
#     success_count = 0
#     total_services = 3

#     results = {
#         "pokemon_info": {
#             "name": name,
#             "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#         },
#         "api_data": {},
#         "csv_data": {},
#         "local_assets": {},
#         "performance_metrics": {
#             "total_duration_ms": None,
#             "breakdown": {},
#             "status": "success",
#             "services_attempted": total_services,
#             "services_successful": 0,
#             "services_failed": 0,
#             "failure_details": []
#         }
#     }

#     async with httpx.AsyncClient(base_url=str(request.base_url)) as client:
#         # --- Call /api/search ---
#         service_name = "Pokemon API Service"
#         try:
#             api_start = time.time()
#             res_api = await client.post("http://127.0.0.1:8003/api/search", json={"Pokemon_Name": name})
#             res_api.raise_for_status()  # Raise exception for HTTP errors
#             api_duration = round((time.time() - api_start) * 1000, 2)
#             api_json = res_api.json()
            
#             # Check if the API service itself reported an error
#             if api_json.get("error") or api_json.get("performance_metrics", {}).get("status") == "failed":
#                 retry_count = api_json.get("performance_metrics", {}).get("retry_count", 0)
#                 raise Exception(f"API service reported failure: {api_json.get('error', {}).get('details', 'Unknown API error')} (after {retry_count} retries)")
            
#             results["api_data"] = api_json.get("api_data", {})
#             results["performance_metrics"]["breakdown"]["api_call_ms"] = api_duration
#             success_count += 1
#             retry_count = api_json.get("performance_metrics", {}).get("retry_count", 0)
#             logger.info(f"{service_name} - SUCCESS in {api_duration}ms (retries: {retry_count})")
            
#         except Exception as e:
#             api_duration = round((time.time() - api_start) * 1000, 2) if 'api_start' in locals() else 0
#             # Try to extract retry count from error response if available
#             retry_count = 0
#             try:
#                 if hasattr(e, 'response') and e.response:
#                     error_json = e.response.json()
#                     retry_count = error_json.get("performance_metrics", {}).get("retry_count", 0)
#             except:
#                 pass
            
#             error_detail = {
#                 "service": service_name,
#                 "endpoint": "/api/search",
#                 "error_type": type(e).__name__,
#                 "error_message": str(e),
#                 "duration_ms": api_duration,
#                 "retry_attempts": retry_count
#             }
#             failures.append(error_detail)
#             logger.error(f"{service_name} FAILED: {str(e)} (retries: {retry_count})")
#             results["performance_metrics"]["breakdown"]["api_call_ms"] = api_duration
#             results["api_data"] = {"error": str(e)}

#         # --- Call /stats/search ---
#         service_name = "Pokemon Stats Service"
#         try:
#             stats_start = time.time()
#             res_stats = await client.post("http://127.0.0.1:8001/stats/search", json={"Pokemon_Name": name})
#             res_stats.raise_for_status()  # Raise exception for HTTP errors
#             stats_duration = round((time.time() - stats_start) * 1000, 2)
#             stats_json = res_stats.json()
            
#             # Check if the stats service itself reported an error
#             if stats_json.get("error") or stats_json.get("performance_metrics", {}).get("status") == "failed":
#                 raise Exception(f"Stats service reported failure: {stats_json.get('error', {}).get('details', 'Unknown stats error')}")
            
#             results["csv_data"] = stats_json.get("csv_data", {})
#             results["performance_metrics"]["breakdown"]["csv_lookup_ms"] = stats_duration
#             success_count += 1
#             logger.info(f"{service_name} - SUCCESS in {stats_duration}ms")
            
#         except Exception as e:
#             stats_duration = round((time.time() - stats_start) * 1000, 2) if 'stats_start' in locals() else 0
#             error_detail = {
#                 "service": service_name,
#                 "endpoint": "/stats/search",
#                 "error_type": type(e).__name__,
#                 "error_message": str(e),
#                 "duration_ms": stats_duration,
#                 "retry_attempts": 0  # Stats service doesn't have retries
#             }
#             failures.append(error_detail)
#             logger.error(f"{service_name} FAILED: {str(e)}")
#             results["performance_metrics"]["breakdown"]["csv_lookup_ms"] = stats_duration
#             results["csv_data"] = {"error": str(e)}

#         # --- Call /images/search ---
#         service_name = "Pokemon Images Service"
#         try:
#             img_start = time.time()
#             res_img = await client.post("http://127.0.0.1:8002/images/search", json={"Pokemon_Name": name})
#             res_img.raise_for_status()  # Raise exception for HTTP errors
#             img_duration = round((time.time() - img_start) * 1000, 2)
#             img_json = res_img.json()
            
#             # Check if the image service itself reported an error
#             if img_json.get("error") or img_json.get("performance_metrics", {}).get("status") == "failed":
#                 raise Exception(f"Images service reported failure: {img_json.get('error', {}).get('details', 'Unknown images error')}")
            
#             results["local_assets"] = img_json.get("local_assets", {})
#             results["performance_metrics"]["breakdown"]["image_scan_ms"] = img_duration
#             success_count += 1
#             logger.info(f"{service_name} - SUCCESS in {img_duration}ms")
            
#         except Exception as e:
#             img_duration = round((time.time() - img_start) * 1000, 2) if 'img_start' in locals() else 0
#             error_detail = {
#                 "service": service_name,
#                 "endpoint": "/images/search",
#                 "error_type": type(e).__name__,
#                 "error_message": str(e),
#                 "duration_ms": img_duration,
#                 "retry_attempts": 0  # Images service doesn't have retries
#             }
#             failures.append(error_detail)
#             logger.error(f"{service_name} FAILED: {str(e)}")
#             results["performance_metrics"]["breakdown"]["image_scan_ms"] = img_duration
#             results["local_assets"] = {"error": str(e)}

#     # Calculate final metrics
#     total_duration = round((time.time() - start_time) * 1000, 2)
#     results["performance_metrics"]["total_duration_ms"] = total_duration
#     results["performance_metrics"]["services_successful"] = success_count
#     results["performance_metrics"]["services_failed"] = len(failures)
#     results["performance_metrics"]["failure_details"] = failures

#     # Determine response status and HTTP code
#     if len(failures) == 0:
#         # All services succeeded
#         results["performance_metrics"]["status"] = "success"
#         status_code = 200
#         logger.info(f"ALL SERVICES SUCCESSFUL - {name.upper()} - {total_duration}ms")
#     elif any(f["service"] == "Pokemon API Service" for f in failures):
#         # If Pokemon API failed, return 500
#         results["performance_metrics"]["status"] = "complete_failure"
#         status_code = 500
#         logger.error(f"POKEMON API FAILURE - {name.upper()} - {total_duration}ms")
#     elif success_count > 0:
#         # Partial failure - some services succeeded, some failed
#         results["performance_metrics"]["status"] = "partial_failure"
#         status_code = 207  # Multi-Status (some succeeded, some failed)
#         failure_summary = ", ".join([f["service"] for f in failures])
#         logger.error(f"PARTIAL FAILURE - {name.upper()} - Failed: {failure_summary} - {total_duration}ms")
#     else:
#         # Complete failure - all services failed
#         results["performance_metrics"]["status"] = "complete_failure"
#         status_code = 500  # Internal Server Error
#         logger.error(f"COMPLETE FAILURE - {name.upper()} - All services failed - {total_duration}ms")

#     # Add summary for JMETER
#     results["test_summary"] = {
#         "overall_status": results["performance_metrics"]["status"],
#         "success_rate": f"{success_count}/{total_services}",
#         "failed_services": [f["service"] for f in failures] if failures else [],
#         "total_retry_attempts": sum(f["retry_attempts"] for f in failures),
#         "slowest_service": max(
#             [
#                 ("API", results["performance_metrics"]["breakdown"].get("api_call_ms", 0)),
#                 ("Stats", results["performance_metrics"]["breakdown"].get("csv_lookup_ms", 0)),
#                 ("Images", results["performance_metrics"]["breakdown"].get("image_scan_ms", 0))
#             ],
#             key=lambda x: x[1] if x[1] is not None else 0
#         )[0] if any(v is not None for v in results["performance_metrics"]["breakdown"].values()) else "None"
#     }

#     logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms - Status: {results['performance_metrics']['status']}")
#     logger.info("-" * 30)
#     logger.info(f"SEARCH SESSION COMPLETED - {name.upper()} - {total_duration}ms")
#     logger.info("-" * 30)

#     # Return with appropriate HTTP status code
#     return JSONResponse(content=results, status_code=status_code)