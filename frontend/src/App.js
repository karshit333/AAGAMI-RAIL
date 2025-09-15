import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Separator } from "./components/ui/separator";
import TrainMap from "./components/TrainMap";
import PerformanceCharts from "./components/PerformanceCharts";
import SimulationControls from "./components/SimulationControls";
import TrainDetailsModal from "./components/TrainDetailsModal";
import AlertSystem from "./components/AlertSystem";
import AdvancedDisasterManager from "./components/AdvancedDisasterManager";
import { 
  Train, 
  MapPin, 
  Activity, 
  AlertTriangle, 
  Info, 
  BarChart3,
  Route,
  Clock,
  Users,
  TrendingUp,
  Zap,
  Bell
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [trains, setTrains] = useState([]);
  const [optimizedTrains, setOptimizedTrains] = useState([]);
  const [kpis, setKpis] = useState({});
  const [stations, setStations] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [disasterScenarios, setDisasterScenarios] = useState({});
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [hasOptimized, setHasOptimized] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [explanations, setExplanations] = useState([]);
  const [disasterSummary, setDisasterSummary] = useState("");
  const [selectedDisaster, setSelectedDisaster] = useState("");
  
  // New state for advanced features
  const [simulationStatus, setSimulationStatus] = useState(null);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [showTrainModal, setShowTrainModal] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);

  useEffect(() => {
    loadInitialData();
    loadSimulationStatus();
    loadSystemAlerts();
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      if (activeTab === "dashboard") {
        loadSimulationStatus();
        loadSystemAlerts();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [activeTab]);

  const loadInitialData = async () => {
    try {
      const [trainsRes, stationsRes, routesRes, disasterRes] = await Promise.all([
        axios.get(`${API}/trains`),
        axios.get(`${API}/stations`),
        axios.get(`${API}/routes`),
        axios.get(`${API}/disaster-scenarios`)
      ]);

      setTrains(trainsRes.data);
      setStations(stationsRes.data);
      setRoutes(routesRes.data);
      setDisasterScenarios(disasterRes.data);
    } catch (error) {
      console.error("Error loading initial data:", error);
    }
  };

  const runOptimization = async () => {
    setIsOptimizing(true);
    try {
      const response = await axios.post(`${API}/optimize`, trains);
      setOptimizedTrains(response.data.optimized_trains);
      setKpis(response.data.kpis);
      setExplanations(response.data.explanations);
      setDisasterSummary("");
      setHasOptimized(true);
    } catch (error) {
      console.error("Error running optimization:", error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const runDisasterScenario = async () => {
    if (!selectedDisaster) return;
    
    setIsOptimizing(true);
    try {
      const scenario = disasterScenarios[selectedDisaster];
      const response = await axios.post(`${API}/disaster`, scenario);
      setOptimizedTrains(response.data.optimized_trains);
      setKpis(response.data.kpis);
      setExplanations(response.data.explanations);
      setDisasterSummary(response.data.disaster_summary);
      setHasOptimized(true);
    } catch (error) {
      console.error("Error running disaster scenario:", error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "High":
        return "bg-red-500";
      case "Medium":
        return "bg-blue-500";
      case "Low":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const getPriorityVariant = (priority) => {
    switch (priority) {
      case "High":
        return "destructive";
      case "Medium":
        return "default";
      case "Low":
        return "secondary";
      default:
        return "secondary";
    }
  };

  const formatTime = (timeStr) => {
    return timeStr || "N/A";
  };

  const Sidebar = () => (
    <div className="w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-0 z-10">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <Train className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-900">AAGAMI RAIL</h1>
            <p className="text-xs text-gray-600">SIH 2025 Prototype</p>
          </div>
        </div>
        
        <nav className="space-y-2">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === "dashboard" 
                ? "bg-blue-50 text-blue-700 font-medium" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            Dashboard
          </button>
          
          <button
            onClick={() => setActiveTab("map")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === "map" 
                ? "bg-blue-50 text-blue-700 font-medium" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <MapPin className="h-4 w-4" />
            Map View
          </button>
          
          <button
            onClick={() => setActiveTab("disaster")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === "disaster" 
                ? "bg-blue-50 text-blue-700 font-medium" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <AlertTriangle className="h-4 w-4" />
            Disaster Mgmt
          </button>
          
          <button
            onClick={() => setActiveTab("performance")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === "performance" 
                ? "bg-blue-50 text-blue-700 font-medium" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Activity className="h-4 w-4" />
            Performance
          </button>
          
          <button
            onClick={() => setActiveTab("about")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === "about" 
                ? "bg-blue-50 text-blue-700 font-medium" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Info className="h-4 w-4" />
            About
          </button>
        </nav>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      
      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">
                  {activeTab === "dashboard" && "Traffic Control Dashboard"}
                  {activeTab === "map" && "Railway Network Map"}
                  {activeTab === "disaster" && "Disaster Management"}
                  {activeTab === "performance" && "Performance Analytics"}
                  {activeTab === "about" && "About AAGAMI RAIL"}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  AI-powered train traffic optimization system
                </p>
              </div>
              <div className="flex gap-3">
                <Button 
                  onClick={runOptimization}
                  disabled={isOptimizing}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  {isOptimizing ? "Optimizing..." : "Run AI Optimization"}
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Tab Content */}
        <main className="p-6">
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              {/* KPI Cards */}
              {hasOptimized && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Total Trains</CardTitle>
                      <Train className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{kpis.total_trains}</div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Avg Delay</CardTitle>
                      <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{kpis.avg_delay_minutes} min</div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">On Time</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{kpis.on_time_trains}</div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Rerouted</CardTitle>
                      <Route className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{kpis.rerouted_trains || 0}</div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Disaster Summary */}
              {disasterSummary && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {disasterSummary}
                  </AlertDescription>
                </Alert>
              )}

              {/* Schedule Comparison */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Original Schedule */}
                <Card>
                  <CardHeader>
                    <CardTitle>Original Schedule</CardTitle>
                    <CardDescription>Current train scheduling with conflicts</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Train</TableHead>
                          <TableHead>Route</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Arrival</TableHead>
                          <TableHead>Departure</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {trains.map((train) => (
                          <TableRow key={train.id}>
                            <TableCell className="font-medium">{train.id.slice(0, 6)}</TableCell>
                            <TableCell>{train.route}</TableCell>
                            <TableCell>
                              <Badge variant={getPriorityVariant(train.priority)}>
                                {train.priority}
                              </Badge>
                            </TableCell>
                            <TableCell>{formatTime(train.planned_arrival)}</TableCell>
                            <TableCell>{formatTime(train.planned_departure)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>

                {/* Optimized Schedule */}
                <Card>
                  <CardHeader>
                    <CardTitle>AI Optimized Schedule</CardTitle>
                    <CardDescription>
                      {hasOptimized 
                        ? "Conflicts resolved with smart routing and priorities" 
                        : "Run optimization to see results"
                      }
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {hasOptimized ? (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Train</TableHead>
                            <TableHead>Route</TableHead>
                            <TableHead>Priority</TableHead>
                            <TableHead>Arrival</TableHead>
                            <TableHead>Departure</TableHead>
                            <TableHead>Status</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {optimizedTrains.map((train) => (
                            <TableRow key={train.id}>
                              <TableCell className="font-medium">{train.id.slice(0, 6)}</TableCell>
                              <TableCell>
                                {train.rerouted ? (
                                  <span className="text-green-600">
                                    {train.new_route} <Badge variant="outline" className="ml-1">Rerouted</Badge>
                                  </span>
                                ) : (
                                  train.route
                                )}
                              </TableCell>
                              <TableCell>
                                <Badge variant={getPriorityVariant(train.priority)}>
                                  {train.priority}
                                </Badge>
                              </TableCell>
                              <TableCell>{formatTime(train.optimized_arrival)}</TableCell>
                              <TableCell>{formatTime(train.optimized_departure)}</TableCell>
                              <TableCell>
                                <span className={train.delay_minutes > 0 ? "text-red-600" : "text-green-600"}>
                                  {train.delay_minutes > 0 ? `+${train.delay_minutes}m` : "On time"}
                                </span>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <div className="flex items-center justify-center h-64 text-gray-500">
                        Click "Run AI Optimization" to see optimized schedule
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* AI Explanations */}
              {explanations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>AI Decision Explanations</CardTitle>
                    <CardDescription>How the AI resolved conflicts and optimized the schedule</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {explanations.map((explanation, index) => (
                        <div key={index} className="text-sm p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                          {explanation}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {activeTab === "map" && (
            <Card>
              <CardHeader>
                <CardTitle>Railway Network Visualization</CardTitle>
                <CardDescription>Real-time train positions with disaster impact visualization</CardDescription>
              </CardHeader>
              <CardContent>
                <TrainMap
                  stations={stations}
                  routes={routes}
                  trains={hasOptimized ? optimizedTrains : trains}
                  getPriorityColor={getPriorityColor}
                />
              </CardContent>
            </Card>
          )}

          {activeTab === "disaster" && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Disaster Scenario Management</CardTitle>
                  <CardDescription>Simulate disruptions and test AI response capabilities</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-4">Predefined Scenarios</h3>
                      <div className="space-y-3">
                        <Select value={selectedDisaster} onValueChange={setSelectedDisaster}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select disaster scenario" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="flood_ab">Flood on A-B Route</SelectItem>
                            <SelectItem value="equipment_failure">Equipment Failure</SelectItem>
                            <SelectItem value="weather_slow">Weather Disruption</SelectItem>
                            <SelectItem value="vip_train">Emergency VIP Train</SelectItem>
                            <SelectItem value="breakdown_ce">Train Breakdown</SelectItem>
                          </SelectContent>
                        </Select>
                        
                        <Button 
                          onClick={runDisasterScenario}
                          disabled={!selectedDisaster || isOptimizing}
                          className="w-full"
                          variant="destructive"
                        >
                          <AlertTriangle className="h-4 w-4 mr-2" />
                          {isOptimizing ? "Simulating..." : "Apply Disaster Scenario"}
                        </Button>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-semibold mb-4">Scenario Details</h3>
                      {selectedDisaster && disasterScenarios[selectedDisaster] && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            {disasterScenarios[selectedDisaster].description}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Disaster Scenarios Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(disasterScenarios).map(([key, scenario]) => (
                  <Card key={key} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => setSelectedDisaster(key)}>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                        {scenario.description.split(' ').slice(0, 3).join(' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-xs text-gray-600">{scenario.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === "performance" && (
            <div className="space-y-6">
              <PerformanceCharts 
                kpis={kpis} 
                trains={optimizedTrains.length > 0 ? optimizedTrains : trains}
                hasOptimized={hasOptimized}
              />
            </div>
          )}

          {activeTab === "about" && (
            <div className="max-w-4xl">
              <Card>
                <CardHeader>
                  <CardTitle>About AAGAMI RAIL</CardTitle>
                  <CardDescription>AI-Powered Train Traffic Control System</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Background</h3>
                    <p className="text-gray-700 leading-relaxed">
                      Indian Railways manages train movements primarily through the experience of traffic controllers. 
                      As congestion grows, manual methods reach their limits. Trains of different priorities share 
                      limited infrastructure, and disruptions make scheduling even harder.
                    </p>
                  </div>
                  
                  <Separator />
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Problem Statement</h3>
                    <p className="text-gray-700 leading-relaxed">
                      How can we maximize section throughput and minimize delays while ensuring safety, 
                      even under disruptions? Traditional manual approaches struggle with the complexity 
                      of modern railway operations.
                    </p>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Our Solution – AAGAMI RAIL</h3>
                    <ul className="list-disc list-inside text-gray-700 space-y-2 leading-relaxed">
                      <li>AI-powered decision-support tool for railway traffic controllers</li>
                      <li>Models constraints, train priorities, and route optimization</li>
                      <li>Produces conflict-free schedules dynamically</li>
                      <li>Re-optimizes rapidly under disruptions and emergencies</li>
                      <li>Provides clear recommendations and what-if simulations</li>
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Key Features</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-start gap-3">
                        <Zap className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium">AI Optimization</h4>
                          <p className="text-sm text-gray-600">Priority-based scheduling with conflict resolution</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Disaster Management</h4>
                          <p className="text-sm text-gray-600">Real-time disruption simulation and rerouting</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <MapPin className="h-5 w-5 text-green-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Map Visualization</h4>
                          <p className="text-sm text-gray-600">Interactive network view with live train tracking</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <BarChart3 className="h-5 w-5 text-purple-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Performance Analytics</h4>
                          <p className="text-sm text-gray-600">Comprehensive KPIs and throughput monitoring</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Expected Impact</h3>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <ul className="list-disc list-inside text-blue-800 space-y-1">
                        <li><strong>Reduced delays</strong> through intelligent conflict resolution</li>
                        <li><strong>Higher throughput</strong> via optimized route utilization</li>
                        <li><strong>Faster decision-making</strong> for traffic controllers</li>
                        <li><strong>Better disaster response</strong> with automated rerouting</li>
                        <li><strong>Improved passenger experience</strong> through reliable scheduling</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white mt-12">
          <div className="px-6 py-4">
            <p className="text-center text-gray-600 text-sm">
              AAGAMI RAIL – SIH 2025 Prototype. AI Decision Support for Indian Railways.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;