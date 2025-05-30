#!/usr/bin/env python3
"""
Simple test script to check if the Pokemon search endpoint works.
"""
import requests
import json

def test_pokemon_search(pokemon_name="pikachu"):
    """Test the /poke/search endpoint"""
    
    url = "http://127.0.0.1:8000/poke/search"
    payload = {"Pokemon_Name": pokemon_name}
    
    print(f"Testing Pokemon Search for: {pokemon_name}")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse:")
            print(json.dumps(result, indent=2))
            
            # Check if there are any images in the response
            if not result.get('images') or len(result.get('images', [])) == 0:
                print("\n❌ Error: No images found in response")
                print("Expected status code: 500")
            else:
                print(f"\n✅ Request successful! Found {len(result['images'])} images")
        else:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    
    print("=" * 60)

def main():
    """Run test scenarios"""
    
    print("POKEMON SEARCH TEST")
    print("=" * 60)
    
    # Test with a valid Pokemon
    test_pokemon_search("pikachu")
    
    # Test with an invalid Pokemon
    test_pokemon_search("invalidpokemon123")

if __name__ == "__main__":
    main() 