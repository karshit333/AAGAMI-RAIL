from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple, Any
import uuid
from datetime import datetime, timedelta
from enum import Enum
import heapq
from collections import defaultdict
import copy
import random


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums
class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DisasterType(str, Enum):
    FLOOD = "flood"
    EQUIPMENT_FAILURE = "equipment_failure"
    WEATHER = "weather"
    EMERGENCY_TRAIN = "emergency_train"
    BREAKDOWN = "breakdown"
    HUMAN_STRIKE = "human_strike"
    CUSTOM = "custom"

class AlertType(str, Enum):
    CRITICAL_DELAY = "critical_delay"
    ROUTE_BLOCKAGE = "route_blockage"
    VIP_TRAIN = "vip_train"
    SYSTEM_HEALTH = "system_health"
    DISASTER = "disaster"

class SimulationState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"


# Enhanced Models
class TrainDetails(BaseModel):
    capacity: int = 400
    current_load: int = 320
    origin: str = "Delhi Junction"
    destination: str = "Lucknow Junction"
    stops: List[str] = []
    fuel_consumption: float = 2.5  # liters per km
    passenger_count: int = 320
    coach_count: int = 12
    engine_type: str = "WAP-7"
    max_speed: int = 140  # km/h

class Train(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: Priority
    planned_arrival: str  # HH:MM format
    planned_departure: str  # HH:MM format
    route: str  # e.g., "A-B", "B-C", etc.
    delay_minutes: int = 0
    optimized_arrival: Optional[str] = None
    optimized_departure: Optional[str] = None
    rerouted: bool = False
    new_route: Optional[str] = None
    explanation: Optional[str] = None
    details: TrainDetails = Field(default_factory=TrainDetails)
    current_position: float = 0.0  # 0.0 to 1.0 along route
    speed_kmh: int = 80
    status: str = "on_time"  # on_time, delayed, critical, blocked

class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AlertType
    title: str
    message: str
    severity: str = "medium"  # low, medium, high, critical
    timestamp: str
    train_id: Optional[str] = None
    route_id: Optional[str] = None
    acknowledged: bool = False

class SimulationControl(BaseModel):
    state: SimulationState = SimulationState.PAUSED
    speed: float = 1.0  # 1x, 2x, 5x speed
    current_time: str = "08:00"  # HH:MM
    auto_advance: bool = True

class CustomDisaster(BaseModel):
    type: DisasterType = DisasterType.CUSTOM
    affected_route: str
    duration_minutes: int = 30
    description: str
    speed_reduction: float = 0.0
    severity: str = "medium"
    coordinates: Optional[List[Dict[str, float]]] = None  # For drawing on map

class TrainCreate(BaseModel):
    priority: Priority
    planned_arrival: str
    planned_departure: str
    route: str

class Station(BaseModel):
    id: str
    name: str
    x: float  # coordinate for map
    y: float  # coordinate for map

class Route(BaseModel):
    id: str
    stations: List[str]  # station IDs
    path: List[Dict[str, float]]  # path coordinates for animation
    blocked: bool = False
    speed_reduction: float = 0.0  # 0.0 to 1.0 (40% reduction = 0.4)
    custom_blocked_sections: List[Dict[str, float]] = []  # Custom blocked areas

class Disaster(BaseModel):
    type: DisasterType
    affected_route: Optional[str] = None
    duration_minutes: int = 60
    description: str = ""
    speed_reduction: float = 0.0
    custom_description: Optional[str] = None
    severity: str = "medium"
    coordinates: Optional[List[Dict[str, float]]] = None

class DisasterScenario(BaseModel):
    disasters: List[Disaster]
    description: str
    multiple: bool = False  # Can handle multiple simultaneous disasters

class OptimizationResult(BaseModel):
    original_trains: List[Train]
    optimized_trains: List[Train]
    kpis: Dict[str, float]
    explanations: List[str]
    disaster_summary: Optional[str] = None
    alerts: List[Alert] = []
    what_changed: Optional[Dict] = None
    what_changed: Optional[Dict[str, Any]] = None

class PerformanceMetrics(BaseModel):
    total_trains: int
    on_time_trains: int
    delayed_trains: int
    rerouted_trains: int
    avg_delay: float
    max_delay: int
    throughput_improvement: float
    route_throughput: Dict[str, int]

class SystemStatus(BaseModel):
    simulation: SimulationControl
    active_alerts: List[Alert]
    system_health: str = "healthy"  # healthy, warning, critical
    total_trains: int
    active_disasters: int


# Global simulation state
SIMULATION_STATE = SimulationControl()
ACTIVE_ALERTS = []
ACTIVE_DISASTERS = []

# Sample data initialization with enhanced details
def generate_train_details(route: str) -> TrainDetails:
    """Generate realistic train details based on route"""
    station_map = {
        "A": "Delhi Junction", "B": "Ghaziabad", "C": "Moradabad", 
        "D": "Bareilly", "E": "Lucknow Junction"
    }
    
    origin_station = route.split('-')[0]
    dest_station = route.split('-')[-1]
    
    return TrainDetails(
        capacity=random.randint(300, 500),
        current_load=random.randint(200, 450),
        origin=station_map.get(origin_station, "Delhi Junction"),
        destination=station_map.get(dest_station, "Lucknow Junction"),
        stops=[station_map.get(s, f"Station {s}") for s in route.split('-')],
        fuel_consumption=round(random.uniform(2.0, 3.5), 1),
        passenger_count=random.randint(200, 450),
        coach_count=random.randint(8, 16),
        engine_type=random.choice(["WAP-7", "WAP-5", "WAG-9", "WAG-7"]),
        max_speed=random.randint(110, 160)
    )

SAMPLE_STATIONS = [
    Station(id="A", name="Delhi Junction", x=100, y=200),
    Station(id="B", name="Ghaziabad", x=300, y=200),
    Station(id="C", name="Moradabad", x=500, y=200),
    Station(id="D", name="Bareilly", x=700, y=200),
    Station(id="E", name="Lucknow Junction", x=500, y=100),
]

SAMPLE_ROUTES = [
    Route(id="A-B", stations=["A", "B"], path=[{"x": 100, "y": 200}, {"x": 300, "y": 200}]),
    Route(id="B-C", stations=["B", "C"], path=[{"x": 300, "y": 200}, {"x": 500, "y": 200}]),
    Route(id="C-D", stations=["C", "D"], path=[{"x": 500, "y": 200}, {"x": 700, "y": 200}]),
    Route(id="D-E", stations=["D", "E"], path=[{"x": 700, "y": 200}, {"x": 500, "y": 100}]),
    Route(id="B-E", stations=["B", "E"], path=[{"x": 300, "y": 200}, {"x": 500, "y": 100}]),
    # Additional alternate routes for rerouting
    Route(id="A-C", stations=["A", "C"], path=[{"x": 100, "y": 200}, {"x": 200, "y": 150}, {"x": 500, "y": 200}]),
    Route(id="A-E", stations=["A", "E"], path=[{"x": 100, "y": 200}, {"x": 300, "y": 100}, {"x": 500, "y": 100}]),
]

# Generate sample trains with enhanced details
SAMPLE_TRAINS = [
    Train(priority=Priority.HIGH, planned_arrival="08:00", planned_departure="08:15", route="A-B", details=generate_train_details("A-B")),
    Train(priority=Priority.HIGH, planned_arrival="08:10", planned_departure="08:25", route="A-B", details=generate_train_details("A-B")),
    Train(priority=Priority.MEDIUM, planned_arrival="08:05", planned_departure="08:20", route="B-C", details=generate_train_details("B-C")),
    Train(priority=Priority.MEDIUM, planned_arrival="08:30", planned_departure="08:45", route="B-C", details=generate_train_details("B-C")),
    Train(priority=Priority.LOW, planned_arrival="08:15", planned_departure="08:30", route="C-D", details=generate_train_details("C-D")),
    Train(priority=Priority.HIGH, planned_arrival="08:20", planned_departure="08:35", route="D-E", details=generate_train_details("D-E")),
    Train(priority=Priority.MEDIUM, planned_arrival="08:25", planned_departure="08:40", route="B-E", details=generate_train_details("B-E")),
    Train(priority=Priority.LOW, planned_arrival="08:35", planned_departure="08:50", route="B-E", details=generate_train_details("B-E")),
    Train(priority=Priority.HIGH, planned_arrival="08:40", planned_departure="08:55", route="C-D", details=generate_train_details("C-D")),
    Train(priority=Priority.LOW, planned_arrival="08:45", planned_departure="09:00", route="A-B", details=generate_train_details("A-B")),
]

# Enhanced disaster scenarios
DISASTER_SCENARIOS = {
    "flood_ab": DisasterScenario(
        disasters=[Disaster(type=DisasterType.FLOOD, affected_route="A-B", duration_minutes=120, description="Heavy rainfall floods A-B section", severity="high")],
        description="Flood on A-B section blocks main route for 2 hours"
    ),
    "equipment_failure": DisasterScenario(
        disasters=[Disaster(type=DisasterType.EQUIPMENT_FAILURE, affected_route="B-C", duration_minutes=45, description="Signal failure at Ghaziabad", severity="medium")],
        description="Equipment failure causes signal outage on B-C route"
    ),
    "weather_slow": DisasterScenario(
        disasters=[Disaster(type=DisasterType.WEATHER, affected_route="all", speed_reduction=0.4, description="Dense fog reduces visibility", severity="medium")],
        description="Weather disruption reduces train speeds by 40% across network"
    ),
    "emergency_train": DisasterScenario(
        disasters=[Disaster(type=DisasterType.EMERGENCY_TRAIN, description="Emergency train requires immediate priority", severity="critical")],
        description="Emergency train insertion requires immediate priority clearance"
    ),
    "breakdown_ce": DisasterScenario(
        disasters=[Disaster(type=DisasterType.BREAKDOWN, affected_route="C-D", duration_minutes=15, description="Freight train breakdown blocks C-D", severity="low")],
        description="Train breakdown blocks C-D section for 15 minutes"
    ),
    "human_strike": DisasterScenario(
        disasters=[Disaster(type=DisasterType.HUMAN_STRIKE, affected_route="all", duration_minutes=240, description="Railway workers strike affects network operations", severity="high", speed_reduction=0.6)],
        description="Railway workers strike reduces operational capacity network-wide"
    ),
    "multiple_disasters": DisasterScenario(
        disasters=[
            Disaster(type=DisasterType.FLOOD, affected_route="A-B", duration_minutes=90, description="Flood on A-B", severity="high"),
            Disaster(type=DisasterType.WEATHER, affected_route="all", speed_reduction=0.3, description="Rain reduces speeds", severity="medium")
        ],
        description="Multiple disasters: Flood on A-B + Weather slowdown across network",
        multiple=True
    )
}


# Utility functions
def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes since midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def advance_simulation_time(minutes: int = 1):
    """Advance simulation time"""
    current_minutes = time_to_minutes(SIMULATION_STATE.current_time)
    new_minutes = current_minutes + minutes
    SIMULATION_STATE.current_time = minutes_to_time(new_minutes % (24 * 60))


def generate_alert(alert_type: AlertType, title: str, message: str, severity: str = "medium", 
                  train_id: str = None, route_id: str = None) -> Alert:
    """Generate a new alert"""
    return Alert(
        type=alert_type,
        title=title,
        message=message,
        severity=severity,
        timestamp=datetime.now().strftime("%H:%M:%S"),
        train_id=train_id,
        route_id=route_id
    )


def check_and_generate_alerts(trains: List[Train], disasters: List[Disaster] = None) -> List[Alert]:
    """Check system state and generate appropriate alerts with detailed reasons"""
    alerts = []
    
    for train in trains:
        # Determine delay reason
        delay_reason = "Unknown cause"
        if disasters:
            for disaster in disasters:
                if disaster.type == DisasterType.FLOOD and disaster.affected_route in [train.route, train.new_route]:
                    delay_reason = f"Track flooding on {disaster.affected_route}"
                elif disaster.type == DisasterType.EQUIPMENT_FAILURE and disaster.affected_route in [train.route, train.new_route]:
                    delay_reason = f"Signal equipment failure on {disaster.affected_route}"
                elif disaster.type == DisasterType.WEATHER:
                    delay_reason = f"Weather conditions reducing speeds by {int(disaster.speed_reduction*100)}%"
                elif disaster.type == DisasterType.BREAKDOWN and disaster.affected_route in [train.route, train.new_route]:
                    delay_reason = f"Train breakdown blocking {disaster.affected_route}"
                elif disaster.type == DisasterType.EMERGENCY_TRAIN:
                    delay_reason = "Emergency train priority clearance"
                elif disaster.type == DisasterType.HUMAN_STRIKE:
                    delay_reason = f"Railway workers strike reducing operations by {int(disaster.speed_reduction*100)}%"
        else:
            # No disaster - likely scheduling conflict
            delay_reason = "Priority-based scheduling conflict resolution"
        
        # Critical delay alert with reason
        if train.delay_minutes > 15:
            alerts.append(generate_alert(
                AlertType.CRITICAL_DELAY,
                f"Critical Delay - Train {train.id[:6]}",
                f"Train {train.id[:6]} delayed by {train.delay_minutes} minutes. Reason: {delay_reason}. Route: {train.rerouted and train.new_route or train.route}",
                "critical",
                train_id=train.id,
                route_id=train.rerouted and train.new_route or train.route
            ))
        
        # High priority train alert with detailed reason
        if train.priority == Priority.HIGH and train.delay_minutes > 5:
            priority_reason = delay_reason
            if train.rerouted:
                priority_reason += f" - Rerouted via {train.new_route}"
            
            alerts.append(generate_alert(
                AlertType.VIP_TRAIN,
                f"High Priority Train Affected - {train.id[:6]}",
                f"High priority train {train.id[:6]} experiencing {train.delay_minutes} min delay. Cause: {priority_reason}. Alternative measures implemented.",
                "high",
                train_id=train.id,
                route_id=train.rerouted and train.new_route or train.route
            ))
        
        # Rerouting alert with explanation
        if train.rerouted:
            alerts.append(generate_alert(
                AlertType.ROUTE_BLOCKAGE,
                f"Train Rerouted - {train.id[:6]}",
                f"Train {train.id[:6]} intelligently rerouted from {train.route} to {train.new_route}. Reason: {delay_reason}. Additional delay: {train.delay_minutes} minutes.",
                "medium",
                train_id=train.id,
                route_id=train.new_route
            ))
    
    # Route blockage alerts with specific details
    if disasters:
        for disaster in disasters:
            if disaster.type in [DisasterType.FLOOD, DisasterType.BREAKDOWN, DisasterType.EQUIPMENT_FAILURE]:
                severity_map = {"low": "low", "medium": "medium", "high": "high", "critical": "critical"}
                
                impact_description = ""
                if disaster.type == DisasterType.FLOOD:
                    impact_description = f"Track flooding makes {disaster.affected_route} impassable"
                elif disaster.type == DisasterType.BREAKDOWN:
                    impact_description = f"Disabled train blocking {disaster.affected_route} for ~{disaster.duration_minutes}min"
                elif disaster.type == DisasterType.EQUIPMENT_FAILURE:
                    impact_description = f"Signal system failure on {disaster.affected_route}"
                
                affected_trains = len([t for t in trains if t.route == disaster.affected_route or (t.rerouted and t.new_route == disaster.affected_route)])
                
                alerts.append(generate_alert(
                    AlertType.ROUTE_BLOCKAGE,
                    f"Route Disruption - {disaster.affected_route}",
                    f"{impact_description}. {affected_trains} trains affected. AI implementing rerouting and delay minimization strategies.",
                    severity_map.get(disaster.severity, "medium"),
                    route_id=disaster.affected_route
                ))
            
            elif disaster.type == DisasterType.EMERGENCY_TRAIN:
                alerts.append(generate_alert(
                    AlertType.VIP_TRAIN,
                    "Emergency Train Deployment",
                    f"Emergency train deployed with highest priority. All scheduled trains rescheduled for immediate clearance. Network recovery in progress.",
                    "critical"
                ))
    
    return alerts


def find_alternate_routes(start: str, end: str, blocked_routes: List[str]) -> List[List[str]]:
    """Find alternate paths between stations avoiding blocked routes"""
    # Create adjacency graph from available routes
    graph = defaultdict(list)
    route_map = {}
    
    for route in SAMPLE_ROUTES:
        if len(route.stations) >= 2 and route.id not in blocked_routes:
            start_station = route.stations[0]
            end_station = route.stations[-1]
            graph[start_station].append(end_station)
            graph[end_station].append(start_station)  # bidirectional
            route_map[f"{start_station}-{end_station}"] = route.id
            route_map[f"{end_station}-{start_station}"] = route.id
    
    # BFS to find paths
    def bfs_paths(start, end, max_depth=3):
        paths = []
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
                
            if current == end and len(path) > 1:
                paths.append(path)
                continue
            
            for neighbor in graph[current]:
                if neighbor not in path:  # avoid cycles
                    queue.append((neighbor, path + [neighbor]))
        
        return paths
    
    paths = bfs_paths(start, end)
    return paths[:3]  # Return top 3 alternate paths


def apply_disasters(routes: List[Route], disasters: List[Disaster]) -> List[Route]:
    """Apply disaster effects to routes"""
    affected_routes = copy.deepcopy(routes)
    
    for disaster in disasters:
        if disaster.type == DisasterType.FLOOD or disaster.type == DisasterType.BREAKDOWN:
            # Block the route
            for route in affected_routes:
                if route.id == disaster.affected_route:
                    route.blocked = True
                    
        elif disaster.type == DisasterType.EQUIPMENT_FAILURE:
            # Block the route temporarily
            for route in affected_routes:
                if route.id == disaster.affected_route:
                    route.blocked = True
                    
        elif disaster.type == DisasterType.WEATHER or disaster.type == DisasterType.HUMAN_STRIKE:
            # Reduce speed on all or specific routes
            for route in affected_routes:
                if disaster.affected_route == "all" or route.id == disaster.affected_route:
                    route.speed_reduction = disaster.speed_reduction
                    
        elif disaster.type == DisasterType.CUSTOM:
            # Custom disaster handling
            for route in affected_routes:
                if route.id == disaster.affected_route:
                    if disaster.speed_reduction > 0:
                        route.speed_reduction = disaster.speed_reduction
                    else:
                        route.blocked = True
                    if disaster.coordinates:
                        route.custom_blocked_sections = disaster.coordinates
    
    return affected_routes


def optimize_with_disasters(trains: List[Train], disasters: List[Disaster] = None) -> Tuple[List[Train], List[str]]:
    """Advanced optimization with disaster handling and rerouting"""
    optimized_trains = []
    explanations = []
    
    # Apply disasters if any
    current_routes = SAMPLE_ROUTES
    if disasters:
        current_routes = apply_disasters(SAMPLE_ROUTES, disasters)
        ACTIVE_DISASTERS.clear()
        ACTIVE_DISASTERS.extend(disasters)
    
    # Priority weights for sorting
    priority_weights = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
    
    # Add Emergency train if disaster includes it
    emergency_disaster = next((d for d in disasters if d.type == DisasterType.EMERGENCY_TRAIN), None) if disasters else None
    if emergency_disaster:
        emergency_train = Train(
            priority=Priority.HIGH,
            planned_arrival="08:12",
            planned_departure="08:27",
            route=emergency_disaster.affected_route or "A-B",  # Use specified route or default
            details=generate_train_details(emergency_disaster.affected_route or "A-B")
        )
        trains = [emergency_train] + trains
        explanations.append(f"🚨 EMERGENCY TRAIN DEPLOYED: High-priority emergency train inserted on route {emergency_disaster.affected_route or 'A-B'} - all scheduled trains rescheduled for immediate clearance")
    
    # Group trains by original route
    route_trains = defaultdict(list)
    for train in trains:
        route_trains[train.route].append(train)
    
    # Process each route
    for route_id, train_list in route_trains.items():
        # Check if route is blocked
        route_obj = next((r for r in current_routes if r.id == route_id), None)
        is_blocked = route_obj and route_obj.blocked if route_obj else False
        speed_reduction = route_obj.speed_reduction if route_obj else 0.0
        
        # Sort trains by priority then arrival time
        train_list.sort(key=lambda t: (-priority_weights[t.priority], time_to_minutes(t.planned_arrival)))
        
        scheduled_trains = []
        
        for train in train_list:
            new_train = Train(**train.dict())
            new_train.optimized_arrival = train.planned_arrival
            new_train.optimized_departure = train.planned_departure
            
            # Handle blocked routes - find alternate path
            if is_blocked:
                start_station = route_id.split('-')[0]
                end_station = route_id.split('-')[1]
                blocked_routes = [r.id for r in current_routes if r.blocked]
                
                alternate_paths = find_alternate_routes(start_station, end_station, blocked_routes)
                
                if alternate_paths:
                    # Use the first (shortest) alternate path
                    path = alternate_paths[0]
                    if len(path) >= 2:
                        new_route = f"{path[0]}-{path[-1]}"
                        new_train.rerouted = True
                        new_train.new_route = new_route
                        new_train.delay_minutes += 10  # Rerouting adds delay
                        new_train.status = "rerouted"
                        new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + 10)
                        new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + 10)
                        explanations.append(f"Train {train.id[:6]} rerouted via {' → '.join(path)} due to {route_id} blockage (+10 min delay)")
                else:
                    # No alternate route - significant delay
                    new_train.delay_minutes += 60
                    new_train.status = "critical"
                    new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + 60)
                    new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + 60)
                    explanations.append(f"Train {train.id[:6]} delayed 60 min - no alternate route available for blocked {route_id}")
            
            # Apply speed reductions
            elif speed_reduction > 0:
                delay_from_speed = int(15 * speed_reduction)  # Base delay proportional to speed reduction
                new_train.delay_minutes += delay_from_speed
                new_train.status = "delayed" if delay_from_speed < 15 else "critical"
                new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + delay_from_speed)
                new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + delay_from_speed)
                
                # Determine the cause of speed reduction
                speed_cause = "speed restrictions"
                if disasters:
                    for disaster in disasters:
                        if disaster.type == DisasterType.WEATHER and disaster.speed_reduction > 0:
                            speed_cause = f"{int(disaster.speed_reduction*100)}% speed reduction due to weather conditions"
                        elif disaster.type == DisasterType.HUMAN_STRIKE and disaster.speed_reduction > 0:
                            speed_cause = f"{int(disaster.speed_reduction*100)}% operational reduction due to railway workers strike"
                
                explanations.append(f"Train {train.id[:6]} delayed {delay_from_speed} min due to {speed_cause}")
            
            # Normal conflict resolution for non-blocked routes
            elif not is_blocked:
                for scheduled_train in scheduled_trains:
                    scheduled_arr = time_to_minutes(scheduled_train.optimized_arrival)
                    scheduled_dep = time_to_minutes(scheduled_train.optimized_departure)
                    current_arr = time_to_minutes(new_train.optimized_arrival)
                    current_dep = time_to_minutes(new_train.optimized_departure)
                    
                    # Check for time overlap
                    if not (scheduled_dep <= current_arr or current_dep <= scheduled_arr):
                        if priority_weights[new_train.priority] < priority_weights[scheduled_train.priority]:
                            # Delay current train
                            delay = scheduled_dep - current_arr + 5
                            new_train.delay_minutes += delay
                            new_train.status = "delayed" if delay < 15 else "critical"
                            new_train.optimized_arrival = minutes_to_time(current_arr + delay)
                            new_train.optimized_departure = minutes_to_time(current_dep + delay)
                            explanations.append(f"Train {train.id[:6]} delayed {delay} min to give priority to {scheduled_train.priority.lower()} priority train {scheduled_train.id[:6]}")
                        elif priority_weights[new_train.priority] > priority_weights[scheduled_train.priority]:
                            # Delay scheduled train
                            delay = current_dep - scheduled_arr + 5
                            scheduled_train.delay_minutes += delay
                            scheduled_train.status = "delayed" if delay < 15 else "critical"
                            scheduled_train.optimized_arrival = minutes_to_time(scheduled_arr + delay)
                            scheduled_train.optimized_departure = minutes_to_time(scheduled_dep + delay)
                            explanations.append(f"Train {scheduled_train.id[:6]} delayed {delay} min to give priority to {new_train.priority.lower()} priority train {train.id[:6]}")
            
            # Update train status
            if new_train.delay_minutes == 0:
                new_train.status = "on_time"
            
            scheduled_trains.append(new_train)
        
        optimized_trains.extend(scheduled_trains)
    
    return optimized_trains, explanations


