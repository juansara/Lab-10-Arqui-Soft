# Pokemon Microservices Architecture

This project consists of 4 independent microservices for Pokemon data retrieval, each with its own logging and performance tracking.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   POKE_SEARCH   │    │   POKE_STATS    │    │  POKE_IMAGES    │    │    POKE_API     │
│     Port 8000   │    │     Port 8001   │    │     Port 8002   │    │     Port 8003   │
│                 │    │                 │    │                 │    │                 │
│ Aggregates all  │    │ CSV Dataset     │    │ Local Images    │    │ External API    │
│ other services  │    │ Lookup          │    │ Scanning        │    │ Calls           │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Microservices

### 1. **POKE_SEARCH** (Port 8000) - Main Aggregator
- **Endpoint**: `POST /poke/search`
- **Purpose**: Combines data from all sources (API + CSV + Images)
- **Log File**: `logs/poke_search.log`

### 2. **POKE_STATS** (Port 8001) - CSV Data Service
- **Endpoint**: `POST /stats/search`
- **Purpose**: Handles CSV dataset lookups only
- **Log File**: `logs/poke_stats.log`

### 3. **POKE_IMAGES** (Port 8002) - Image Service
- **Endpoint**: `POST /images/search`
- **Purpose**: Scans local image folders only
- **Log File**: `logs/poke_images.log`

### 4. **POKE_API** (Port 8003) - External API Service
- **Endpoint**: `POST /api/search`
- **Purpose**: Handles PokeAPI calls with retry logic
- **Log File**: `logs/poke_api.log`

## 🔧 Starting the Services

### Option 1: Individual Services
```bash
# Terminal 1 - Main Search Service
python start_poke_search.py

# Terminal 2 - Stats Service
python start_poke_stats.py

# Terminal 3 - Images Service
python start_poke_images.py

# Terminal 4 - API Service
python start_poke_api.py
```

### Option 2: Direct Uvicorn Commands
```bash
# Main Search (Port 8000)
uvicorn poke_search.main:app --reload --port 8000

# Stats Service (Port 8001)
uvicorn poke_stats.main:app --reload --port 8001

# Images Service (Port 8002)
uvicorn poke_images.main:app --reload --port 8002

# API Service (Port 8003)
uvicorn poke_api.main:app --reload --port 8003
```

## 🧪 Testing with Postman/JMeter

### Request Format (Same for all services):
```json
{
    "Pokemon_Name": "charizard"
}
```

### Service URLs:
- **Main Search**: `http://localhost:8000/poke/search`
- **Stats Only**: `http://localhost:8001/stats/search`
- **Images Only**: `http://localhost:8002/images/search`
- **API Only**: `http://localhost:8003/api/search`

## 📊 JMeter Testing Strategy

### Performance Testing Scenarios:

1. **Individual Component Testing**:
   - Test each service separately to identify bottlenecks
   - Compare response times: API vs CSV vs Images

2. **Load Testing**:
   - Run concurrent requests on each service
   - Monitor individual log files for performance metrics

3. **Stress Testing**:
   - Test retry mechanisms on API service
   - Test file system performance on Images service

### Log Analysis:
Each service generates separate logs with session separators:
```
==============================
NEW [SERVICE] SESSION STARTED
==============================
... performance logs ...
------------------------------
[SERVICE] SESSION COMPLETED - CHARIZARD - 150ms
------------------------------
```

## 📈 Response Formats

### POKE_SEARCH (Complete Data):
```json
{
  "pokemon_info": { "name": "charizard", "search_timestamp": "..." },
  "api_data": { "stats": [...], "sprite_image": "...", "source": "pokeapi.co" },
  "csv_data": { "stats": {...}, "found": true, "source": "local_dataset" },
  "local_assets": { "images": [...], "image_count": 3, "images_available": true },
  "performance_metrics": { "total_duration_ms": 150, "breakdown": {...}, "retry_count": 0, "status": "success" }
}
```

### POKE_STATS (CSV Only):
```json
{
  "pokemon_info": { "name": "charizard", "search_timestamp": "..." },
  "csv_data": { "stats": {...}, "found": true, "source": "local_dataset" },
  "performance_metrics": { "total_duration_ms": 25, "csv_lookup_ms": 25, "status": "success" }
}
```

### POKE_IMAGES (Images Only):
```json
{
  "pokemon_info": { "name": "charizard", "search_timestamp": "..." },
  "local_assets": { "images": [...], "image_count": 3, "images_available": true, "folder_path": "..." },
  "performance_metrics": { "total_duration_ms": 5, "image_scan_ms": 5, "status": "success" }
}
```

### POKE_API (External API Only):
```json
{
  "pokemon_info": { "name": "charizard", "search_timestamp": "..." },
  "api_data": { "stats": [...], "sprite_image": "...", "source": "pokeapi.co", "pokemon_id": 6, "height": 17, "weight": 905 },
  "performance_metrics": { "total_duration_ms": 120, "api_call_ms": 120, "retry_count": 0, "status": "success" }
}
```

## 📝 Log Files

Each service maintains its own log file:
- `logs/poke_search.log` - Main aggregator service
- `logs/poke_stats.log` - CSV lookup service
- `logs/poke_images.log` - Image scanning service
- `logs/poke_api.log` - External API service

## 🎯 Benefits for JMeter Testing

1. **Isolated Performance Testing**: Test each component separately
2. **Bottleneck Identification**: Compare individual service performance
3. **Scalability Testing**: Scale individual services based on load
4. **Failure Analysis**: Separate logs for each service
5. **Retry Monitoring**: Track API retry attempts separately 