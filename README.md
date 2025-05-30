# Pokemon Search API

A distributed microservices architecture for Pokemon data retrieval and analysis.

## 🚀 Quick Start

1. Start the main service:
```bash
uvicorn poke_search.main:app --reload
```

2. Test the API:
```bash
curl -X POST http://localhost:8000/poke/search \
-H "Content-Type: application/json" \
-d '{"Pokemon_Name": "charizard"}'
```

## 🏗️ Architecture

The system consists of 4 microservices:

1. **Main Search Service** (`poke_search/`)
   - Entry point for all Pokemon searches
   - Orchestrates calls to other services
   - Port: 8000

2. **Pokemon API Service** (`poke_api/`)
   - Fetches data from pokeapi.co
   - Implements retry logic with exponential backoff
   - Port: 8003

3. **Stats Service** (`poke_stats/`)
   - Provides Pokemon statistics from local CSV
   - Fast in-memory lookup
   - Port: 8001

4. **Images Service** (`poke_images/`)
   - Manages local Pokemon images
   - Port: 8002

## 🤖 Bot Integration

The system includes two bot implementations:

1. **Discord Bot** (`bot/discord_bot.py`)
   - Commands:
     - `/pokemon <name>`: Search Pokemon info
     - `/stats <name>`: Get Pokemon stats
     - `/image <name>`: Get Pokemon images
   - Features:
     - Rich embeds with Pokemon data
     - Error handling with user-friendly messages
     - Rate limiting protection

2. **Telegram Bot** (`bot/telegram_bot.py`)
   - Commands:
     - `/start`: Welcome message
     - `/pokemon <name>`: Search Pokemon info
     - `/stats <name>`: Get Pokemon stats
     - `/image <name>`: Get Pokemon images
   - Features:
     - Interactive buttons for navigation
     - Error handling with retry options
     - Rate limiting protection

### Bot Setup

1. **Discord Bot**:
   ```bash
   # Set environment variables
   export DISCORD_TOKEN=your_token_here
   export API_BASE_URL=http://localhost:8000
   
   # Run the bot
   python bot/discord_bot.py
   ```

2. **Telegram Bot**:
   ```bash
   # Set environment variables
   export TELEGRAM_TOKEN=your_token_here
   export API_BASE_URL=http://localhost:8000
   
   # Run the bot
   python bot/telegram_bot.py
   ```

## 🎯 Error Handling

The API implements comprehensive error handling with appropriate HTTP status codes:

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| **200** | Complete Success | All services succeeded |
| **207** | Partial Failure | Some services succeeded, some failed |
| **500** | Complete Failure | All services failed or Pokemon API failed |

### Response Structure

```json
{
  "name": "pokemon_name",
  "api_data": { /* Pokemon API data */ },
  "stats_data": { /* CSV stats data */ },
  "images": { /* Image files */ }
}
```

## 🧪 JMETER Testing

### Key Metrics to Monitor

1. **Success Rate**: Services successful / services attempted
2. **HTTP Status Distribution**: Count of 200, 207, 500 responses
3. **Retry Frequency**: Total retry attempts per request
4. **Service Reliability**: Individual service success rates
5. **Performance**: Response time trends

### Performance Thresholds

```bash
# Define acceptable response times
Total Duration: < 5000ms (success), < 30000ms (partial), any (failure)
API Call: < 3000ms (with retries)
CSV Lookup: < 100ms
Image Scan: < 50ms
```

### Alert Conditions

```bash
# Critical Alerts
- HTTP 500 rate > 10%
- Total retry attempts > 5 per request average
- Response time > 30 seconds

# Warning Alerts  
- HTTP 207 rate > 25%
- API service retry rate > 2 per request
- CSV lookup time > 100ms average
```

## 🔧 Troubleshooting

### Common Issues

1. **High Retry Counts**
   - Check: Pokemon API rate limiting
   - Solution: Implement exponential backoff, reduce concurrent requests

2. **Partial Failures (207)**
   - Check: Individual service health
   - Solution: Check service logs, database connections

3. **Complete Failures (500)**
   - Check: System-wide issues
   - Solution: Check infrastructure, service dependencies

## 📈 Monitoring

Each service generates detailed logs with:
- Request/response timing
- Error details
- Retry attempts
- Service status

Log format:
```
[timestamp] [service] [level] message - extra={"module": "service_name", "endpoint": "/endpoint"}
```

## 🚀 Load Testing Recommendations

1. **Baseline Test**: 1-10 concurrent users
2. **Stress Test**: 100-1000 concurrent users
3. **Endurance Test**: 30+ minutes sustained load
4. **Spike Test**: Sudden traffic bursts
5. **Failure Test**: Test with external services down