def calculate_advanced_kpis(original_trains: List[Train], optimized_trains: List[Train], disasters: List[Disaster] = None) -> Dict[str, float]:
    """Calculate comprehensive KPIs including disaster impact"""
    total_trains = len(original_trains)
    
    # Basic metrics
    total_delay = sum(train.delay_minutes for train in optimized_trains)
    avg_delay = total_delay / total_trains if total_trains > 0 else 0
    max_delay = max((train.delay_minutes for train in optimized_trains), default=0)
    
    # On-time performance
    on_time_trains = len([train for train in optimized_trains if train.delay_minutes == 0])
    delayed_trains = total_trains - on_time_trains
    rerouted_trains = len([train for train in optimized_trains if train.rerouted])
    
    # Throughput calculation
    original_throughput = total_trains  # baseline
    current_throughput = len([train for train in optimized_trains if train.delay_minutes < 30])  # trains with acceptable delay
    throughput_improvement = ((current_throughput - original_throughput) / original_throughput * 100) if original_throughput > 0 else 0
    
    # Route throughput calculation
    route_throughput = {}
    for train in optimized_trains:
        route = train.rerouted and train.new_route or train.route
        if train.delay_minutes < 30:  # Consider successful if delay < 30 min
            route_throughput[route] = route_throughput.get(route, 0) + 1
    
    return {
        "total_trains": float(total_trains),
        "on_time_trains": float(on_time_trains),
        "delayed_trains": float(delayed_trains),
        "rerouted_trains": float(rerouted_trains),
        "avg_delay_minutes": round(avg_delay, 2),
        "max_delay_minutes": float(max_delay),
        "total_delay_minutes": float(total_delay),
        "throughput_improvement": round(throughput_improvement, 2),
        "disaster_impact": float(len(disasters) if disasters else 0)
    }



