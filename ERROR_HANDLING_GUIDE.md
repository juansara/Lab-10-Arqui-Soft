# Pokemon Search API - Error Handling & JMETER Testing Guide

## 🎯 Overview

The Pokemon Search API now implements proper error handling with appropriate HTTP status codes and detailed failure tracking, making it ideal for comprehensive JMETER testing and monitoring.

## 🚨 HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| **200** | Complete Success | All 3 services (API, Stats, Images) succeeded |
| **207** | Partial Failure | Some services succeeded, some failed |
| **500** | Complete Failure | All services failed |

## 📊 Response Structure

### Success Response (200)
```json
{
  "pokemon_info": {
    "name": "pikachu",
    "search_timestamp": "2025-05-29 21:30:00"
  },
  "api_data": { /* Pokemon API data */ },
  "csv_data": { /* CSV stats data */ },
  "local_assets": { /* Image files */ },
  "performance_metrics": {
    "total_duration_ms": 1250,
    "breakdown": {
      "api_call_ms": 800,
      "csv_lookup_ms": 5,
      "image_scan_ms": 2
    },
    "status": "success",
    "services_attempted": 3,
    "services_successful": 3,
    "services_failed": 0,
    "failure_details": []
  },
  "test_summary": {
    "overall_status": "success",
    "success_rate": "3/3",
    "failed_services": [],
    "total_retry_attempts": 2,
    "slowest_service": "API"
  }
}
```

### Partial Failure Response (207)
```json
{
  // ... pokemon_info, partial data ...
  "performance_metrics": {
    "total_duration_ms": 15000,
    "breakdown": {
      "api_call_ms": null,  // Failed
      "csv_lookup_ms": 5,   // Succeeded
      "image_scan_ms": 2    // Succeeded
    },
    "status": "partial_failure",
    "services_attempted": 3,
    "services_successful": 2,
    "services_failed": 1,
    "failure_details": [
      {
        "service": "Pokemon API Service",
        "endpoint": "/api/search",
        "error_type": "ConnectTimeout",
        "error_message": "Connection timeout after 3 retries",
        "duration_ms": 15000,
        "retry_attempts": 3
      }
    ]
  },
  "test_summary": {
    "overall_status": "partial_failure",
    "success_rate": "2/3",
    "failed_services": ["Pokemon API Service"],
    "total_retry_attempts": 3,
    "slowest_service": "API"
  }
}
```

### Complete Failure Response (500)
```json
{
  // ... pokemon_info ...
  "api_data": {"error": "Connection failed"},
  "csv_data": {"error": "Database unavailable"},
  "local_assets": {"error": "File system error"},
  "performance_metrics": {
    "status": "complete_failure",
    "services_attempted": 3,
    "services_successful": 0,
    "services_failed": 3,
    "failure_details": [
      // ... detailed error information for each failed service
    ]
  },
  "test_summary": {
    "overall_status": "complete_failure",
    "success_rate": "0/3",
    "failed_services": ["Pokemon API Service", "Pokemon Stats Service", "Pokemon Images Service"],
    "total_retry_attempts": 15
  }
}
```

## 🧪 JMETER Testing Configuration

### 1. HTTP Request Sampler
```
Method: POST
URL: http://127.0.0.1:8000/poke/search
Body: {"Pokemon_Name": "pikachu"}
Content-Type: application/json
```

### 2. Response Assertions

#### HTTP Status Code Assertion
```
Response Code: 200|207|500
```

#### JSON Path Assertions
```
$.test_summary.overall_status exists
$.performance_metrics.services_attempted equals 3
$.performance_metrics.total_duration_ms exists
```

### 3. Data Extraction (Post-Processors)

#### JSON Extractor - Extract Key Metrics
```bash
# Overall status
$.test_summary.overall_status → overall_status

# Success rate
$.test_summary.success_rate → success_rate

# Failed services count
$.performance_metrics.services_failed → failed_count

# Total retry attempts
$.test_summary.total_retry_attempts → total_retries

# Performance metrics
$.performance_metrics.total_duration_ms → total_duration
$.performance_metrics.breakdown.api_call_ms → api_duration
$.performance_metrics.breakdown.csv_lookup_ms → csv_duration
$.performance_metrics.breakdown.image_scan_ms → image_duration

# Slowest service
$.test_summary.slowest_service → slowest_service
```

