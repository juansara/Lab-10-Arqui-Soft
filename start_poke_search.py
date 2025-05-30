#!/usr/bin/env python3
"""
Startup script for Pokemon Search Microservice (Main)
Port: 8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "poke_search.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 