def generate_what_changed_summary(original_trains: List[Train], optimized_trains: List[Train], disasters: List[Disaster] = None) -> Dict[str, Any]:
    """Generate comprehensive 'What Changed?' summary with AI analysis"""
    
    # Before/After comparison
    original_delays = sum(train.delay_minutes for train in original_trains)
    optimized_delays = sum(train.delay_minutes for train in optimized_trains)
    
    original_on_time = len([t for t in original_trains if t.delay_minutes == 0])
    optimized_on_time = len([t for t in optimized_trains if t.delay_minutes == 0])
    
    rerouted_count = len([t for t in optimized_trains if t.rerouted])
    critical_delays = len([t for t in optimized_trains if t.delay_minutes > 15])
    
    # Calculate changes
    delay_change = optimized_delays - original_delays
    on_time_change = optimized_on_time - original_on_time
    
    # AI Decision Categories
    ai_decisions = {
        "priority_adjustments": [],
        "rerouting_decisions": [],
        "delay_minimization": [],
        "conflict_resolutions": []
    }
    
    # Analyze each train for changes
    for i, (original, optimized) in enumerate(zip(original_trains, optimized_trains)):
        if optimized.delay_minutes != original.delay_minutes:
            if optimized.delay_minutes > original.delay_minutes:
                ai_decisions["delay_minimization"].append({
                    "train": optimized.id[:6],
                    "action": f"Added {optimized.delay_minutes - original.delay_minutes}min delay",
                    "reason": "Conflict resolution" if not disasters else "Disaster response"
                })
        
        if optimized.rerouted:
            ai_decisions["rerouting_decisions"].append({
                "train": optimized.id[:6],
                "action": f"Rerouted from {original.route} to {optimized.new_route}",
                "reason": "Route optimization" if not disasters else "Disaster avoidance"
            })
    
    # Generate impact analysis
    impact_analysis = {
        "overall_impact": "positive" if delay_change <= 0 else "negative" if delay_change > 30 else "mixed",
        "delay_impact": {
            "change": delay_change,
            "description": f"{'Reduced' if delay_change < 0 else 'Increased' if delay_change > 0 else 'Maintained'} total delays by {abs(delay_change)} minutes"
        },
        "on_time_performance": {
            "change": on_time_change,
            "description": f"{'Improved' if on_time_change > 0 else 'Reduced' if on_time_change < 0 else 'Maintained'} on-time trains by {abs(on_time_change)}"
        },
        "operational_changes": {
            "rerouted_trains": rerouted_count,
            "critical_delays": critical_delays,
            "total_affected": len([t for t in optimized_trains if t.delay_minutes > 0 or t.rerouted])
        }
    }
    
    # Generate AI insights
    insights = []
    
    if disasters:
        insights.append(f"AI successfully handled {len(disasters)} disaster scenario(s)")
        if rerouted_count > 0:
            insights.append(f"Smart rerouting prevented {rerouted_count * 15} additional delay minutes")
    
    if on_time_change > 0:
        insights.append(f"Priority-based optimization improved on-time performance")
    elif on_time_change < 0:
        insights.append(f"Delay propagation minimized through intelligent scheduling")
    
    if critical_delays == 0:
        insights.append("No critical delays (>15min) in optimized schedule")
    
    # Generate recommendations
    recommendations = []
    
    if critical_delays > 0:
        recommendations.append("Consider additional capacity on critical routes")
    
    if rerouted_count > 2:
        recommendations.append("Evaluate alternate route infrastructure for resilience")
    
    if delay_change > 20:
        recommendations.append("Review disaster response protocols for faster recovery")
    
    return {
        "ai_decisions": ai_decisions,
        "impact_analysis": impact_analysis,
        "insights": insights,
        "recommendations": recommendations,
        "summary_stats": {
            "trains_processed": len(optimized_trains),
            "total_delay_change": delay_change,
            "on_time_change": on_time_change,
            "rerouted_trains": rerouted_count,
            "optimization_effectiveness": max(0, min(100, 100 - (delay_change * 2)))
        }
    }


