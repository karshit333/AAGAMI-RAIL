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
    def __init__(self, base_url="https://aagami-rail.preview.emergentagent.com"):
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
        """Test GET /api/trains endpoint"""
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
                        if priorities.issubset(expected_priorities):
                            self.log_test("Get Trains Endpoint", True, f"Retrieved {len(trains)} trains")
                            return trains
                        else:
                            self.log_test("Get Trains Endpoint", False, f"Invalid priorities: {priorities}")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_train]
                        self.log_test("Get Trains Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Trains Endpoint", False, f"Expected 10 trains, got {len(trains) if isinstance(trains, list) else 'non-list'}")
            else:
                self.log_test("Get Trains Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Trains Endpoint", False, f"Exception: {str(e)}")
        
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
        """Test GET /api/routes endpoint"""
        try:
            response = requests.get(f"{self.api_url}/routes", timeout=10)
            success = response.status_code == 200
            
            if success:
                routes = response.json()
                if isinstance(routes, list) and len(routes) == 5:
                    # Validate route structure
                    required_fields = ['id', 'stations', 'path']
                    first_route = routes[0]
                    
                    if all(field in first_route for field in required_fields):
                        # Check route IDs
                        route_ids = set(route['id'] for route in routes)
                        expected_ids = {'A-B', 'B-C', 'C-D', 'D-E', 'B-E'}
                        if route_ids == expected_ids:
                            self.log_test("Get Routes Endpoint", True, f"Retrieved {len(routes)} routes")
                            return routes
                        else:
                            self.log_test("Get Routes Endpoint", False, f"Invalid route IDs: {route_ids}")
                    else:
                        missing_fields = [f for f in required_fields if f not in first_route]
                        self.log_test("Get Routes Endpoint", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Routes Endpoint", False, f"Expected 5 routes, got {len(routes) if isinstance(routes, list) else 'non-list'}")
            else:
                self.log_test("Get Routes Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Routes Endpoint", False, f"Exception: {str(e)}")
        
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
        """Test POST /api/optimize endpoint"""
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
                    
                    # Validate KPIs structure
                    required_kpi_fields = ['total_trains', 'avg_delay_minutes', 'throughput_percentage', 'on_time_trains']
                    if all(field in kpis for field in required_kpi_fields):
                        # Check if optimization actually worked
                        total_trains = kpis['total_trains']
                        on_time_trains = kpis['on_time_trains']
                        avg_delay = kpis['avg_delay_minutes']
                        throughput = kpis['throughput_percentage']
                        
                        if total_trains == 10:  # Expected number of trains
                            self.log_test("Optimize Trains Endpoint", True, 
                                        f"KPIs: {total_trains} trains, {on_time_trains} on-time, {avg_delay}min avg delay, {throughput}% throughput")
                            return optimization_result
                        else:
                            self.log_test("Optimize Trains Endpoint", False, f"Expected 10 trains, got {total_trains}")
                    else:
                        missing_kpi_fields = [f for f in required_kpi_fields if f not in kpis]
                        self.log_test("Optimize Trains Endpoint", False, f"Missing KPI fields: {missing_kpi_fields}")
                else:
                    missing_fields = [f for f in required_fields if f not in optimization_result]
                    self.log_test("Optimize Trains Endpoint", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Optimize Trains Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Optimize Trains Endpoint", False, f"Exception: {str(e)}")
        
        return None

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚂 AAGAMI RAIL Backend API Testing Suite")
        print("=" * 50)
        
        # Test basic endpoints
        self.test_api_root()
        trains = self.test_get_trains()
        stations = self.test_get_stations()
        routes = self.test_get_routes()
        conflicts = self.test_get_conflicts()
        
        # Test optimization with sample data
        optimization_result = self.test_optimize_trains(trains)
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
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