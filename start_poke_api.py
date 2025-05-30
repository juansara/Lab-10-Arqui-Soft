#!/usr/bin/env python3
"""
Startup script for Pokemon API Microservice
Port: 8003
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "poke_api.main:app",
        host="127.0.0.1",
        port=8003,
        reload=True,
        log_level="info"
    ) 