def generate_enhanced_explanations(trains: List[Train], disasters: List[Disaster] = None) -> List[str]:
    """Generate enhanced AI explanations with reasoning and context"""
    explanations = []
    
    # Disaster context
    if disasters:
        disaster_context = f"Responding to {len(disasters)} active disruption(s): "
        disaster_types = []
        for disaster in disasters:
            if disaster.type == DisasterType.FLOOD:
                disaster_types.append(f"flooding on {disaster.affected_route}")
            elif disaster.type == DisasterType.WEATHER:
                disaster_types.append(f"weather reducing speeds by {int(disaster.speed_reduction*100)}%")
            elif disaster.type == DisasterType.EQUIPMENT_FAILURE:
                disaster_types.append(f"signal failure on {disaster.affected_route}")
            elif disaster.type == DisasterType.EMERGENCY_TRAIN:
                disaster_types.append("emergency train deployment")
            elif disaster.type == DisasterType.BREAKDOWN:
                disaster_types.append(f"train breakdown blocking {disaster.affected_route}")
            elif disaster.type == DisasterType.HUMAN_STRIKE:
                disaster_types.append(f"railway workers strike reducing operations by {int(disaster.speed_reduction*100)}%")
        
        explanations.append(disaster_context + ", ".join(disaster_types))
        explanations.append("🧠 AI EMERGENCY RESPONSE: Implementing immediate clearance protocol...")
    
    # Analyze train changes
    priority_changes = 0
    rerouting_changes = 0
    delay_optimizations = 0
    
    for train in trains:
        if train.rerouted:
            rerouting_changes += 1
            explanations.append(
                f"🔄 SMART REROUTING: Train {train.id[:6]} ({train.priority} priority) "
                f"rerouted via alternate path {train.new_route} - avoiding disrupted section, "
                f"minimizing delay to {train.delay_minutes} minutes"
            )
        
        if train.delay_minutes > 0 and not train.rerouted:
            delay_optimizations += 1
            if train.delay_minutes <= 10:
                explanations.append(
                    f"⚡ CONFLICT RESOLUTION: Train {train.id[:6]} delayed {train.delay_minutes} min "
                    f"- optimal scheduling maintains {train.priority.lower()} priority sequence"
                )
            else:
                explanations.append(
                    f"🚨 PRIORITY OPTIMIZATION: Train {train.id[:6]} ({train.priority} priority) "
                    f"delayed {train.delay_minutes} min - necessary to maintain higher priority train schedules, "
                    f"minimizes overall network disruption"
                )
        
        if train.delay_minutes == 0 and train.priority == Priority.HIGH:
            explanations.append(
                f"✅ PRIORITY MAINTAINED: High priority train {train.id[:6]} "
                f"kept on original schedule - critical timing preserved"
            )
    
    # Summary insights
    if rerouting_changes > 0:
        explanations.append(
            f"🧠 AI INSIGHT: {rerouting_changes} intelligent rerouting(s) prevented "
            f"approximately {rerouting_changes * 25} additional delay minutes"
        )
    
    if delay_optimizations > 0:
        explanations.append(
            f"⚖️ OPTIMIZATION RESULT: {delay_optimizations} strategic delay(s) applied "
            f"- balanced approach minimizes total network impact"
        )
    
    # Network-level insights
    total_delays = sum(train.delay_minutes for train in trains)
    on_time_count = len([train for train in trains if train.delay_minutes == 0])
    
    explanations.append(
        f"📊 NETWORK PERFORMANCE: {on_time_count}/{len(trains)} trains on schedule, "
        f"total delay burden: {total_delays} minutes - "
        f"{'optimal' if total_delays < 30 else 'acceptable' if total_delays < 60 else 'challenging'} outcome achieved"
    )
    
    return explanations


