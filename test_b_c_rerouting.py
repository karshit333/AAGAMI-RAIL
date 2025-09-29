#!/usr/bin/env python3
"""
Test B-C Route Blockage and B→A→C Rerouting
"""

import requests
import json

BASE_URL = "https://smart-railway-1.preview.emergentagent.com/api"

def test_b_c_rerouting():
    print("🧪 Testing B-C Route Blockage and Rerouting")
    print("=" * 50)
    
    # Step 1: Reset system to clean state
    print("\n1️⃣ Resetting system to clean state...")
    reset_response = requests.post(f"{BASE_URL}/debug/reset")
    print(f"   Reset status: {reset_response.status_code}")
    
    # Step 2: Check initial B-C trains
    print("\n2️⃣ Checking B-C route trains...")
    trains_response = requests.get(f"{BASE_URL}/debug/trains")
    trains_data = trains_response.json()
    b_c_trains = [t for t in trains_data['trains'] if t['route'] == 'B-C']
    print(f"   B-C route trains: {[t['id'] for t in b_c_trains]}")
    
    # Step 3: Create B-C flood disaster
    print("\n3️⃣ Creating B-C route flood disaster...")
    disaster_data = {
        "type": "flood",
        "affected_route": "B-C",
        "description": "Heavy flooding blocks B-C route - should reroute TRN003 and TRN004 via B→A→C",
        "severity": "critical"
    }
    
    disaster_response = requests.post(f"{BASE_URL}/disaster/custom", json=disaster_data)
    print(f"   Disaster creation status: {disaster_response.status_code}")
    
    if disaster_response.status_code == 200:
        disaster_result = disaster_response.json()
        print(f"   Disaster applied successfully")
        
        # Check rerouted trains
        if 'rerouted_trains' in disaster_result:
            print(f"\n   🚄 Rerouted trains:")
            for train in disaster_result['rerouted_trains']:
                print(f"      {train['id']}: {train['original_route']} → {train['new_route']}")
                print(f"         Path: {' → '.join(train.get('alternate_path_stations', []))}")
        
        # Check if TRN003 and TRN004 are rerouted
        optimized_trains = disaster_result.get('optimized_trains', [])
        trn003 = next((t for t in optimized_trains if t['id'] == 'TRN003'), None)
        trn004 = next((t for t in optimized_trains if t['id'] == 'TRN004'), None)
        
        print(f"\n   📊 B-C trains status:")
        if trn003:
            print(f"      TRN003: rerouted={trn003.get('rerouted', False)}")
            if trn003.get('rerouted'):
                print(f"         New route: {trn003.get('new_route', 'N/A')}")
                print(f"         Path: {' → '.join(trn003.get('alternate_path_stations', []))}")
        
        if trn004:
            print(f"      TRN004: rerouted={trn004.get('rerouted', False)}")
            if trn004.get('rerouted'):
                print(f"         New route: {trn004.get('new_route', 'N/A')}")
                print(f"         Path: {' → '.join(trn004.get('alternate_path_stations', []))}")
    
    # Step 4: Verify blocked routes
    print("\n4️⃣ Verifying blocked routes...")
    routes_response = requests.get(f"{BASE_URL}/debug/routes")
    routes_data = routes_response.json()
    blocked_routes = routes_data['blocked_routes']
    print(f"   Blocked routes: {blocked_routes}")
    
    print("\n🎯 Expected Behavior:")
    print("   - B-C route should be blocked (thick black line)")
    print("   - TRN003 should be rerouted B→A→C")
    print("   - TRN004 should be rerouted B→A→C")
    print("   - B-A and A-C segments should be highlighted in yellow")

if __name__ == "__main__":
    test_b_c_rerouting()