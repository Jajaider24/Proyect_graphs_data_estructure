#!/usr/bin/env python3
"""
Test script to verify data loading works correctly.
Tests the complete pipeline without using Flet UI.
"""

import sys
import os
import asyncio
import httpx
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.config import API_CONFIG


async def test_graph_load():
    """Test loading graph via API."""
    print("=" * 60)
    print("TEST 1: Load Graph from Backend")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Load graph
            print("\n[TEST] POST /api/graph/load")
            response = await client.post(
                f"{API_CONFIG['BASE_URL']}/api/graph/load",
                params={"network_file": "../data/sample_network.json"},
                timeout=API_CONFIG["TIMEOUT"]
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {data}")
                return True
            else:
                print(f"❌ FAILED: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False


async def test_graph_data():
    """Test getting graph data after loading."""
    print("\n" + "=" * 60)
    print("TEST 2: Get Graph Data")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # First ensure graph is loaded
            print("\n[STEP 1] Loading graph...")
            load_response = await client.post(
                f"{API_CONFIG['BASE_URL']}/api/graph/load",
                params={"network_file": "../data/sample_network.json"},
                timeout=API_CONFIG["TIMEOUT"]
            )
            
            if load_response.status_code != 200:
                print(f"❌ Failed to load graph: {load_response.text}")
                return False
            
            print("✅ Graph loaded")
            
            # Then get graph data
            print("\n[STEP 2] Retrieving graph data...")
            data_response = await client.get(
                f"{API_CONFIG['BASE_URL']}/api/graph/data",
                timeout=API_CONFIG["TIMEOUT"]
            )
            
            print(f"Status: {data_response.status_code}")
            
            if data_response.status_code == 200:
                data = data_response.json()
                print(f"✅ SUCCESS:")
                print(f"   - Total airports: {data.get('total_airports', 0)}")
                print(f"   - Total routes: {data.get('total_routes', 0)}")
                if 'airports' in data:
                    print(f"   - First 3 airports: {[a.get('id') for a in data['airports'][:3]]}")
                return True
            else:
                print(f"❌ FAILED: {data_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False


async def test_network_statistics():
    """Test network statistics endpoint."""
    print("\n" + "=" * 60)
    print("TEST 3: Get Network Statistics")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # First ensure graph is loaded
            print("\n[STEP 1] Loading graph...")
            load_response = await client.post(
                f"{API_CONFIG['BASE_URL']}/api/graph/load",
                params={"network_file": "../data/sample_network.json"},
                timeout=API_CONFIG["TIMEOUT"]
            )
            
            if load_response.status_code != 200:
                print(f"❌ Failed to load graph: {load_response.text}")
                return False
            
            print("✅ Graph loaded")
            
            # Then get statistics
            print("\n[STEP 2] Retrieving network statistics...")
            stats_response = await client.get(
                f"{API_CONFIG['BASE_URL']}/api/network/statistics",
                timeout=API_CONFIG["TIMEOUT"]
            )
            
            print(f"Status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ SUCCESS:")
                print(f"   - Total airports: {stats.get('total_airports', 0)}")
                print(f"   - Total routes: {stats.get('total_routes', 0)}")
                print(f"   - Hub airports: {stats.get('hub_airports', 0)}")
                print(f"   - Avg connections: {stats.get('average_connections', 0)}")
                print(f"   - Network density: {stats.get('network_density', 0)}")
                return True
            else:
                print(f"❌ FAILED: {stats_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False


async def test_backend_health():
    """Test backend connectivity."""
    print("=" * 60)
    print("TEST 0: Backend Health Check")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"\n[TEST] GET {API_CONFIG['BASE_URL']}/")
            response = await client.get(
                f"{API_CONFIG['BASE_URL']}/",
                timeout=5
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is healthy: {data}")
                return True
            else:
                print(f"❌ Backend returned: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend is NOT running: {e}")
            print(f"\n⚠️  START BACKEND FIRST with: python api/main.py")
            return False


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SkyRoute Planner - Data Loading Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Test backend is running
    if not await test_backend_health():
        print("\n❌ Tests aborted - backend not running")
        return False
    
    # Test loading data
    if not await test_graph_load():
        print("\n❌ Tests aborted - unable to load graph")
        return False
    
    # Test getting data
    if not await test_graph_data():
        print("\n❌ Tests failed - unable to retrieve graph data")
        return False
    
    # Test network statistics
    if not await test_network_statistics():
        print("\n❌ Tests failed - unable to get network statistics")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now use the Frontend to:")
    print("  1. Click 'Cargar Red de Aeropuertos' on Dashboard")
    print("  2. See data populate across all pages")
    print("\nRun with: flet run main.py -r")
    print()
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