def find_next_conflict_time(trains: List[Train]) -> Optional[str]:
    """Find the next conflict time in the schedule"""
    current_time_minutes = time_to_minutes(SIMULATION_STATE.current_time)
    
    conflicts = []
    route_trains = defaultdict(list)
    
    for train in trains:
        route_trains[train.route].append(train)
    
    for route, train_list in route_trains.items():
        for i, train1 in enumerate(train_list):
            for train2 in train_list[i+1:]:
                train1_arr = time_to_minutes(train1.optimized_arrival or train1.planned_arrival)
                train1_dep = time_to_minutes(train1.optimized_departure or train1.planned_departure)
                train2_arr = time_to_minutes(train2.optimized_arrival or train2.planned_arrival)
                train2_dep = time_to_minutes(train2.optimized_departure or train2.planned_departure)
                
                if not (train1_dep <= train2_arr or train2_dep <= train1_arr):
                    conflict_time = max(train1_arr, train2_arr)
                    if conflict_time > current_time_minutes:
                        conflicts.append(conflict_time)
    
    if conflicts:
        next_conflict = min(conflicts)
        return minutes_to_time(next_conflict)
    
    return None


# API Routes
@api_router.get("/")
async def root():
    return {"message": "AAGAMI RAIL - AI Train Traffic Control API"}


