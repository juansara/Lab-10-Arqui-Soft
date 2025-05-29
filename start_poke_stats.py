#!/usr/bin/env python3
"""
Startup script for Pokemon Stats Microservice
Port: 8001
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "poke_stats.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 