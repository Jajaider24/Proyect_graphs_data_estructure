"""
Test script for SkyRoute Planner API endpoints.

Run this script to test all API endpoints after starting the backend.
Usage: python test_api.py
"""

import httpx
import asyncio
import json
from pprint import pprint


BASE_URL = "http://localhost:8000"


async def test_endpoints():
    """Test all API endpoints."""
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        
        print("\n" + "="*60)
        print("  SkyRoute Planner - API Test Suite")
        print("="*60 + "\n")
        
        # Test 1: Health check
        print("1. Health Check")
        print("-" * 60)
        try:
            response = await client.get("/health")
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: Load graph
        print("\n2. Load Graph")
        print("-" * 60)
        try:
            response = await client.post("/api/graph/load", json={"network_file": "../data/sample_network.json"})
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: Get graph status
        print("\n3. Graph Status")
        print("-" * 60)
        try:
            response = await client.get("/api/graph/status")
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: Get airports
        print("\n4. Get Airports")
        print("-" * 60)
        try:
            response = await client.get("/api/graph/airports")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total airports: {len(data)}")
            if data:
                print("Sample airport:")
                pprint(data[0])
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 5: Get routes
        print("\n5. Get Routes")
        print("-" * 60)
        try:
            response = await client.get("/api/graph/routes")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total routes: {len(data)}")
            if data:
                print("Sample route:")
                pprint(data[0])
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 6: Get network statistics
        print("\n6. Network Statistics")
        print("-" * 60)
        try:
            response = await client.get("/api/network/statistics")
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 7: Get hub airports
        print("\n7. Hub Airports")
        print("-" * 60)
        try:
            response = await client.get("/api/network/hubs")
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 8: Get graph data
        print("\n8. Complete Graph Data")
        print("-" * 60)
        try:
            response = await client.get("/api/graph/data")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Total airports: {data['total_airports']}")
            print(f"Total routes: {data['total_routes']}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 9: Calculate shortest path
        print("\n9. Shortest Path (Distance)")
        print("-" * 60)
        try:
            response = await client.post(
                "/api/planning/shortest-path",
                json={
                    "start": "MDE",
                    "end": "BOG",
                    "criterion": "distance"
                }
            )
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 10: Compare routes
        print("\n10. Compare Routes")
        print("-" * 60)
        try:
            response = await client.post(
                "/api/planning/compare-routes",
                json={"start": "MDE", "end": "BOG"}
            )
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 11: Generate itinerary
        print("\n11. Generate Itinerary")
        print("-" * 60)
        try:
            response = await client.post(
                "/api/planning/itinerary",
                json={
                    "origin": "MDE",
                    "budget": 5000,
                    "available_time": 480,  # 8 hours
                    "aircraft_type": "Commercial"
                }
            )
            print(f"Status: {response.status_code}")
            pprint(response.json())
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60)
        print("  All tests completed!")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    print("\nStarting API tests...")
    print("Make sure the backend is running on http://localhost:8000")
    input("Press Enter to continue...")
    
    try:
        asyncio.run(test_endpoints())
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the backend is running!")


if __name__ == "__main__":
    main()