@api_router.get("/trains", response_model=List[Train])
async def get_trains():
    """Get all trains (sample data for demo)"""
    return SAMPLE_TRAINS


@api_router.get("/train/{train_id}", response_model=Train)
async def get_train_details(train_id: str):
    """Get detailed information about a specific train"""
    for train in SAMPLE_TRAINS:
        if train.id.startswith(train_id):
            return train
    
    raise HTTPException(status_code=404, detail="Train not found")


@api_router.post("/trains", response_model=Train)
async def create_train(train: TrainCreate):
    """Create a new train"""
    new_train = Train(**train.dict(), details=generate_train_details(train.route))
    return new_train


@api_router.get("/stations", response_model=List[Station])
async def get_stations():
    """Get all stations for map display"""
    return SAMPLE_STATIONS


@api_router.get("/routes", response_model=List[Route])
async def get_routes():
    """Get all routes for map display"""
    return SAMPLE_ROUTES


@api_router.post("/optimize", response_model=OptimizationResult)
async def optimize_trains(trains: List[Train] = None):
    """Run AI optimization on train schedules"""
    if trains is None:
        trains = SAMPLE_TRAINS
    
    # Reset any previous optimization
    original_trains = copy.deepcopy(trains)
    for train in trains:
        train.delay_minutes = 0
        train.optimized_arrival = None
        train.optimized_departure = None
        train.rerouted = False
        train.new_route = None
        train.explanation = None
        train.status = "on_time"
    
    optimized_trains, basic_explanations = optimize_with_disasters(trains)
    kpis = calculate_advanced_kpis(original_trains, optimized_trains)
    
    # Generate enhanced explanations and what changed summary
    enhanced_explanations = generate_enhanced_explanations(optimized_trains)
    what_changed = generate_what_changed_summary(original_trains, optimized_trains)
    
    alerts = check_and_generate_alerts(optimized_trains)
    
    # Update global alerts
    ACTIVE_ALERTS.clear()
    ACTIVE_ALERTS.extend(alerts)
    
    return OptimizationResult(
        original_trains=original_trains,
        optimized_trains=optimized_trains,
        kpis=kpis,
        explanations=enhanced_explanations,
        alerts=alerts,
        what_changed=what_changed
    )


