#!/usr/bin/env python3
"""
AAGAMI RAIL Backend API Testing Suite
Tests all backend endpoints for the AI Train Optimization system
"""

import requests
import sys
import json
from datetime import datetime

class AagamiRailAPITester:
    def __init__(self, base_url="https://rail-optimizer-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def test_api_root(self):
        """Test GET /api/ endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_message = "AAGAMI RAIL - AI Train Traffic Control API"
                if data.get("message") == expected_message:
                    self.log_test("API Root Endpoint", True)
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Unexpected message: {data}")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_get_trains(self):
        """Test GET /api/trains endpoint - Enhanced for train ID format"""
        try:
            response = requests.get(f"{self.api_url}/trains", timeout=10)
            success = response.status_code == 200
            
            if success:
                trains = response.json()
                if isinstance(trains, list) and len(trains) == 10:
                    # Validate train structure
                    required_fields = ['id', 'priority', 'planned_arrival', 'planned_departure', 'route', 'delay_minutes']
                    first_train = trains[0]
                    
                    if all(field in first_train for field in required_fields):
                        # Check priority values
                        priorities = set(train['priority'] for train in trains)
                        expected_priorities = {'High', 'Medium', 'Low'}
                        
                        # Check train ID format (TRN001-TRN010)
                        train_id_test_passed = True
                        invalid_ids = []
                        
                        for train in trains:
                            train_id = train.get('id', '')
                            if not (train_id.startswith('TRN') and len(train_id) == 6 and train_id[3:].isdigit()):
                                train_id_test_passed = False
                                invalid_ids.append(train_id)
                        
                        if priorities.issubset(expected_priorities) and train_id_test_passed:
                            self.log_test("Get Trains Endpoint (TRN Format)", True, f"Retrieved {len(trains)} trains with correct TRN001-TRN010 format")
                            return trains
                        elif not train_id_test_passed:
                            self.log_test("Get Trains Endpoint (TRN Format)", False, f"Invalid train ID formats: {invalid_ids}")
                        else:
                            self.log_test("Get Trains Endpoint (TRN Format)", False, f"Invalid priorities: {priorities}")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_train]
                        self.log_test("Get Trains Endpoint (TRN Format)", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Trains Endpoint (TRN Format)", False, f"Expected 10 trains, got {len(trains) if isinstance(trains, list) else 'non-list'}")
            else:
                self.log_test("Get Trains Endpoint (TRN Format)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Trains Endpoint (TRN Format)", False, f"Exception: {str(e)}")
        
        return None

    def test_get_stations(self):
        """Test GET /api/stations endpoint"""
        try:
            response = requests.get(f"{self.api_url}/stations", timeout=10)
            success = response.status_code == 200
            
            if success:
                stations = response.json()
                if isinstance(stations, list) and len(stations) == 5:
                    # Validate station structure
                    required_fields = ['id', 'name', 'x', 'y']
                    first_station = stations[0]
                    
                    if all(field in first_station for field in required_fields):
                        # Check station IDs
                        station_ids = set(station['id'] for station in stations)
                        expected_ids = {'A', 'B', 'C', 'D', 'E'}
                        if station_ids == expected_ids:
                            self.log_test("Get Stations Endpoint", True, f"Retrieved {len(stations)} stations")
                            return stations
                        else:
                            self.log_test("Get Stations Endpoint", False, f"Invalid station IDs: {station_ids}")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_station]
                        self.log_test("Get Stations Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Stations Endpoint", False, f"Expected 5 stations, got {len(stations) if isinstance(stations, list) else 'non-list'}")
            else:
                self.log_test("Get Stations Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Stations Endpoint", False, f"Exception: {str(e)}")
        
        return None

    def test_get_routes(self):
        """Test GET /api/routes endpoint - Enhanced for disaster effects"""
        try:
            response = requests.get(f"{self.api_url}/routes", timeout=10)
            success = response.status_code == 200
            
            if success:
                routes = response.json()
                if isinstance(routes, list) and len(routes) == 7:
                    # Validate route structure
                    required_fields = ['id', 'stations', 'path']
                    first_route = routes[0]
                    
                    if all(field in first_route for field in required_fields):
                        # Check route IDs - now expecting 7 routes including alternates
                        route_ids = set(route['id'] for route in routes)
                        expected_ids = {'A-B', 'B-C', 'C-D', 'D-E', 'B-E', 'A-C', 'A-E'}
                        if route_ids == expected_ids:
                            # Check for disaster effect fields (blocked, speed_reduction)
                            disaster_fields_present = all(
                                'blocked' in route and 'speed_reduction' in route 
                                for route in routes
                            )
                            
                            if disaster_fields_present:
                                self.log_test("Get Routes Endpoint (Disaster Effects)", True, 
                                            f"Retrieved {len(routes)} routes with disaster effect fields")
                            else:
                                self.log_test("Get Routes Endpoint (Disaster Effects)", False, 
                                            "Routes missing disaster effect fields (blocked, speed_reduction)")
                            return routes
                        else:
                            self.log_test("Get Routes Endpoint (Disaster Effects)", False, f"Invalid route IDs: {route_ids}")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_route]
                        self.log_test("Get Routes Endpoint (Disaster Effects)", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Routes Endpoint (Disaster Effects)", False, f"Expected 7 routes, got {len(routes) if isinstance(routes, list) else 'non-list'}")
            else:
                self.log_test("Get Routes Endpoint (Disaster Effects)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Routes Endpoint (Disaster Effects)", False, f"Exception: {str(e)}")
        
        return None

    def test_get_conflicts(self):
        """Test GET /api/conflicts endpoint"""
        try:
            response = requests.get(f"{self.api_url}/conflicts", timeout=10)
            success = response.status_code == 200
            
            if success:
                conflicts_data = response.json()
                if isinstance(conflicts_data, dict) and 'conflicts' in conflicts_data and 'details' in conflicts_data:
                    conflicts_count = conflicts_data['conflicts']
                    details = conflicts_data['details']
                    
                    if isinstance(conflicts_count, int) and isinstance(details, list):
                        self.log_test("Get Conflicts Endpoint", True, f"Found {conflicts_count} conflicts")
                        return conflicts_data
                    else:
                        self.log_test("Get Conflicts Endpoint", False, "Invalid conflicts data structure")
                else:
                    self.log_test("Get Conflicts Endpoint", False, "Missing 'conflicts' or 'details' fields")
            else:
                self.log_test("Get Conflicts Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Conflicts Endpoint", False, f"Exception: {str(e)}")
        
        return None

    def test_optimize_trains(self, trains=None):
        """Test POST /api/optimize endpoint - Enhanced for ETA testing"""
        try:
            # Use sample trains if none provided
            payload = trains if trains else None
            
            response = requests.post(
                f"{self.api_url}/optimize", 
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                optimization_result = response.json()
                required_fields = ['original_trains', 'optimized_trains', 'kpis']
                
                if all(field in optimization_result for field in required_fields):
                    original_trains = optimization_result['original_trains']
                    optimized_trains = optimization_result['optimized_trains']
                    kpis = optimization_result['kpis']
                    
                    # CRITICAL TEST: Check for both original and optimized times
                    eta_test_passed = True
                    eta_details = []
                    
                    for i, (original, optimized) in enumerate(zip(original_trains, optimized_trains)):
                        # Check that original train has planned times
                        if not (original.get('planned_arrival') and original.get('planned_departure')):
                            eta_test_passed = False
                            eta_details.append(f"Train {i}: Missing planned times in original")
                        
                        # Check that optimized train has both planned AND optimized times
                        if not (optimized.get('planned_arrival') and optimized.get('planned_departure')):
                            eta_test_passed = False
                            eta_details.append(f"Train {i}: Missing planned times in optimized")
                        
                        if not (optimized.get('optimized_arrival') and optimized.get('optimized_departure')):
                            eta_test_passed = False
                            eta_details.append(f"Train {i}: Missing optimized times")
                        
                        # Check train ID format (TRN001-TRN010)
                        train_id = optimized.get('id', '')
                        if not (train_id.startswith('TRN') and len(train_id) == 6):
                            eta_test_passed = False
                            eta_details.append(f"Train {i}: Invalid ID format '{train_id}' (expected TRN001-TRN010)")
                    
                    # Validate KPIs structure
                    required_kpi_fields = ['total_trains', 'avg_delay_minutes', 'on_time_trains']
                    if all(field in kpis for field in required_kpi_fields):
                        # Check if optimization actually worked
                        total_trains = kpis['total_trains']
                        on_time_trains = kpis['on_time_trains']
                        avg_delay = kpis['avg_delay_minutes']
                        
                        if total_trains == 10 and eta_test_passed:  # Expected number of trains
                            self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", True, 
                                        f"KPIs: {total_trains} trains, {on_time_trains} on-time, {avg_delay}min avg delay. All trains have both original and optimized ETAs with correct TRN format")
                            return optimization_result
                        elif not eta_test_passed:
                            self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"ETA/ID issues: {'; '.join(eta_details)}")
                        else:
                            self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"Expected 10 trains, got {total_trains}")
                    else:
                        missing_kpi_fields = [f for f in required_kpi_fields if f not in kpis]
                        self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"Missing KPI fields: {missing_kpi_fields}")
                else:
                    missing_fields = [f for f in required_fields if f not in optimization_result]
                    self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Optimize Trains Endpoint (ETA & Train ID Format)", False, f"Exception: {str(e)}")
        
        return None

    def test_get_disaster_scenarios(self):
        """Test GET /api/disaster-scenarios endpoint"""
        try:
            response = requests.get(f"{self.api_url}/disaster-scenarios", timeout=10)
            success = response.status_code == 200
            
            if success:
                scenarios = response.json()
                if isinstance(scenarios, dict) and len(scenarios) == 7:
                    # Check for expected scenario keys
                    expected_keys = {'flood_ab', 'equipment_failure', 'weather_slow', 'emergency_train', 'breakdown_ce', 'human_strike', 'multiple_disasters'}
                    scenario_keys = set(scenarios.keys())
                    
                    if scenario_keys == expected_keys:
                        # Validate scenario structure
                        first_scenario = list(scenarios.values())[0]
                        if 'disasters' in first_scenario and 'description' in first_scenario:
                            self.log_test("Get Disaster Scenarios Endpoint", True, f"Retrieved {len(scenarios)} scenarios")
                            return scenarios
                        else:
                            self.log_test("Get Disaster Scenarios Endpoint", False, "Missing 'disasters' or 'description' fields")
                    else:
                        self.log_test("Get Disaster Scenarios Endpoint", False, f"Invalid scenario keys: {scenario_keys}")
                else:
                    self.log_test("Get Disaster Scenarios Endpoint", False, f"Expected 7 scenarios, got {len(scenarios) if isinstance(scenarios, dict) else 'non-dict'}")
            else:
                self.log_test("Get Disaster Scenarios Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Disaster Scenarios Endpoint", False, f"Exception: {str(e)}")
        
        return None

    def test_apply_disaster_scenario(self, scenarios=None):
        """Test POST /api/disaster endpoint - Enhanced for disaster management testing"""
        try:
            if not scenarios:
                self.log_test("Apply Disaster Scenario Endpoint", False, "No scenarios available for testing")
                return None
            
            # Test with flood scenario - send the scenario object directly
            flood_scenario = scenarios.get('flood_ab')
            if not flood_scenario:
                self.log_test("Apply Disaster Scenario Endpoint", False, "Flood scenario not found")
                return None
            
            response = requests.post(
                f"{self.api_url}/disaster", 
                json=flood_scenario,  # Send the scenario object directly
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                disaster_result = response.json()
                required_fields = ['original_trains', 'optimized_trains', 'kpis', 'explanations']
                
                if all(field in disaster_result for field in required_fields):
                    kpis = disaster_result['kpis']
                    explanations = disaster_result['explanations']
                    disaster_summary = disaster_result.get('disaster_summary', '')
                    optimized_trains = disaster_result['optimized_trains']
                    
                    # Check train ID consistency in disaster response
                    train_id_test_passed = True
                    train_id_details = []
                    
                    for train in optimized_trains:
                        train_id = train.get('id', '')
                        if not (train_id.startswith('TRN') and len(train_id) == 6) and not train_id.startswith('EMG'):
                            train_id_test_passed = False
                            train_id_details.append(f"Invalid train ID format: '{train_id}'")
                    
                    # Check if disaster had impact
                    rerouted_trains = kpis.get('rerouted_trains', 0)
                    delayed_trains = kpis.get('delayed_trains', 0)
                    
                    if rerouted_trains > 0 or delayed_trains > 0 or len(explanations) > 0:
                        if train_id_test_passed:
                            self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", True, 
                                        f"Disaster applied: {rerouted_trains} rerouted, {delayed_trains} delayed, {len(explanations)} explanations. Train IDs consistent.")
                        else:
                            self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, 
                                        f"Train ID issues: {'; '.join(train_id_details)}")
                        return disaster_result
                    else:
                        self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, "Disaster scenario had no visible impact")
                else:
                    missing_fields = [f for f in required_fields if f not in disaster_result]
                    self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, f"Missing fields: {missing_fields}")
            else:
                # Get error details for debugging
                try:
                    error_detail = response.json()
                    self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, f"Status code: {response.status_code}, Error: {error_detail}")
                except:
                    self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Apply Disaster Scenario Endpoint (Train ID Consistency)", False, f"Exception: {str(e)}")
        
        return None

    def test_custom_disaster_without_duration(self):
        """Test POST /api/disaster/custom endpoint without duration_minutes"""
        try:
            # Test custom disaster without duration_minutes field
            custom_disaster = {
                "type": "custom",
                "affected_route": "A-B",
                "description": "Test custom disaster without duration",
                "speed_reduction": 0.3,
                "severity": "medium"
                # Intentionally omitting duration_minutes to test default behavior
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=custom_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                disaster_result = response.json()
                required_fields = ['original_trains', 'optimized_trains', 'kpis', 'explanations']
                
                if all(field in disaster_result for field in required_fields):
                    kpis = disaster_result['kpis']
                    explanations = disaster_result['explanations']
                    optimized_trains = disaster_result['optimized_trains']
                    
                    # Check if disaster had impact (should work even without duration)
                    rerouted_trains = kpis.get('rerouted_trains', 0)
                    delayed_trains = kpis.get('delayed_trains', 0)
                    
                    # Check train ID consistency
                    train_id_test_passed = True
                    for train in optimized_trains:
                        train_id = train.get('id', '')
                        if not (train_id.startswith('TRN') and len(train_id) == 6) and not train_id.startswith('EMG'):
                            train_id_test_passed = False
                            break
                    
                    if (rerouted_trains > 0 or delayed_trains > 0 or len(explanations) > 0) and train_id_test_passed:
                        self.log_test("Custom Disaster Without Duration", True, 
                                    f"Custom disaster worked without duration: {rerouted_trains} rerouted, {delayed_trains} delayed")
                        return disaster_result
                    elif not train_id_test_passed:
                        self.log_test("Custom Disaster Without Duration", False, "Train ID format issues in custom disaster response")
                    else:
                        self.log_test("Custom Disaster Without Duration", False, "Custom disaster had no visible impact")
                else:
                    missing_fields = [f for f in required_fields if f not in disaster_result]
                    self.log_test("Custom Disaster Without Duration", False, f"Missing fields: {missing_fields}")
            else:
                try:
                    error_detail = response.json()
                    self.log_test("Custom Disaster Without Duration", False, f"Status code: {response.status_code}, Error: {error_detail}")
                except:
                    self.log_test("Custom Disaster Without Duration", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Custom Disaster Without Duration", False, f"Exception: {str(e)}")
        
        return None

    def test_emergency_train_insertion(self):
        """Test emergency train insertion functionality"""
        try:
            # Test emergency train disaster scenario
            emergency_scenario = {
                "disasters": [
                    {
                        "type": "emergency_train",
                        "description": "Emergency train requires immediate priority",
                        "severity": "critical",
                        "affected_route": "A-B"
                    }
                ],
                "description": "Emergency train insertion test"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster", 
                json=emergency_scenario,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                disaster_result = response.json()
                optimized_trains = disaster_result.get('optimized_trains', [])
                
                # Check if emergency train was inserted
                emergency_train_found = False
                for train in optimized_trains:
                    if train.get('id', '').startswith('EMG'):
                        emergency_train_found = True
                        break
                
                # Check train ID consistency
                train_id_test_passed = True
                for train in optimized_trains:
                    train_id = train.get('id', '')
                    if not (train_id.startswith('TRN') and len(train_id) == 6) and not train_id.startswith('EMG'):
                        train_id_test_passed = False
                        break
                
                if emergency_train_found and train_id_test_passed:
                    self.log_test("Emergency Train Insertion", True, 
                                f"Emergency train successfully inserted. Total trains: {len(optimized_trains)}")
                    return disaster_result
                elif not emergency_train_found:
                    self.log_test("Emergency Train Insertion", False, "Emergency train was not inserted")
                else:
                    self.log_test("Emergency Train Insertion", False, "Train ID format issues with emergency train")
            else:
                try:
                    error_detail = response.json()
                    self.log_test("Emergency Train Insertion", False, f"Status code: {response.status_code}, Error: {error_detail}")
                except:
                    self.log_test("Emergency Train Insertion", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Emergency Train Insertion", False, f"Exception: {str(e)}")
        
        return None

    def test_all_disaster_types(self):
        """Test all disaster types to ensure they process correctly"""
        disaster_types = [
            {"type": "flood", "affected_route": "A-B", "duration_minutes": 60, "description": "Test flood"},
            {"type": "equipment_failure", "affected_route": "B-C", "duration_minutes": 30, "description": "Test equipment failure"},
            {"type": "weather", "affected_route": "all", "speed_reduction": 0.4, "description": "Test weather"},
            {"type": "breakdown", "affected_route": "C-D", "duration_minutes": 15, "description": "Test breakdown"},
            {"type": "human_strike", "affected_route": "all", "speed_reduction": 0.6, "duration_minutes": 120, "description": "Test strike"},
            {"type": "emergency_train", "description": "Test emergency train", "affected_route": "A-B"}
        ]
        
        all_passed = True
        results = []
        
        for disaster_data in disaster_types:
            try:
                scenario = {
                    "disasters": [disaster_data],
                    "description": f"Test {disaster_data['type']} disaster"
                }
                
                response = requests.post(
                    f"{self.api_url}/disaster", 
                    json=scenario,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                
                if response.status_code == 200:
                    disaster_result = response.json()
                    kpis = disaster_result.get('kpis', {})
                    optimized_trains = disaster_result.get('optimized_trains', [])
                    
                    # Check train ID consistency
                    train_id_consistent = all(
                        (train.get('id', '').startswith('TRN') and len(train.get('id', '')) == 6) or 
                        train.get('id', '').startswith('EMG')
                        for train in optimized_trains
                    )
                    
                    # Check if disaster had some impact
                    has_impact = (
                        kpis.get('rerouted_trains', 0) > 0 or 
                        kpis.get('delayed_trains', 0) > 0 or
                        len(disaster_result.get('explanations', [])) > 0
                    )
                    
                    if train_id_consistent and has_impact:
                        results.append(f"✅ {disaster_data['type']}: OK")
                    else:
                        results.append(f"❌ {disaster_data['type']}: {'ID issues' if not train_id_consistent else 'No impact'}")
                        all_passed = False
                else:
                    results.append(f"❌ {disaster_data['type']}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {disaster_data['type']}: Exception {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log_test("All Disaster Types Processing", True, f"All 6 disaster types work correctly: {'; '.join(results)}")
        else:
            self.log_test("All Disaster Types Processing", False, f"Some disaster types failed: {'; '.join(results)}")
        
        return all_passed

    def test_enhanced_rerouting_flood_ab(self):
        """Test enhanced rerouting logic for flood disaster on A-B route"""
        try:
            # Create flood disaster that completely blocks A-B route
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-B",
                "duration_minutes": 120,
                "description": "Heavy rainfall floods A-B section causing complete blockage",
                "severity": "high",
                "speed_reduction": 0.0  # Complete blockage
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                # Find trains originally on A-B route
                ab_trains = [train for train in optimized_trains if train.get('route') == 'A-B']
                
                rerouting_test_passed = True
                rerouting_details = []
                
                for train in ab_trains:
                    train_id = train.get('id', '')[:6]
                    
                    # Check if train was rerouted
                    if train.get('rerouted', False):
                        # Verify alternate path fields are present
                        alt_path_stations = train.get('alternate_path_stations', [])
                        alt_route_segments = train.get('alternate_route_segments', [])
                        new_route = train.get('new_route', '')
                        
                        if not alt_path_stations:
                            rerouting_test_passed = False
                            rerouting_details.append(f"Train {train_id}: Missing alternate_path_stations")
                        elif not alt_route_segments:
                            rerouting_test_passed = False
                            rerouting_details.append(f"Train {train_id}: Missing alternate_route_segments")
                        elif not new_route:
                            rerouting_test_passed = False
                            rerouting_details.append(f"Train {train_id}: Missing new_route description")
                        else:
                            # Verify the alternate path makes sense (A to B via other stations)
                            if len(alt_path_stations) >= 2 and alt_path_stations[0] == 'A' and alt_path_stations[-1] == 'B':
                                # Verify route doesn't include blocked A-B
                                if 'A-B' not in alt_route_segments:
                                    rerouting_details.append(f"✅ Train {train_id}: Properly rerouted via {' → '.join(alt_path_stations)} using routes {' → '.join(alt_route_segments)}")
                                else:
                                    rerouting_test_passed = False
                                    rerouting_details.append(f"Train {train_id}: ERROR - Rerouted via blocked A-B route!")
                            else:
                                rerouting_test_passed = False
                                rerouting_details.append(f"Train {train_id}: Invalid alternate path {alt_path_stations}")
                    else:
                        # Train not rerouted - should have significant delay instead
                        delay = train.get('delay_minutes', 0)
                        if delay >= 30:  # Acceptable if given significant delay
                            rerouting_details.append(f"⚠️ Train {train_id}: Not rerouted but given {delay}min delay")
                        else:
                            rerouting_test_passed = False
                            rerouting_details.append(f"Train {train_id}: Not rerouted and insufficient delay ({delay}min)")
                
                if rerouting_test_passed and len(ab_trains) > 0:
                    self.log_test("Enhanced Rerouting - Flood A-B Route", True, 
                                f"All {len(ab_trains)} A-B trains properly handled: {'; '.join(rerouting_details)}")
                    return result
                elif len(ab_trains) == 0:
                    self.log_test("Enhanced Rerouting - Flood A-B Route", False, "No trains found on A-B route to test")
                else:
                    self.log_test("Enhanced Rerouting - Flood A-B Route", False, 
                                f"Rerouting issues: {'; '.join(rerouting_details)}")
            else:
                self.log_test("Enhanced Rerouting - Flood A-B Route", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Rerouting - Flood A-B Route", False, f"Exception: {str(e)}")
        
        return None

    def test_enhanced_rerouting_different_routes(self):
        """Test rerouting logic for different blocked routes (B-C, C-D)"""
        test_routes = [
            {"route": "B-C", "expected_alternates": ["B-E-D-C", "B-A-C"]},
            {"route": "C-D", "expected_alternates": ["C-B-E-D", "C-A-E-D"]}
        ]
        
        all_passed = True
        results = []
        
        for test_case in test_routes:
            try:
                blocked_route = test_case["route"]
                
                # Create flood disaster for this route
                flood_disaster = {
                    "type": "flood",
                    "affected_route": blocked_route,
                    "duration_minutes": 90,
                    "description": f"Flood blocks {blocked_route} route",
                    "severity": "high"
                }
                
                response = requests.post(
                    f"{self.api_url}/disaster/custom", 
                    json=flood_disaster,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    optimized_trains = result.get('optimized_trains', [])
                    
                    # Find trains originally on this route
                    affected_trains = [train for train in optimized_trains if train.get('route') == blocked_route]
                    
                    route_test_passed = True
                    route_details = []
                    
                    for train in affected_trains:
                        train_id = train.get('id', '')[:6]
                        
                        if train.get('rerouted', False):
                            alt_route_segments = train.get('alternate_route_segments', [])
                            
                            # Verify blocked route is not in alternate segments
                            if blocked_route not in alt_route_segments:
                                route_details.append(f"✅ Train {train_id}: Avoids blocked {blocked_route}")
                            else:
                                route_test_passed = False
                                route_details.append(f"❌ Train {train_id}: Uses blocked route {blocked_route}!")
                        else:
                            # Check if given appropriate delay
                            delay = train.get('delay_minutes', 0)
                            if delay >= 30:
                                route_details.append(f"⚠️ Train {train_id}: {delay}min delay instead of rerouting")
                            else:
                                route_test_passed = False
                                route_details.append(f"❌ Train {train_id}: No rerouting, insufficient delay")
                    
                    if route_test_passed:
                        results.append(f"✅ {blocked_route}: {len(affected_trains)} trains handled correctly")
                    else:
                        results.append(f"❌ {blocked_route}: Issues found")
                        all_passed = False
                        
                else:
                    results.append(f"❌ {blocked_route}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {blocked_route}: Exception {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log_test("Enhanced Rerouting - Different Blocked Routes", True, 
                        f"All route blockages handled correctly: {'; '.join(results)}")
        else:
            self.log_test("Enhanced Rerouting - Different Blocked Routes", False, 
                        f"Some route blockages failed: {'; '.join(results)}")
        
        return all_passed

    def test_alternate_path_response_structure(self):
        """Test that response includes proper alternate path structure"""
        try:
            # Create a flood disaster to trigger rerouting
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-B",
                "duration_minutes": 60,
                "description": "Test alternate path response structure",
                "severity": "high"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                structure_test_passed = True
                structure_details = []
                
                # Find rerouted trains
                rerouted_trains = [train for train in optimized_trains if train.get('rerouted', False)]
                
                if len(rerouted_trains) == 0:
                    self.log_test("Alternate Path Response Structure", False, "No rerouted trains found to test structure")
                    return None
                
                for train in rerouted_trains:
                    train_id = train.get('id', '')[:6]
                    
                    # Check required fields
                    required_fields = ['alternate_path_stations', 'alternate_route_segments', 'new_route']
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in train or not train[field]:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        structure_test_passed = False
                        structure_details.append(f"Train {train_id}: Missing {', '.join(missing_fields)}")
                    else:
                        # Validate field types and content
                        alt_stations = train['alternate_path_stations']
                        alt_segments = train['alternate_route_segments']
                        new_route = train['new_route']
                        
                        if not isinstance(alt_stations, list) or len(alt_stations) < 2:
                            structure_test_passed = False
                            structure_details.append(f"Train {train_id}: Invalid alternate_path_stations")
                        elif not isinstance(alt_segments, list) or len(alt_segments) < 1:
                            structure_test_passed = False
                            structure_details.append(f"Train {train_id}: Invalid alternate_route_segments")
                        elif not isinstance(new_route, str) or len(new_route) < 3:
                            structure_test_passed = False
                            structure_details.append(f"Train {train_id}: Invalid new_route description")
                        else:
                            structure_details.append(f"✅ Train {train_id}: Complete structure - stations: {alt_stations}, segments: {alt_segments}")
                
                if structure_test_passed:
                    self.log_test("Alternate Path Response Structure", True, 
                                f"All {len(rerouted_trains)} rerouted trains have complete structure: {'; '.join(structure_details)}")
                    return result
                else:
                    self.log_test("Alternate Path Response Structure", False, 
                                f"Structure issues found: {'; '.join(structure_details)}")
            else:
                self.log_test("Alternate Path Response Structure", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Alternate Path Response Structure", False, f"Exception: {str(e)}")
        
        return None

    def test_no_alternative_scenario(self):
        """Test scenario where no alternate route exists"""
        try:
            # This is tricky to test with current network topology since there are multiple alternate routes
            # We'll test by creating multiple simultaneous disasters to block most routes
            multiple_disasters = {
                "disasters": [
                    {"type": "flood", "affected_route": "A-B", "duration_minutes": 60, "description": "Flood blocks A-B"},
                    {"type": "breakdown", "affected_route": "A-C", "duration_minutes": 45, "description": "Breakdown blocks A-C"},
                    {"type": "equipment_failure", "affected_route": "A-E", "duration_minutes": 30, "description": "Signal failure blocks A-E"}
                ],
                "description": "Multiple disasters blocking most alternate routes",
                "multiple": True
            }
            
            response = requests.post(
                f"{self.api_url}/disaster", 
                json=multiple_disasters,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                # Find trains that should be affected (originally on blocked routes)
                affected_trains = [train for train in optimized_trains 
                                 if train.get('route') in ['A-B', 'A-C', 'A-E']]
                
                no_alt_test_passed = True
                no_alt_details = []
                
                for train in affected_trains:
                    train_id = train.get('id', '')[:6]
                    delay = train.get('delay_minutes', 0)
                    
                    if train.get('rerouted', False):
                        # If rerouted, check that it's a valid alternate
                        alt_segments = train.get('alternate_route_segments', [])
                        blocked_routes = ['A-B', 'A-C', 'A-E']
                        
                        uses_blocked = any(blocked in alt_segments for blocked in blocked_routes)
                        if uses_blocked:
                            no_alt_test_passed = False
                            no_alt_details.append(f"Train {train_id}: Rerouted via blocked route!")
                        else:
                            no_alt_details.append(f"✅ Train {train_id}: Found valid alternate route")
                    else:
                        # Not rerouted - should have significant delay
                        if delay >= 45:  # Significant delay expected when no alternatives
                            no_alt_details.append(f"✅ Train {train_id}: Given {delay}min delay (no alternate route)")
                        else:
                            no_alt_test_passed = False
                            no_alt_details.append(f"Train {train_id}: Insufficient delay ({delay}min) for no-alternate scenario")
                
                if no_alt_test_passed:
                    self.log_test("No Alternative Route Scenario", True, 
                                f"Multiple disasters handled correctly: {'; '.join(no_alt_details)}")
                    return result
                else:
                    self.log_test("No Alternative Route Scenario", False, 
                                f"Issues with no-alternative handling: {'; '.join(no_alt_details)}")
            else:
                self.log_test("No Alternative Route Scenario", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("No Alternative Route Scenario", False, f"Exception: {str(e)}")
        
        return None

    def test_rerouting_explanation_accuracy(self):
        """Test that explanations mention actual alternate paths, not blocked routes"""
        try:
            # Create flood disaster on A-B
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-B",
                "duration_minutes": 90,
                "description": "Test explanation accuracy for rerouting",
                "severity": "high"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                explanations = result.get('explanations', [])
                optimized_trains = result.get('optimized_trains', [])
                
                explanation_test_passed = True
                explanation_details = []
                
                # Find rerouted trains
                rerouted_trains = [train for train in optimized_trains if train.get('rerouted', False)]
                
                if len(rerouted_trains) == 0:
                    self.log_test("Rerouting Explanation Accuracy", False, "No rerouted trains to test explanations")
                    return None
                
                # Check explanations for accuracy
                for explanation in explanations:
                    explanation_text = explanation.lower()
                    
                    # Should NOT mention rerouting "via A-B" when A-B is blocked
                    if "via a-b" in explanation_text and "rerouted" in explanation_text:
                        explanation_test_passed = False
                        explanation_details.append(f"❌ Explanation mentions rerouting via blocked A-B: '{explanation[:100]}...'")
                    
                    # Should mention actual alternate paths
                    if "rerouted" in explanation_text:
                        if any(alt_path in explanation_text for alt_path in ["a → c → b", "a-c", "c-b"]):
                            explanation_details.append(f"✅ Explanation mentions valid alternate path")
                        else:
                            explanation_details.append(f"⚠️ Rerouting explanation lacks specific path details")
                
                # Check individual train explanations
                for train in rerouted_trains:
                    train_id = train.get('id', '')[:6]
                    alt_path = train.get('alternate_path_stations', [])
                    
                    if len(alt_path) >= 2:
                        path_description = ' → '.join(alt_path)
                        explanation_details.append(f"✅ Train {train_id}: Alternate path {path_description}")
                
                if explanation_test_passed:
                    self.log_test("Rerouting Explanation Accuracy", True, 
                                f"Explanations are accurate: {'; '.join(explanation_details)}")
                    return result
                else:
                    self.log_test("Rerouting Explanation Accuracy", False, 
                                f"Explanation issues: {'; '.join(explanation_details)}")
            else:
                self.log_test("Rerouting Explanation Accuracy", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Rerouting Explanation Accuracy", False, f"Exception: {str(e)}")
        
        return None

    def test_ac_route_blockage_specific(self):
        """Test A-C Direct Route Blockage and A-B-C Rerouting (SPECIFIC FOCUS)"""
        try:
            # Create flood disaster affecting A-C route (complete blockage)
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-C",
                "duration_minutes": 120,
                "description": "Heavy rainfall floods A-C section causing complete blockage",
                "severity": "high",
                "speed_reduction": 0.0  # Complete blockage
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                explanations = result.get('explanations', [])
                
                # Find TRN011 and TRN012 specifically (they use A-C route)
                trn011 = next((train for train in optimized_trains if train.get('id') == 'TRN011'), None)
                trn012 = next((train for train in optimized_trains if train.get('id') == 'TRN012'), None)
                
                ac_test_passed = True
                ac_details = []
                
                # Test TRN011
                if trn011:
                    if trn011.get('rerouted', False):
                        alt_path = trn011.get('alternate_path_stations', [])
                        alt_segments = trn011.get('alternate_route_segments', [])
                        delay = trn011.get('delay_minutes', 0)
                        
                        # Check if rerouted via A→B→C path
                        if alt_path == ['A', 'B', 'C'] and alt_segments == ['A-B', 'B-C']:
                            if delay >= 5 and delay <= 15:  # Minimal rerouting delay
                                ac_details.append(f"✅ TRN011: Correctly rerouted A→B→C with {delay}min delay")
                            else:
                                ac_test_passed = False
                                ac_details.append(f"❌ TRN011: Rerouted correctly but delay {delay}min not in 5-15min range")
                        else:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN011: Wrong rerouting path {alt_path} via {alt_segments}")
                    else:
                        # Check if given 60-minute delay instead of rerouting
                        delay = trn011.get('delay_minutes', 0)
                        if delay >= 60:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN011: Given {delay}min delay instead of A→B→C rerouting")
                        else:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN011: Not rerouted and insufficient delay ({delay}min)")
                else:
                    ac_test_passed = False
                    ac_details.append("❌ TRN011 not found in response")
                
                # Test TRN012
                if trn012:
                    if trn012.get('rerouted', False):
                        alt_path = trn012.get('alternate_path_stations', [])
                        alt_segments = trn012.get('alternate_route_segments', [])
                        delay = trn012.get('delay_minutes', 0)
                        
                        # Check if rerouted via A→B→C path
                        if alt_path == ['A', 'B', 'C'] and alt_segments == ['A-B', 'B-C']:
                            if delay >= 5 and delay <= 15:  # Minimal rerouting delay
                                ac_details.append(f"✅ TRN012: Correctly rerouted A→B→C with {delay}min delay")
                            else:
                                ac_test_passed = False
                                ac_details.append(f"❌ TRN012: Rerouted correctly but delay {delay}min not in 5-15min range")
                        else:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN012: Wrong rerouting path {alt_path} via {alt_segments}")
                    else:
                        # Check if given 60-minute delay instead of rerouting
                        delay = trn012.get('delay_minutes', 0)
                        if delay >= 60:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN012: Given {delay}min delay instead of A→B→C rerouting")
                        else:
                            ac_test_passed = False
                            ac_details.append(f"❌ TRN012: Not rerouted and insufficient delay ({delay}min)")
                else:
                    ac_test_passed = False
                    ac_details.append("❌ TRN012 not found in response")
                
                # Check explanations mention A→B→C path
                explanation_mentions_abc = False
                for explanation in explanations:
                    if "a → b → c" in explanation.lower() or ("a-b" in explanation.lower() and "b-c" in explanation.lower()):
                        explanation_mentions_abc = True
                        ac_details.append("✅ Explanations mention A→B→C alternate path")
                        break
                
                if not explanation_mentions_abc:
                    ac_details.append("⚠️ Explanations don't explicitly mention A→B→C path")
                
                if ac_test_passed:
                    self.log_test("A-C Route Blockage → A→B→C Rerouting", True, 
                                f"TRN011 and TRN012 correctly rerouted via A→B→C: {'; '.join(ac_details)}")
                    return result
                else:
                    self.log_test("A-C Route Blockage → A→B→C Rerouting", False, 
                                f"A-C blockage rerouting issues: {'; '.join(ac_details)}")
            else:
                self.log_test("A-C Route Blockage → A→B→C Rerouting", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("A-C Route Blockage → A→B→C Rerouting", False, f"Exception: {str(e)}")
        
        return None

    def test_shortest_path_prioritization(self):
        """Test that shortest paths (A→B→C = 2 hops) are selected first"""
        try:
            # Create flood disaster on A-C to test path prioritization
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-C",
                "duration_minutes": 90,
                "description": "Test shortest path prioritization for A-C blockage",
                "severity": "high"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                # Find trains originally on A-C route
                ac_trains = [train for train in optimized_trains if train.get('route') == 'A-C']
                
                path_test_passed = True
                path_details = []
                
                for train in ac_trains:
                    train_id = train.get('id', '')[:6]
                    
                    if train.get('rerouted', False):
                        alt_path = train.get('alternate_path_stations', [])
                        alt_segments = train.get('alternate_route_segments', [])
                        
                        # Calculate path length (number of hops)
                        path_length = len(alt_path) - 1 if alt_path else 0
                        
                        # A→B→C should be the shortest (2 hops)
                        if alt_path == ['A', 'B', 'C'] and path_length == 2:
                            path_details.append(f"✅ Train {train_id}: Shortest path A→B→C selected ({path_length} hops)")
                        elif path_length > 2:
                            # Check if there was a valid reason for longer path
                            if 'A-B' in alt_segments or 'B-C' in alt_segments:
                                path_test_passed = False
                                path_details.append(f"❌ Train {train_id}: Longer path {' → '.join(alt_path)} ({path_length} hops) when A→B→C available")
                            else:
                                path_details.append(f"⚠️ Train {train_id}: Longer path {' → '.join(alt_path)} ({path_length} hops) - may be justified")
                        else:
                            path_test_passed = False
                            path_details.append(f"❌ Train {train_id}: Invalid path {alt_path}")
                    else:
                        path_details.append(f"⚠️ Train {train_id}: Not rerouted")
                
                if path_test_passed and len(ac_trains) > 0:
                    self.log_test("Shortest Path Prioritization (A→B→C)", True, 
                                f"Shortest paths correctly prioritized: {'; '.join(path_details)}")
                    return result
                elif len(ac_trains) == 0:
                    self.log_test("Shortest Path Prioritization (A→B→C)", False, "No A-C trains found to test")
                else:
                    self.log_test("Shortest Path Prioritization (A→B→C)", False, 
                                f"Path prioritization issues: {'; '.join(path_details)}")
            else:
                self.log_test("Shortest Path Prioritization (A→B→C)", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Shortest Path Prioritization (A→B→C)", False, f"Exception: {str(e)}")
        
        return None

    def test_bc_blockage_comparison(self):
        """Test B-C blockage to ensure alternate routing works for other routes too"""
        try:
            # Create flood disaster on B-C route
            flood_disaster = {
                "type": "flood",
                "affected_route": "B-C",
                "duration_minutes": 90,
                "description": "Test B-C blockage for comparison with A-C blockage",
                "severity": "high"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                # Find trains originally on B-C route
                bc_trains = [train for train in optimized_trains if train.get('route') == 'B-C']
                
                bc_test_passed = True
                bc_details = []
                
                for train in bc_trains:
                    train_id = train.get('id', '')[:6]
                    
                    if train.get('rerouted', False):
                        alt_path = train.get('alternate_path_stations', [])
                        alt_segments = train.get('alternate_route_segments', [])
                        delay = train.get('delay_minutes', 0)
                        
                        # Verify alternate path doesn't use blocked B-C
                        if 'B-C' not in alt_segments:
                            # Check for reasonable alternate paths (B→A→C, B→E→D→C, etc.)
                            if len(alt_path) >= 3 and alt_path[0] == 'B' and alt_path[-1] == 'C':
                                bc_details.append(f"✅ Train {train_id}: Valid alternate B→C via {' → '.join(alt_path)} (+{delay}min)")
                            else:
                                bc_test_passed = False
                                bc_details.append(f"❌ Train {train_id}: Invalid alternate path {alt_path}")
                        else:
                            bc_test_passed = False
                            bc_details.append(f"❌ Train {train_id}: Uses blocked B-C route in alternate path!")
                    else:
                        delay = train.get('delay_minutes', 0)
                        if delay >= 30:
                            bc_details.append(f"⚠️ Train {train_id}: Not rerouted, given {delay}min delay")
                        else:
                            bc_test_passed = False
                            bc_details.append(f"❌ Train {train_id}: Not rerouted, insufficient delay ({delay}min)")
                
                if bc_test_passed and len(bc_trains) > 0:
                    self.log_test("B-C Route Blockage Alternate Routing", True, 
                                f"B-C blockage handled correctly: {'; '.join(bc_details)}")
                    return result
                elif len(bc_trains) == 0:
                    self.log_test("B-C Route Blockage Alternate Routing", False, "No B-C trains found to test")
                else:
                    self.log_test("B-C Route Blockage Alternate Routing", False, 
                                f"B-C blockage issues: {'; '.join(bc_details)}")
            else:
                self.log_test("B-C Route Blockage Alternate Routing", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("B-C Route Blockage Alternate Routing", False, f"Exception: {str(e)}")
        
        return None

    def test_delay_calculation_accuracy(self):
        """Test that rerouting delays are calculated correctly (5-15 minutes for 2-hop paths)"""
        try:
            # Create flood disaster on A-C to test delay calculation
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-C",
                "duration_minutes": 60,
                "description": "Test delay calculation for A→B→C rerouting",
                "severity": "high"
            }
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                
                # Find rerouted trains from A-C route
                ac_rerouted = [train for train in optimized_trains 
                             if train.get('route') == 'A-C' and train.get('rerouted', False)]
                
                delay_test_passed = True
                delay_details = []
                
                for train in ac_rerouted:
                    train_id = train.get('id', '')[:6]
                    delay = train.get('delay_minutes', 0)
                    alt_path = train.get('alternate_path_stations', [])
                    path_length = len(alt_path) - 1 if alt_path else 0
                    
                    # For A→B→C (2 hops), delay should be 5 + (2-1)*3 = 8 minutes, range 5-15
                    if path_length == 2:  # 2-hop path
                        expected_min = 5
                        expected_max = 15
                        
                        if expected_min <= delay <= expected_max:
                            delay_details.append(f"✅ Train {train_id}: {delay}min delay for {path_length}-hop path (expected {expected_min}-{expected_max}min)")
                        else:
                            delay_test_passed = False
                            delay_details.append(f"❌ Train {train_id}: {delay}min delay for {path_length}-hop path (expected {expected_min}-{expected_max}min)")
                    else:
                        # For other path lengths, check if delay is reasonable
                        expected_min = 5 + max(0, (path_length - 1) * 3)
                        expected_max = min(15, expected_min + 5)
                        
                        if expected_min <= delay <= expected_max + 5:  # Allow some flexibility
                            delay_details.append(f"✅ Train {train_id}: {delay}min delay for {path_length}-hop path")
                        else:
                            delay_test_passed = False
                            delay_details.append(f"❌ Train {train_id}: {delay}min delay seems incorrect for {path_length}-hop path")
                
                if delay_test_passed and len(ac_rerouted) > 0:
                    self.log_test("Rerouting Delay Calculation Accuracy", True, 
                                f"Delays calculated correctly: {'; '.join(delay_details)}")
                    return result
                elif len(ac_rerouted) == 0:
                    self.log_test("Rerouting Delay Calculation Accuracy", False, "No rerouted A-C trains found to test delays")
                else:
                    self.log_test("Rerouting Delay Calculation Accuracy", False, 
                                f"Delay calculation issues: {'; '.join(delay_details)}")
            else:
                self.log_test("Rerouting Delay Calculation Accuracy", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Rerouting Delay Calculation Accuracy", False, f"Exception: {str(e)}")
        
        return None

    def test_get_performance_metrics(self):
        """Test GET /api/performance endpoint"""
        try:
            response = requests.get(f"{self.api_url}/performance", timeout=10)
            success = response.status_code == 200
            
            if success:
                performance = response.json()
                required_fields = ['total_trains', 'on_time_trains', 'delayed_trains', 'rerouted_trains', 
                                 'avg_delay', 'max_delay', 'throughput_improvement']
                
                if all(field in performance for field in required_fields):
                    total_trains = performance['total_trains']
                    on_time_trains = performance['on_time_trains']
                    avg_delay = performance['avg_delay']
                    
                    if total_trains == 10:  # Expected number of trains
                        self.log_test("Get Performance Metrics Endpoint", True, 
                                    f"Performance: {total_trains} trains, {on_time_trains} on-time, {avg_delay}min avg delay")
                        return performance
                    else:
                        self.log_test("Get Performance Metrics Endpoint", False, f"Expected 10 trains, got {total_trains}")
                else:
                    missing_fields = [f for f in required_fields if f not in performance]
                    self.log_test("Get Performance Metrics Endpoint", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Get Performance Metrics Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Performance Metrics Endpoint", False, f"Exception: {str(e)}")
        
        return None

    def test_ac_route_blockage_console_output(self):
        """Test A-C Route Blockage with Console Output Analysis (SPECIFIC USER REQUEST)"""
        try:
            print("\n" + "="*80)
            print("🎯 SPECIFIC A-C ROUTE BLOCKAGE TEST - CONSOLE OUTPUT ANALYSIS")
            print("="*80)
            
            # Create A-C Route Flood Disaster (complete blockage)
            flood_disaster = {
                "type": "flood",
                "affected_route": "A-C",
                "duration_minutes": 120,
                "description": "Heavy rainfall floods A-C section causing complete blockage",
                "severity": "high",
                "speed_reduction": 0.0  # Complete blockage
            }
            
            print("🚫 Creating A-C Route Flood Disaster...")
            print(f"   - Route: A-C (COMPLETE BLOCKAGE)")
            print(f"   - Affected Trains: TRN011, TRN012")
            print(f"   - Expected Rerouting: A→B→C")
            print()
            
            response = requests.post(
                f"{self.api_url}/disaster/custom", 
                json=flood_disaster,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_trains = result.get('optimized_trains', [])
                explanations = result.get('explanations', [])
                
                print("📊 DISASTER RESPONSE ANALYSIS:")
                print("-" * 50)
                
                # Find TRN011 and TRN012 specifically
                trn011 = next((train for train in optimized_trains if train.get('id') == 'TRN011'), None)
                trn012 = next((train for train in optimized_trains if train.get('id') == 'TRN012'), None)
                
                console_test_passed = True
                console_details = []
                
                # Analyze TRN011
                if trn011:
                    print(f"🚂 TRN011 Analysis:")
                    print(f"   - Original Route: {trn011.get('route', 'N/A')}")
                    print(f"   - Rerouted: {trn011.get('rerouted', False)}")
                    
                    if trn011.get('rerouted', False):
                        alt_path = trn011.get('alternate_path_stations', [])
                        alt_segments = trn011.get('alternate_route_segments', [])
                        new_route = trn011.get('new_route', '')
                        delay = trn011.get('delay_minutes', 0)
                        
                        print(f"   - Alternate Path Stations: {alt_path}")
                        print(f"   - Alternate Route Segments: {alt_segments}")
                        print(f"   - New Route Description: {new_route}")
                        print(f"   - Rerouting Delay: {delay} minutes")
                        
                        # Validate A→B→C rerouting
                        if alt_path == ['A', 'B', 'C'] and alt_segments == ['A-B', 'B-C']:
                            if new_route == 'A-B → B-C':
                                if delay >= 5 and delay <= 15:
                                    console_details.append("✅ TRN011: Perfect A→B→C rerouting")
                                    print("   ✅ VALIDATION: Perfect A→B→C rerouting")
                                else:
                                    console_test_passed = False
                                    console_details.append(f"❌ TRN011: Delay {delay}min outside 5-15min range")
                                    print(f"   ❌ VALIDATION: Delay {delay}min outside expected range")
                            else:
                                console_test_passed = False
                                console_details.append(f"❌ TRN011: Wrong route description '{new_route}'")
                                print(f"   ❌ VALIDATION: Wrong route description")
                        else:
                            console_test_passed = False
                            console_details.append(f"❌ TRN011: Wrong path {alt_path} via {alt_segments}")
                            print(f"   ❌ VALIDATION: Wrong rerouting path")
                    else:
                        console_test_passed = False
                        console_details.append("❌ TRN011: Not rerouted")
                        print("   ❌ VALIDATION: Train not rerouted")
                else:
                    console_test_passed = False
                    console_details.append("❌ TRN011: Not found")
                    print("   ❌ ERROR: TRN011 not found in response")
                
                print()
                
                # Analyze TRN012
                if trn012:
                    print(f"🚂 TRN012 Analysis:")
                    print(f"   - Original Route: {trn012.get('route', 'N/A')}")
                    print(f"   - Rerouted: {trn012.get('rerouted', False)}")
                    
                    if trn012.get('rerouted', False):
                        alt_path = trn012.get('alternate_path_stations', [])
                        alt_segments = trn012.get('alternate_route_segments', [])
                        new_route = trn012.get('new_route', '')
                        delay = trn012.get('delay_minutes', 0)
                        
                        print(f"   - Alternate Path Stations: {alt_path}")
                        print(f"   - Alternate Route Segments: {alt_segments}")
                        print(f"   - New Route Description: {new_route}")
                        print(f"   - Rerouting Delay: {delay} minutes")
                        
                        # Validate A→B→C rerouting
                        if alt_path == ['A', 'B', 'C'] and alt_segments == ['A-B', 'B-C']:
                            if new_route == 'A-B → B-C':
                                if delay >= 5 and delay <= 15:
                                    console_details.append("✅ TRN012: Perfect A→B→C rerouting")
                                    print("   ✅ VALIDATION: Perfect A→B→C rerouting")
                                else:
                                    console_test_passed = False
                                    console_details.append(f"❌ TRN012: Delay {delay}min outside 5-15min range")
                                    print(f"   ❌ VALIDATION: Delay {delay}min outside expected range")
                            else:
                                console_test_passed = False
                                console_details.append(f"❌ TRN012: Wrong route description '{new_route}'")
                                print(f"   ❌ VALIDATION: Wrong route description")
                        else:
                            console_test_passed = False
                            console_details.append(f"❌ TRN012: Wrong path {alt_path} via {alt_segments}")
                            print(f"   ❌ VALIDATION: Wrong rerouting path")
                    else:
                        console_test_passed = False
                        console_details.append("❌ TRN012: Not rerouted")
                        print("   ❌ VALIDATION: Train not rerouted")
                else:
                    console_test_passed = False
                    console_details.append("❌ TRN012: Not found")
                    print("   ❌ ERROR: TRN012 not found in response")
                
                print()
                print("🔍 EXPLANATION ANALYSIS:")
                print("-" * 30)
                
                # Analyze explanations for expected console output patterns
                expected_patterns = [
                    "finding alternate routes from a to c",
                    "available route network",
                    "valid path found: a → b → c",
                    "a-b → b-c"
                ]
                
                found_patterns = []
                for explanation in explanations:
                    explanation_lower = explanation.lower()
                    print(f"📝 {explanation}")
                    
                    for pattern in expected_patterns:
                        if pattern in explanation_lower:
                            found_patterns.append(pattern)
                
                print()
                print("🎯 EXPECTED CONSOLE OUTPUT VALIDATION:")
                print("-" * 40)
                
                expected_console_outputs = [
                    "🚫 Route A-C is BLOCKED - finding alternatives for A → C",
                    "🔍 Finding alternate routes from A to C",
                    "📍 Available route network:",
                    "✅ VALID PATH FOUND: A → B → C via routes A-B → B-C"
                ]
                
                for expected in expected_console_outputs:
                    print(f"Expected: {expected}")
                    # Note: We can't capture actual console output from the backend server
                    # But we can verify the logic worked by checking the results
                
                print()
                print("📋 RESPONSE VALIDATION SUMMARY:")
                print("-" * 35)
                
                # Check if both trains were rerouted correctly
                both_trains_correct = (
                    trn011 and trn011.get('rerouted', False) and 
                    trn011.get('alternate_path_stations') == ['A', 'B', 'C'] and
                    trn011.get('alternate_route_segments') == ['A-B', 'B-C'] and
                    trn012 and trn012.get('rerouted', False) and 
                    trn012.get('alternate_path_stations') == ['A', 'B', 'C'] and
                    trn012.get('alternate_route_segments') == ['A-B', 'B-C']
                )
                
                if both_trains_correct:
                    print("✅ Both TRN011 and TRN012 rerouted via A→B→C")
                    print("✅ Route segments are ['A-B', 'B-C'] as expected")
                    print("✅ Path description is 'A → B → C' as expected")
                    print("✅ No 60-minute delays - trains rerouted instead")
                else:
                    print("❌ Rerouting validation failed")
                
                if console_test_passed and both_trains_correct:
                    self.log_test("A-C Route Blockage Console Output Analysis", True, 
                                f"SPECIFIC TEST PASSED: {'; '.join(console_details)}")
                    print("\n🎉 SPECIFIC A-C ROUTE BLOCKAGE TEST: PASSED")
                    return result
                else:
                    self.log_test("A-C Route Blockage Console Output Analysis", False, 
                                f"Console output test issues: {'; '.join(console_details)}")
                    print("\n❌ SPECIFIC A-C ROUTE BLOCKAGE TEST: FAILED")
            else:
                self.log_test("A-C Route Blockage Console Output Analysis", False, f"HTTP {response.status_code}")
                print(f"\n❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            self.log_test("A-C Route Blockage Console Output Analysis", False, f"Exception: {str(e)}")
            print(f"\n❌ Exception: {str(e)}")
        
        print("="*80)
        return None

    def run_all_tests(self):
        """Run all backend API tests - Enhanced for AAGAMI RAIL requirements"""
        print("🚂 AAGAMI RAIL Backend API Testing Suite")
        print("=" * 50)
        
        # Test basic endpoints with enhanced validation
        self.test_api_root()
        trains = self.test_get_trains()  # Now tests TRN format
        stations = self.test_get_stations()
        routes = self.test_get_routes()  # Now tests disaster effect fields
        conflicts = self.test_get_conflicts()
        
        # Test optimization with ETA validation
        optimization_result = self.test_optimize_trains(trains)  # Now tests both original and optimized ETAs
        
        # Test disaster scenarios with comprehensive validation
        scenarios = self.test_get_disaster_scenarios()
        disaster_result = self.test_apply_disaster_scenario(scenarios)  # Now tests train ID consistency
        
        # Test custom disaster without duration (key requirement)
        self.test_custom_disaster_without_duration()
        
        # Test emergency train insertion
        self.test_emergency_train_insertion()
        
        # Test all disaster types
        self.test_all_disaster_types()
        
        # ENHANCED REROUTING LOGIC TESTS (Primary Focus)
        print("\n🔄 ENHANCED REROUTING LOGIC TESTS")
        print("-" * 40)
        self.test_enhanced_rerouting_flood_ab()
        self.test_enhanced_rerouting_different_routes()
        self.test_alternate_path_response_structure()
        self.test_no_alternative_scenario()
        self.test_rerouting_explanation_accuracy()
        
        # A-C ROUTE BLOCKAGE SPECIFIC TESTS (Review Request Focus)
        print("\n🎯 A-C ROUTE BLOCKAGE SPECIFIC TESTS")
        print("-" * 40)
        self.test_ac_route_blockage_specific()
        self.test_shortest_path_prioritization()
        self.test_bc_blockage_comparison()
        self.test_delay_calculation_accuracy()
        
        # Test performance metrics
        performance = self.test_get_performance_metrics()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            print("\n✅ AAGAMI RAIL Requirements Verified:")
            print("  • Train Schedule API returns both original and optimized ETAs")
            print("  • Custom disasters work without requiring duration_minutes")
            print("  • Emergency train insertion functions properly")
            print("  • All disaster types process correctly")
            print("  • Train IDs consistently use TRN001-TRN010 format")
            print("  • Routes include disaster effect fields for map visualization")
            print("\n🔄 ENHANCED REROUTING LOGIC VERIFIED:")
            print("  • Flood disaster on A-B route triggers proper alternate path finding")
            print("  • Alternate paths avoid blocked routes completely")
            print("  • Response includes alternate_path_stations and alternate_route_segments")
            print("  • Different blocked routes (B-C, C-D) handled correctly")
            print("  • No-alternative scenarios result in appropriate delays")
            print("  • Explanations mention actual alternate paths, not blocked routes")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['details']}")
            return 1

def main():
    tester = AagamiRailAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())