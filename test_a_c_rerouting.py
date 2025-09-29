#!/usr/bin/env python3
"""
Test A-C Route Blockage and A→B→C Rerouting
"""

import requests
import json

BASE_URL = "https://smart-railway-1.preview.emergentagent.com/api"

def test_a_c_rerouting():
    print("🧪 Testing A-C Route Blockage and Rerouting")
    print("=" * 50)
    
    # Step 1: Reset system to clean state
    print("\n1️⃣ Resetting system to clean state...")
    reset_response = requests.post(f"{BASE_URL}/debug/reset")
    print(f"   Reset status: {reset_response.status_code}")
    
    # Step 2: Check initial state
    print("\n2️⃣ Checking initial state...")
    routes_response = requests.get(f"{BASE_URL}/debug/routes")
    routes_data = routes_response.json()
    print(f"   Total routes: {routes_data['total_routes']}")
    print(f"   Blocked routes: {routes_data['blocked_routes']}")
    
    trains_response = requests.get(f"{BASE_URL}/debug/trains")
    trains_data = trains_response.json()
    a_c_trains = [t for t in trains_data['trains'] if t['route'] == 'A-C']
    print(f"   A-C route trains: {[t['id'] for t in a_c_trains]}")
    
    # Step 3: Create A-C flood disaster
    print("\n3️⃣ Creating A-C route flood disaster...")
    disaster_data = {
        "type": "flood",
        "affected_route": "A-C",
        "description": "Heavy flooding blocks A-C direct route - should reroute via A→B→C",
        "severity": "critical"
    }
    
    disaster_response = requests.post(f"{BASE_URL}/disaster/custom", json=disaster_data)
    print(f"   Disaster creation status: {disaster_response.status_code}")
    
    if disaster_response.status_code == 200:
        disaster_result = disaster_response.json()
        print(f"   Disaster created successfully")
        
        # Check rerouted trains
        if 'rerouted_trains' in disaster_result:
            print(f"\n   🚄 Rerouted trains:")
            for train in disaster_result['rerouted_trains']:
                print(f"      {train['id']}: {train['original_route']} → {train['new_route']}")
                print(f"         Path: {' → '.join(train.get('alternate_path_stations', []))}")
                print(f"         Delay: +{train['additional_delay']} min")
        
        # Check optimized trains
        if 'optimized_trains' in disaster_result:
            a_c_optimized = [t for t in disaster_result['optimized_trains'] if t['route'] == 'A-C' or t.get('rerouted')]
            print(f"\n   📊 A-C affected trains status:")
            for train in a_c_optimized:
                print(f"      {train['id']}: rerouted={train.get('rerouted', False)}")
                if train.get('rerouted'):
                    print(f"         New route: {train.get('new_route', 'N/A')}")
                    print(f"         Alternate segments: {train.get('alternate_route_segments', [])}")
    
    # Step 4: Verify final state
    print("\n4️⃣ Verifying final state...")
    routes_response = requests.get(f"{BASE_URL}/debug/routes")
    routes_data = routes_response.json()
    blocked_routes = routes_data['blocked_routes']
    print(f"   Blocked routes: {blocked_routes}")
    
    if 'A-C' in blocked_routes:
        print("   ✅ A-C route correctly blocked")
    else:
        print("   ❌ A-C route not blocked as expected")
    
    print("\n🎯 Expected Behavior:")
    print("   - A-C route should be blocked (thick black line on map)")
    print("   - TRN011 and TRN012 should be rerouted A→B→C")
    print("   - A-B and B-C segments should be highlighted in yellow")
    print("   - Trains should show 'REROUTED: A → B → C' on map")

if __name__ == "__main__":
    test_a_c_rerouting()