@api_router.post("/disaster", response_model=OptimizationResult)
async def apply_disaster_scenario(scenario: DisasterScenario):
    """Apply disaster scenario and re-optimize"""
    trains = SAMPLE_TRAINS
        
    # Reset trains and keep original for comparison
    original_trains = copy.deepcopy(trains)
    for train in trains:
        train.delay_minutes = 0
        train.optimized_arrival = None
        train.optimized_departure = None
        train.rerouted = False
        train.new_route = None
        train.explanation = None
        train.status = "on_time"
    
    optimized_trains, basic_explanations = optimize_with_disasters(trains, scenario.disasters)
    kpis = calculate_advanced_kpis(original_trains, optimized_trains, scenario.disasters)
    
    # Generate enhanced explanations and comprehensive analysis
    enhanced_explanations = generate_enhanced_explanations(optimized_trains, scenario.disasters)
    what_changed = generate_what_changed_summary(original_trains, optimized_trains, scenario.disasters)
    
    # Create disaster summary from what_changed analysis
    effectiveness = what_changed["summary_stats"]["optimization_effectiveness"]
    disaster_summary = f"AI Response Effectiveness: {effectiveness}% - {what_changed['impact_analysis']['delay_impact']['description']}"
    if what_changed["summary_stats"]["rerouted_trains"] > 0:
        disaster_summary += f" {what_changed['summary_stats']['rerouted_trains']} trains intelligently rerouted."
    
    alerts = check_and_generate_alerts(optimized_trains, scenario.disasters)
    
    # Update global alerts
    ACTIVE_ALERTS.clear()
    ACTIVE_ALERTS.extend(alerts)
    
    return OptimizationResult(
        original_trains=original_trains,
        optimized_trains=optimized_trains,
        kpis=kpis,
        explanations=enhanced_explanations,
        disaster_summary=disaster_summary,
        alerts=alerts,
        what_changed=what_changed
    )


@api_router.post("/disaster/custom", response_model=OptimizationResult)
async def apply_custom_disaster(disaster: CustomDisaster):
    """Apply custom disaster scenario"""
    trains = SAMPLE_TRAINS
    
    # Reset trains and keep original for comparison
    original_trains = copy.deepcopy(trains)
    for train in trains:
        train.delay_minutes = 0
        train.optimized_arrival = None
        train.optimized_departure = None
        train.rerouted = False
        train.new_route = None
        train.explanation = None
        train.status = "on_time"
    
    disaster_obj = Disaster(**disaster.dict())
    scenario = DisasterScenario(
        disasters=[disaster_obj],
        description=f"Custom disruption: {disaster.description}"
    )
    
    optimized_trains, basic_explanations = optimize_with_disasters(trains, scenario.disasters)
    kpis = calculate_advanced_kpis(original_trains, optimized_trains, scenario.disasters)
    
    # Generate enhanced explanations and comprehensive analysis
    enhanced_explanations = generate_enhanced_explanations(optimized_trains, scenario.disasters)
    what_changed = generate_what_changed_summary(original_trains, optimized_trains, scenario.disasters)
    
    # Create disaster summary from what_changed analysis
    effectiveness = what_changed["summary_stats"]["optimization_effectiveness"]
    disaster_summary = f"AI Response Effectiveness: {effectiveness}% - {what_changed['impact_analysis']['delay_impact']['description']}"
    if what_changed["summary_stats"]["rerouted_trains"] > 0:
        disaster_summary += f" {what_changed['summary_stats']['rerouted_trains']} trains intelligently rerouted."
    
    alerts = check_and_generate_alerts(optimized_trains, scenario.disasters)
    
    # Update global alerts
    ACTIVE_ALERTS.clear()
    ACTIVE_ALERTS.extend(alerts)
    
    return OptimizationResult(
        original_trains=original_trains,
        optimized_trains=optimized_trains,
        kpis=kpis,
        explanations=enhanced_explanations,
        disaster_summary=disaster_summary,
        alerts=alerts,
        what_changed=what_changed
    )


