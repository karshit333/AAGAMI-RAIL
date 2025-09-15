from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum


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

class TrainCreate(BaseModel):
    priority: Priority
    planned_arrival: str
    planned_departure: str
    route: str

class OptimizationResult(BaseModel):
    original_trains: List[Train]
    optimized_trains: List[Train]
    kpis: Dict[str, float]

class Station(BaseModel):
    id: str
    name: str
    x: float  # coordinate for map
    y: float  # coordinate for map

class Route(BaseModel):
    id: str
    stations: List[str]  # station IDs
    path: List[Dict[str, float]]  # path coordinates for animation


# Sample data initialization
SAMPLE_STATIONS = [
    Station(id="A", name="Station A", x=100, y=200),
    Station(id="B", name="Station B", x=300, y=200),
    Station(id="C", name="Station C", x=500, y=200),
    Station(id="D", name="Station D", x=700, y=200),
    Station(id="E", name="Station E", x=500, y=100),
]

SAMPLE_ROUTES = [
    Route(id="A-B", stations=["A", "B"], path=[{"x": 100, "y": 200}, {"x": 300, "y": 200}]),
    Route(id="B-C", stations=["B", "C"], path=[{"x": 300, "y": 200}, {"x": 500, "y": 200}]),
    Route(id="C-D", stations=["C", "D"], path=[{"x": 500, "y": 200}, {"x": 700, "y": 200}]),
    Route(id="D-E", stations=["D", "E"], path=[{"x": 700, "y": 200}, {"x": 500, "y": 100}]),
    Route(id="B-E", stations=["B", "E"], path=[{"x": 300, "y": 200}, {"x": 500, "y": 100}]),
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


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes since midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def detect_conflicts(trains: List[Train]) -> List[tuple]:
    """Detect scheduling conflicts between trains on same route"""
    conflicts = []
    route_trains = {}
    
    # Group trains by route
    for train in trains:
        if train.route not in route_trains:
            route_trains[train.route] = []
        route_trains[train.route].append(train)
    
    # Check for conflicts within each route
    for route, route_train_list in route_trains.items():
        for i, train1 in enumerate(route_train_list):
            for j, train2 in enumerate(route_train_list[i+1:], i+1):
                # Check if trains overlap
                train1_arr = time_to_minutes(train1.planned_arrival)
                train1_dep = time_to_minutes(train1.planned_departure)
                train2_arr = time_to_minutes(train2.planned_arrival)
                train2_dep = time_to_minutes(train2.planned_departure)
                
                # Check for time overlap
                if not (train1_dep <= train2_arr or train2_dep <= train1_arr):
                    conflicts.append((train1, train2))
    
    return conflicts


def optimize_schedule(trains: List[Train]) -> List[Train]:
    """AI-powered optimization algorithm"""
    optimized_trains = []
    
    # Priority weights for sorting
    priority_weights = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
    
    # Group trains by route and sort by priority then arrival time
    route_trains = {}
    for train in trains:
        if train.route not in route_trains:
            route_trains[train.route] = []
        route_trains[train.route].append(train)
    
    # Optimize each route separately
    for route, route_train_list in route_trains.items():
        # Sort by priority (high first) then by planned arrival
        route_train_list.sort(key=lambda t: (-priority_weights[t.priority], time_to_minutes(t.planned_arrival)))
        
        # Schedule trains sequentially with conflict resolution
        scheduled_trains = []
        for train in route_train_list:
            new_train = Train(**train.dict())
            new_train.optimized_arrival = train.planned_arrival
            new_train.optimized_departure = train.planned_departure
            
            # Check for conflicts with already scheduled trains
            for scheduled_train in scheduled_trains:
                scheduled_arr = time_to_minutes(scheduled_train.optimized_arrival)
                scheduled_dep = time_to_minutes(scheduled_train.optimized_departure)
                current_arr = time_to_minutes(new_train.optimized_arrival)
                current_dep = time_to_minutes(new_train.optimized_departure)
                
                # If conflict detected, delay the lower priority train
                if not (scheduled_dep <= current_arr or current_dep <= scheduled_arr):
                    if priority_weights[new_train.priority] < priority_weights[scheduled_train.priority]:
                        # Delay current train
                        delay = scheduled_dep - current_arr + 5  # 5 minute buffer
                        new_train.delay_minutes = delay
                        new_train.optimized_arrival = minutes_to_time(current_arr + delay)
                        new_train.optimized_departure = minutes_to_time(current_dep + delay)
                    else:
                        # Delay scheduled train (shouldn't happen due to sorting)
                        delay = current_dep - scheduled_arr + 5
                        scheduled_train.delay_minutes = delay
                        scheduled_train.optimized_arrival = minutes_to_time(scheduled_arr + delay)
                        scheduled_train.optimized_departure = minutes_to_time(scheduled_dep + delay)
            
            scheduled_trains.append(new_train)
        
        optimized_trains.extend(scheduled_trains)
    
    return optimized_trains


def calculate_kpis(original_trains: List[Train], optimized_trains: List[Train]) -> Dict[str, float]:
    """Calculate performance KPIs"""
    total_trains = len(original_trains)
    total_delay = sum(train.delay_minutes for train in optimized_trains)
    avg_delay = total_delay / total_trains if total_trains > 0 else 0
    
    # Throughput calculation (trains on time vs delayed)
    on_time_trains = len([train for train in optimized_trains if train.delay_minutes == 0])
    throughput_percentage = (on_time_trains / total_trains * 100) if total_trains > 0 else 100
    
    return {
        "total_trains": total_trains,
        "avg_delay_minutes": round(avg_delay, 2),
        "throughput_percentage": round(throughput_percentage, 2),
        "total_delay_minutes": total_delay,
        "on_time_trains": on_time_trains
    }


# API Routes
@api_router.get("/")
async def root():
    return {"message": "AAGAMI RAIL - AI Train Optimization API"}


@api_router.get("/trains", response_model=List[Train])
async def get_trains():
    """Get all trains (sample data for demo)"""
    return SAMPLE_TRAINS


@api_router.post("/trains", response_model=Train)
async def create_train(train: TrainCreate):
    """Create a new train"""
    new_train = Train(**train.dict())
    # In a real app, save to database
    return new_train


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
    
    optimized_trains = optimize_schedule(trains)
    kpis = calculate_kpis(trains, optimized_trains)
    
    return OptimizationResult(
        original_trains=trains,
        optimized_trains=optimized_trains,
        kpis=kpis
    )


@api_router.get("/stations", response_model=List[Station])
async def get_stations():
    """Get all stations for map display"""
    return SAMPLE_STATIONS


@api_router.get("/routes", response_model=List[Route])
async def get_routes():
    """Get all routes for map display"""
    return SAMPLE_ROUTES


@api_router.get("/conflicts")
async def get_conflicts():
    """Get current scheduling conflicts"""
    conflicts = detect_conflicts(SAMPLE_TRAINS)
    return {
        "conflicts": len(conflicts),
        "details": [
            {
                "train1": f"{c[0].id} ({c[0].route})",
                "train2": f"{c[1].id} ({c[1].route})",
                "route": c[0].route
            }
            for c in conflicts
        ]
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