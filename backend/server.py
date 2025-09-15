from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime, timedelta
from enum import Enum
import heapq
from collections import defaultdict
import copy


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
    VIP_TRAIN = "vip_train"
    BREAKDOWN = "breakdown"


# Models
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

class Disaster(BaseModel):
    type: DisasterType
    affected_route: Optional[str] = None
    duration_minutes: int = 60
    description: str = ""
    speed_reduction: float = 0.0
    custom_description: Optional[str] = None

class DisasterScenario(BaseModel):
    disasters: List[Disaster]
    description: str

class OptimizationResult(BaseModel):
    original_trains: List[Train]
    optimized_trains: List[Train]
    kpis: Dict[str, float]
    explanations: List[str]
    disaster_summary: Optional[str] = None

class PerformanceMetrics(BaseModel):
    total_trains: int
    on_time_trains: int
    delayed_trains: int
    rerouted_trains: int
    avg_delay: float
    max_delay: int
    throughput_improvement: float
    route_throughput: Dict[str, int]


# Sample data initialization
SAMPLE_STATIONS = [
    Station(id="A", name="Delhi Junction", x=100, y=200),
    Station(id="B", name="Ghaziabad", x=300, y=200),
    Station(id="C", name="Moradabad", x=500, y=200),
    Station(id="D", name="Bareilly", x=700, y=200),
    Station(id="E", name="Lucknow", x=500, y=100),
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

SAMPLE_TRAINS = [
    Train(priority=Priority.HIGH, planned_arrival="08:00", planned_departure="08:15", route="A-B"),
    Train(priority=Priority.HIGH, planned_arrival="08:10", planned_departure="08:25", route="A-B"),
    Train(priority=Priority.MEDIUM, planned_arrival="08:05", planned_departure="08:20", route="B-C"),
    Train(priority=Priority.MEDIUM, planned_arrival="08:30", planned_departure="08:45", route="B-C"),
    Train(priority=Priority.LOW, planned_arrival="08:15", planned_departure="08:30", route="C-D"),
    Train(priority=Priority.HIGH, planned_arrival="08:20", planned_departure="08:35", route="D-E"),
    Train(priority=Priority.MEDIUM, planned_arrival="08:25", planned_departure="08:40", route="B-E"),
    Train(priority=Priority.LOW, planned_arrival="08:35", planned_departure="08:50", route="B-E"),
    Train(priority=Priority.HIGH, planned_arrival="08:40", planned_departure="08:55", route="C-D"),
    Train(priority=Priority.LOW, planned_arrival="08:45", planned_departure="09:00", route="A-B"),
]

# Predefined disaster scenarios
DISASTER_SCENARIOS = {
    "flood_ab": DisasterScenario(
        disasters=[Disaster(type=DisasterType.FLOOD, affected_route="A-B", duration_minutes=120, description="Heavy rainfall floods A-B section")],
        description="Flood on A-B section blocks main route for 2 hours"
    ),
    "equipment_failure": DisasterScenario(
        disasters=[Disaster(type=DisasterType.EQUIPMENT_FAILURE, affected_route="B-C", duration_minutes=45, description="Signal failure at Ghaziabad")],
        description="Equipment failure causes signal outage on B-C route"
    ),
    "weather_slow": DisasterScenario(
        disasters=[Disaster(type=DisasterType.WEATHER, affected_route="all", speed_reduction=0.4, description="Dense fog reduces visibility")],
        description="Weather disruption reduces train speeds by 40% across network"
    ),
    "vip_train": DisasterScenario(
        disasters=[Disaster(type=DisasterType.VIP_TRAIN, description="Emergency VIP train requires immediate priority")],
        description="Emergency VIP train insertion requires priority clearance"
    ),
    "breakdown_ce": DisasterScenario(
        disasters=[Disaster(type=DisasterType.BREAKDOWN, affected_route="C-D", duration_minutes=15, description="Freight train breakdown blocks C-D")],
        description="Train breakdown blocks C-D section for 15 minutes"
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
                    
        elif disaster.type == DisasterType.WEATHER:
            # Reduce speed on all or specific routes
            for route in affected_routes:
                if disaster.affected_route == "all" or route.id == disaster.affected_route:
                    route.speed_reduction = disaster.speed_reduction
    
    return affected_routes


def optimize_with_disasters(trains: List[Train], disasters: List[Disaster] = None) -> Tuple[List[Train], List[str]]:
    """Advanced optimization with disaster handling and rerouting"""
    optimized_trains = []
    explanations = []
    
    # Apply disasters if any
    current_routes = SAMPLE_ROUTES
    if disasters:
        current_routes = apply_disasters(SAMPLE_ROUTES, disasters)
    
    # Priority weights for sorting
    priority_weights = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
    
    # Add VIP train if disaster includes it
    vip_disaster = next((d for d in disasters if d.type == DisasterType.VIP_TRAIN), None) if disasters else None
    if vip_disaster:
        vip_train = Train(
            priority=Priority.HIGH,
            planned_arrival="08:12",
            planned_departure="08:27",
            route="A-B"  # VIP train takes priority route
        )
        trains = [vip_train] + trains
        explanations.append("Emergency VIP train inserted with highest priority on A-B route")
    
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
                        new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + 10)
                        new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + 10)
                        explanations.append(f"Train {train.id[:6]} rerouted via {' → '.join(path)} due to {route_id} blockage (+10 min delay)")
                else:
                    # No alternate route - significant delay
                    new_train.delay_minutes += 60
                    new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + 60)
                    new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + 60)
                    explanations.append(f"Train {train.id[:6]} delayed 60 min - no alternate route available for blocked {route_id}")
            
            # Apply speed reductions
            elif speed_reduction > 0:
                delay_from_speed = int(15 * speed_reduction)  # Base delay proportional to speed reduction
                new_train.delay_minutes += delay_from_speed
                new_train.optimized_arrival = minutes_to_time(time_to_minutes(train.planned_arrival) + delay_from_speed)
                new_train.optimized_departure = minutes_to_time(time_to_minutes(train.planned_departure) + delay_from_speed)
                explanations.append(f"Train {train.id[:6]} delayed {delay_from_speed} min due to {int(speed_reduction*100)}% speed reduction")
            
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
                            new_train.optimized_arrival = minutes_to_time(current_arr + delay)
                            new_train.optimized_departure = minutes_to_time(current_dep + delay)
                            explanations.append(f"Train {train.id[:6]} delayed {delay} min to give priority to {scheduled_train.priority.lower()} priority train {scheduled_train.id[:6]}")
                        elif priority_weights[new_train.priority] > priority_weights[scheduled_train.priority]:
                            # Delay scheduled train
                            delay = current_dep - scheduled_arr + 5
                            scheduled_train.delay_minutes += delay
                            scheduled_train.optimized_arrival = minutes_to_time(scheduled_arr + delay)
                            scheduled_train.optimized_departure = minutes_to_time(scheduled_dep + delay)
                            explanations.append(f"Train {scheduled_train.id[:6]} delayed {delay} min to give priority to {new_train.priority.lower()} priority train {train.id[:6]}")
            
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
        "disaster_impact": float(len(disasters) if disasters else 0),
        "route_throughput": route_throughput
    }


