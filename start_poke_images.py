#!/usr/bin/env python3
"""
Startup script for Pokemon Images Microservice
Port: 8002
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "poke_images.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 