#!/usr/bin/env python3
"""
Test script to demonstrate the new error handling capabilities.
This shows what JMETER will see when testing the endpoints.
"""
import requests
import json

def test_pokemon_search(pokemon_name="pikachu"):
    """Test the /poke/search endpoint and show the response structure"""
    
    url = "http://127.0.0.1:8000/poke/search"
    payload = {"Pokemon_Name": pokemon_name}
    
    print(f"🔍 Testing Pokemon Search for: {pokemon_name}")
    print(f"📡 POST {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        # Print HTTP status information
        print(f"📊 HTTP Status Code: {response.status_code}")
        print(f"📊 Status Text: {response.reason}")
        
        # Parse JSON response
        try:
            result = response.json()
            
            # Print key metrics for JMETER analysis
            print("\n🎯 JMETER TEST METRICS:")
            print(f"   Overall Status: {result.get('test_summary', {}).get('overall_status', 'unknown')}")
            print(f"   Success Rate: {result.get('test_summary', {}).get('success_rate', 'unknown')}")
            print(f"   Failed Services: {result.get('test_summary', {}).get('failed_services', [])}")
            print(f"   Total Retries: {result.get('test_summary', {}).get('total_retry_attempts', 0)}")
            print(f"   Slowest Service: {result.get('test_summary', {}).get('slowest_service', 'unknown')}")
            
            # Print performance breakdown
            breakdown = result.get('performance_metrics', {}).get('breakdown', {})
            print(f"\n⚡ PERFORMANCE BREAKDOWN:")
            print(f"   Total Duration: {result.get('performance_metrics', {}).get('total_duration_ms', 0)}ms")
            print(f"   API Call: {breakdown.get('api_call_ms', 'N/A')}ms")
            print(f"   CSV Lookup: {breakdown.get('csv_lookup_ms', 'N/A')}ms")
            print(f"   Image Scan: {breakdown.get('image_scan_ms', 'N/A')}ms")
            
            # Print failure details if any
            failures = result.get('performance_metrics', {}).get('failure_details', [])
            if failures:
                print(f"\n❌ FAILURE DETAILS:")
                for i, failure in enumerate(failures, 1):
                    print(f"   {i}. {failure.get('service', 'Unknown')}")
                    print(f"      Error Type: {failure.get('error_type', 'Unknown')}")
                    print(f"      Error Message: {failure.get('error_message', 'No message')}")
                    print(f"      Duration: {failure.get('duration_ms', 0)}ms")
                    print(f"      Retry Attempts: {failure.get('retry_attempts', 0)}")
            
            # Print success indicators
            services_successful = result.get('performance_metrics', {}).get('services_successful', 0)
            services_total = result.get('performance_metrics', {}).get('services_attempted', 3)
            
            if services_successful == services_total:
                print(f"\n✅ ALL SERVICES SUCCESSFUL ({services_successful}/{services_total})")
            elif services_successful > 0:
                print(f"\n⚠️  PARTIAL SUCCESS ({services_successful}/{services_total})")
            else:
                print(f"\n❌ COMPLETE FAILURE (0/{services_total})")
            
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response")
            print(f"Raw response: {response.text[:500]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    
    print("=" * 60)

def main():
    """Run multiple test scenarios"""
    
    print("🧪 POKEMON SEARCH ERROR HANDLING TEST")
    print("=" * 60)
    
    # Test with a valid Pokemon
    test_pokemon_search("pikachu")
    
    # Test with an invalid Pokemon (should trigger API errors)
    test_pokemon_search("invalidpokemon123")
    
    print("\n📋 JMETER CONFIGURATION NOTES:")
    print("   • Use HTTP Status Code assertions:")
    print("     - 200: Complete success")
    print("     - 207: Partial failure (some services failed)")
    print("     - 500: Complete failure (all services failed)")
    print("   • Extract metrics from JSON response:")
    print("     - test_summary.overall_status")
    print("     - test_summary.success_rate")
    print("     - test_summary.failed_services")
    print("     - test_summary.total_retry_attempts")
    print("     - performance_metrics.failure_details")

if __name__ == "__main__":
    main() 