### 4. Response Time Analysis

#### Performance Thresholds
```bash
# Define acceptable response times
Total Duration: < 5000ms (success), < 30000ms (partial), any (failure)
API Call: < 3000ms (with retries)
CSV Lookup: < 100ms
Image Scan: < 50ms
```

### 5. Error Analysis

#### BeanShell Post-Processor Example
```java
import org.json.JSONObject;
import org.json.JSONArray;

// Parse response
String response = prev.getResponseDataAsString();
JSONObject json = new JSONObject(response);

// Extract failure details
if (json.has("performance_metrics")) {
    JSONObject metrics = json.getJSONObject("performance_metrics");
    
    if (metrics.has("failure_details")) {
        JSONArray failures = metrics.getJSONArray("failure_details");
        
        for (int i = 0; i < failures.length(); i++) {
            JSONObject failure = failures.getJSONObject(i);
            
            // Extract error information
            String service = failure.getString("service");
            String errorType = failure.getString("error_type");
            String errorMessage = failure.getString("error_message");
            int retryAttempts = failure.getInt("retry_attempts");
            int duration = failure.getInt("duration_ms");
            
            // Set JMeter variables for reporting
            vars.put("error_" + i + "_service", service);
            vars.put("error_" + i + "_type", errorType);
            vars.put("error_" + i + "_retries", String.valueOf(retryAttempts));
            vars.put("error_" + i + "_duration", String.valueOf(duration));
        }
        
        vars.put("total_errors", String.valueOf(failures.length()));
    }
}
```

## 📈 Monitoring & Alerting

### Key Metrics to Monitor

1. **Success Rate**: `services_successful / services_attempted`
2. **HTTP Status Distribution**: Count of 200, 207, 500 responses
3. **Retry Frequency**: `total_retry_attempts` per request
4. **Service Reliability**: Individual service success rates
5. **Performance Degradation**: Response time trends
6. **Error Patterns**: Most common error types and services

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

# Performance Alerts
- Total response time > 5 seconds average
- API call time > 3 seconds average
- Services failed > 1 per request average
```

## 🔍 Troubleshooting

### Common Issues

1. **High Retry Counts**
   - Check: `test_summary.total_retry_attempts`
   - Cause: Pokemon API rate limiting or network issues
   - Solution: Implement exponential backoff, reduce concurrent requests

2. **Partial Failures (207)**
   - Check: `test_summary.failed_services`
   - Cause: Individual service unavailability
   - Solution: Check service health, database connections

3. **Complete Failures (500)**
   - Check: `performance_metrics.failure_details`
   - Cause: System-wide issues, network problems
   - Solution: Check infrastructure, service dependencies

### Log Correlation

Each request generates detailed logs with session tracking:
```
NEW SEARCH SESSION STARTED
/poke/search search_pokemon Started for: pikachu
Pokemon API Service - SUCCESS in 850ms (retries: 2)
Pokemon Stats Service - SUCCESS in 5ms (retries: 0)  
Pokemon Images Service - SUCCESS in 2ms (retries: 0)
SEARCH SESSION COMPLETED - PIKACHU - 857ms
```

## 🚀 Load Testing Recommendations

### Test Scenarios

1. **Baseline Test**: 1-10 concurrent users, valid Pokemon names
2. **Stress Test**: 100-1000 concurrent users, mixed valid/invalid names
3. **Endurance Test**: Sustained load for 30+ minutes
4. **Spike Test**: Sudden traffic bursts
5. **Failure Test**: Test with external services down

### Metrics Collection

- Track all HTTP status codes (200, 207, 500)
- Monitor retry patterns and frequencies
- Measure service-specific performance
- Collect error distribution by service and type
- Monitor system resources during tests

This comprehensive error handling system provides full visibility into system behavior, making it perfect for production monitoring and load testing with JMETER! 