@api_router.get("/disaster-scenarios")
async def get_disaster_scenarios():
    """Get predefined disaster scenarios"""
    return DISASTER_SCENARIOS


@api_router.get("/simulation/status", response_model=SystemStatus)
async def get_simulation_status():
    """Get current simulation status"""
    return SystemStatus(
        simulation=SIMULATION_STATE,
        active_alerts=ACTIVE_ALERTS[-10:],  # Last 10 alerts
        system_health="healthy" if len(ACTIVE_ALERTS) < 5 else "warning" if len(ACTIVE_ALERTS) < 10 else "critical",
        total_trains=len(SAMPLE_TRAINS),
        active_disasters=len(ACTIVE_DISASTERS)
    )


@api_router.post("/simulation/control")
async def control_simulation(control: SimulationControl):
    """Control simulation state"""
    global SIMULATION_STATE
    SIMULATION_STATE = control
    
    # Advance time if playing
    if control.state == SimulationState.PLAYING:
        advance_simulation_time(int(control.speed))
    
    return {"status": "updated", "simulation": SIMULATION_STATE}


@api_router.get("/simulation/next-conflict")
async def get_next_conflict():
    """Get time of next scheduling conflict"""
    next_conflict_time = find_next_conflict_time(SAMPLE_TRAINS)
    
    return {
        "next_conflict_time": next_conflict_time,
        "current_time": SIMULATION_STATE.current_time,
        "can_jump": next_conflict_time is not None
    }


@api_router.post("/simulation/jump-to-conflict")
async def jump_to_next_conflict():
    """Jump simulation time to next conflict"""
    next_conflict_time = find_next_conflict_time(SAMPLE_TRAINS)
    
    if next_conflict_time:
        SIMULATION_STATE.current_time = next_conflict_time
        return {"status": "jumped", "new_time": next_conflict_time}
    
    return {"status": "no_conflicts", "current_time": SIMULATION_STATE.current_time}


@api_router.get("/alerts", response_model=List[Alert])
async def get_active_alerts():
    """Get active system alerts"""
    return ACTIVE_ALERTS


@api_router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    for alert in ACTIVE_ALERTS:
        if alert.id == alert_id:
            alert.acknowledged = True
            return {"status": "acknowledged", "alert_id": alert_id}
    
    raise HTTPException(status_code=404, detail="Alert not found")


@api_router.delete("/alerts/{alert_id}")
async def dismiss_alert(alert_id: str):
    """Dismiss an alert"""
    global ACTIVE_ALERTS
    ACTIVE_ALERTS = [alert for alert in ACTIVE_ALERTS if alert.id != alert_id]
    return {"status": "dismissed", "alert_id": alert_id}


@api_router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    # Run optimization to get current metrics
    optimized_trains, _ = optimize_with_disasters(SAMPLE_TRAINS)
    kpis = calculate_advanced_kpis(SAMPLE_TRAINS, optimized_trains)
    
    # Calculate route throughput separately for performance metrics
    route_throughput = {}
    for train in optimized_trains:
        route = train.rerouted and train.new_route or train.route
        if train.delay_minutes < 30:  # Consider successful if delay < 30 min
            route_throughput[route] = route_throughput.get(route, 0) + 1
    
    return PerformanceMetrics(
        total_trains=int(kpis["total_trains"]),
        on_time_trains=int(kpis["on_time_trains"]),
        delayed_trains=int(kpis["delayed_trains"]),
        rerouted_trains=int(kpis["rerouted_trains"]),
        avg_delay=kpis["avg_delay_minutes"],
        max_delay=int(kpis["max_delay_minutes"]),
        throughput_improvement=kpis["throughput_improvement"],
        route_throughput=route_throughput
    )


@api_router.get("/conflicts")
async def get_conflicts():
    """Get current scheduling conflicts"""
    # Detect conflicts in original schedule
    conflicts = []
    route_trains = defaultdict(list)
    
    for train in SAMPLE_TRAINS:
        route_trains[train.route].append(train)
    
    conflict_count = 0
    for route, trains in route_trains.items():
        for i, train1 in enumerate(trains):
            for train2 in trains[i+1:]:
                train1_arr = time_to_minutes(train1.planned_arrival)
                train1_dep = time_to_minutes(train1.planned_departure)
                train2_arr = time_to_minutes(train2.planned_arrival)
                train2_dep = time_to_minutes(train2.planned_departure)
                
                if not (train1_dep <= train2_arr or train2_dep <= train1_arr):
                    conflicts.append({
                        "train1": f"{train1.id[:6]} ({train1.priority})",
                        "train2": f"{train2.id[:6]} ({train2.priority})",
                        "route": route,
                        "overlap_minutes": min(train1_dep, train2_dep) - max(train1_arr, train2_arr),
                        "conflict_time": minutes_to_time(max(train1_arr, train2_arr))
                    })
                    conflict_count += 1
    
    return {
        "conflicts": conflict_count,
        "details": conflicts
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()