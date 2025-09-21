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