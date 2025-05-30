from fastapi import FastAPI, Request
import os
import glob
import time
from .logger import get_logger
from fastapi.responses import JSONResponse

app = FastAPI(title="Pokemon Images Service", version="1.0.0")
logger = get_logger("poke_images")

@app.post("/images/search")
async def get_pokemon_images(payload: dict, request: Request):
    # Session start separator
    logger.info("=" * 30)
    logger.info(f"NEW IMAGES SESSION STARTED")
    logger.info("=" * 30)
    
    start_time = time.time()
    name = payload.get("Pokemon_Name", "").lower()
    logger.info(f"{request.url.path} images_search Started for: {name}")

    try:
        # Image scanning with timing
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
        
        # Total timing
        total_duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.url.path} SUMMARY - Total: {total_duration}ms | IMG: {image_duration}ms")
        
        # Session end separator
        logger.info("-" * 30)
        logger.info(f"IMAGES SESSION COMPLETED - {name.upper()} - {total_duration}ms")
        logger.info("-" * 30)

        return {
            "pokemon_info": {
                "name": name,
                "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "local_assets": {
                "images": image_list,
                "image_count": image_count,
                "images_available": image_count > 0,
                "folder_path": image_folder
            },
            "performance_metrics": {
                "total_duration_ms": total_duration,
                "image_scan_ms": image_duration,
                "status": "success"
            }
        }

    except Exception as e:
        error_duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.url.path} images_search ERROR after {error_duration}ms: {str(e)}")
        
        # Session end separator for errors
        logger.info("-" * 30)
        logger.error(f"IMAGES SESSION FAILED - {name.upper()} - {error_duration}ms")
        logger.info("-" * 30)
        
        # Return error response with 500 status code
        return JSONResponse(
            status_code=500,
            content={
                "pokemon_info": {
                    "name": name,
                    "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "error": {
                    "message": f"Failed to scan images for {name}",
                    "details": str(e),
                    "error_type": type(e).__name__
                },
                "performance_metrics": {
                    "total_duration_ms": error_duration,
                    "status": "failed"
                }
            }
        ) 