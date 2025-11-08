#!/usr/bin/env python3
"""
Test script for the new state query format
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/states"

def test_new_query_format():
    """Test the new query format with filter object"""
    
    print("Testing new query format...")
    
    # Test 1: Get all states with minimal view
    print("\n1. Testing: Get all states with minimal view")
    payload1 = {
        "filter": {
            "view": "minimal",
            "id": ["t_all"]
        },
        "from": 0,
        "size": 5
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/query", json=payload1)
        print(f"Status Code: {response1.status_code}")
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"Total states: {data1.get('total', 0)}")
            print(f"Returned states: {len(data1.get('states', []))}")
            print(f"Page info: {data1.get('page', 0)}/{data1.get('total_pages', 0)}")
            if data1.get('states'):
                print(f"First state: {data1['states'][0].get('name', 'N/A')}")
        else:
            print(f"Error: {response1.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 2: Get specific states by IDs (if we have any)
    print("\n2. Testing: Get specific states by IDs")
    payload2 = {
        "filter": {
            "view": "minimal",
            "id": ["68dc1021e2dc335296605a38", "68dc1021e2dc335296605a39"]  # Example IDs
        },
        "from": 0,
        "size": 10
    }
    
    try:
        response2 = requests.post(f"{BASE_URL}/query", json=payload2)
        print(f"Status Code: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"Total states: {data2.get('total', 0)}")
            print(f"Returned states: {len(data2.get('states', []))}")
        else:
            print(f"Error: {response2.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 3: Test pagination
    print("\n3. Testing: Pagination with from/size")
    payload3 = {
        "filter": {
            "view": "minimal",
            "id": ["t_all"]
        },
        "from": 2,
        "size": 3
    }
    
    try:
        response3 = requests.post(f"{BASE_URL}/query", json=payload3)
        print(f"Status Code: {response3.status_code}")
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"Total states: {data3.get('total', 0)}")
            print(f"Returned states: {len(data3.get('states', []))}")
            print(f"Page info: {data3.get('page', 0)}/{data3.get('total_pages', 0)}")
            print(f"Has next: {data3.get('has_next', False)}")
            print(f"Has prev: {data3.get('has_prev', False)}")
        else:
            print(f"Error: {response3.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 4: Test full view
    print("\n4. Testing: Full view")
    payload4 = {
        "filter": {
            "view": "full",
            "id": ["t_all"]
        },
        "from": 0,
        "size": 2
    }
    
    try:
        response4 = requests.post(f"{BASE_URL}/query", json=payload4)
        print(f"Status Code: {response4.status_code}")
        if response4.status_code == 200:
            data4 = response4.json()
            print(f"Total states: {data4.get('total', 0)}")
            print(f"Returned states: {len(data4.get('states', []))}")
            if data4.get('states'):
                first_state = data4['states'][0]
                print(f"First state keys: {list(first_state.keys())}")
        else:
            print(f"Error: {response4.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_legacy_format():
    """Test the legacy query format for backward compatibility"""
    
    print("\n" + "="*50)
    print("Testing legacy query format...")
    
    # Test legacy format
    payload_legacy = {
        "template": "minimal",
        "page": 1,
        "limit": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query/legacy", json=payload_legacy)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total states: {data.get('total', 0)}")
            print(f"Returned states: {len(data.get('states', []))}")
            print(f"Page info: {data.get('page', 0)}/{data.get('total_pages', 0)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("FastTV API - New Query Format Test")
    print("="*50)
    
    # Test new format
    test_new_query_format()
    
    # Test legacy format
    test_legacy_format()
    
    print("\n" + "="*50)
    print("Test completed!")
    print("Check the Swagger UI at: http://localhost:8000/docs")
    print("New endpoint: POST /api/v1/states/query")
    print("Legacy endpoint: POST /api/v1/states/query/legacy")