def generate_disaster_summary(disasters: List[Disaster], kpis: Dict[str, float], explanations: List[str]) -> str:
    """Generate human-readable disaster impact summary"""
    if not disasters:
        return ""
    
    summary_parts = []
    
    # Count impacts
    delayed_count = kpis.get("delayed_trains", 0)
    rerouted_count = kpis.get("rerouted_trains", 0)
    avg_delay = kpis.get("avg_delay_minutes", 0)
    throughput_change = kpis.get("throughput_improvement", 0)
    
    # Disaster descriptions
    disaster_descriptions = []
    for disaster in disasters:
        if disaster.type == DisasterType.FLOOD:
            disaster_descriptions.append(f"flood on {disaster.affected_route}")
        elif disaster.type == DisasterType.WEATHER:
            disaster_descriptions.append(f"weather disruption reducing speeds by {int(disaster.speed_reduction*100)}%")
        elif disaster.type == DisasterType.EQUIPMENT_FAILURE:
            disaster_descriptions.append(f"equipment failure on {disaster.affected_route}")
        elif disaster.type == DisasterType.VIP_TRAIN:
            disaster_descriptions.append("emergency VIP train insertion")
        elif disaster.type == DisasterType.BREAKDOWN:
            disaster_descriptions.append(f"train breakdown on {disaster.affected_route}")
    
    disaster_text = ", ".join(disaster_descriptions)
    
    summary = f"Disaster Impact: {disaster_text.title()} affected {delayed_count} trains with average delay of {avg_delay:.1f} minutes."
    
    if rerouted_count > 0:
        summary += f" {rerouted_count} trains were rerouted to alternate paths."
    
    if throughput_change < 0:
        summary += f" Network throughput decreased by {abs(throughput_change):.1f}%."
    
    return summary


# API Routes
@api_router.get("/")
async def root():
    return {"message": "AAGAMI RAIL - AI Train Traffic Control API"}


@api_router.get("/trains", response_model=List[Train])
async def get_trains():
    """Get all trains (sample data for demo)"""
    return SAMPLE_TRAINS


@api_router.post("/trains", response_model=Train)
async def create_train(train: TrainCreate):
    """Create a new train"""
    new_train = Train(**train.dict())
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
    for train in trains:
        train.delay_minutes = 0
        train.optimized_arrival = None
        train.optimized_departure = None
        train.rerouted = False
        train.new_route = None
        train.explanation = None
    
    optimized_trains, explanations = optimize_with_disasters(trains)
    kpis = calculate_advanced_kpis(trains, optimized_trains)
    
    return OptimizationResult(
        original_trains=trains,
        optimized_trains=optimized_trains,
        kpis=kpis,
        explanations=explanations
    )


@api_router.post("/disaster", response_model=OptimizationResult)
async def apply_disaster_scenario(scenario: DisasterScenario, trains: List[Train] = None):
    """Apply disaster scenario and re-optimize"""
    if trains is None:
        trains = SAMPLE_TRAINS
        
    # Reset trains
    for train in trains:
        train.delay_minutes = 0
        train.optimized_arrival = None
        train.optimized_departure = None
        train.rerouted = False
        train.new_route = None
        train.explanation = None
    
    optimized_trains, explanations = optimize_with_disasters(trains, scenario.disasters)
    kpis = calculate_advanced_kpis(trains, optimized_trains, scenario.disasters)
    disaster_summary = generate_disaster_summary(scenario.disasters, kpis, explanations)
    
    return OptimizationResult(
        original_trains=trains,
        optimized_trains=optimized_trains,
        kpis=kpis,
        explanations=explanations,
        disaster_summary=disaster_summary
    )


@api_router.get("/disaster-scenarios")
async def get_disaster_scenarios():
    """Get predefined disaster scenarios"""
    return DISASTER_SCENARIOS


@api_router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    # Run optimization to get current metrics
    optimized_trains, _ = optimize_with_disasters(SAMPLE_TRAINS)
    kpis = calculate_advanced_kpis(SAMPLE_TRAINS, optimized_trains)
    
    return PerformanceMetrics(
        total_trains=kpis["total_trains"],
        on_time_trains=kpis["on_time_trains"],
        delayed_trains=kpis["delayed_trains"],
        rerouted_trains=kpis["rerouted_trains"],
        avg_delay=kpis["avg_delay_minutes"],
        max_delay=kpis["max_delay_minutes"],
        throughput_improvement=kpis["throughput_improvement"],
        route_throughput=kpis["route_throughput"]
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
                        "overlap_minutes": min(train1_dep, train2_dep) - max(train1_arr, train2_arr)
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