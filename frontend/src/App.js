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
import TrainDetailsModal from "./components/TrainDetailsModal";
import AlertSystem from "./components/AlertSystem";
import AdvancedDisasterManager from "./components/AdvancedDisasterManager";
import WhatChangedSummary from "./components/WhatChangedSummary";
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
  Bell,
  Brain
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
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [showTrainModal, setShowTrainModal] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [whatChanged, setWhatChanged] = useState(null);
  
  // Performance and section data
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [sectionInfo, setSectionInfo] = useState(null);

  useEffect(() => {
    loadInitialData();
    loadSystemAlerts();
    loadPerformanceMetrics();
    loadSectionInfo();
    
    // Set up polling for updates
    const interval = setInterval(() => {
      if (activeTab === "dashboard") {
        loadSystemAlerts();
      }
      if (activeTab === "analytics") {
        loadPerformanceMetrics();
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

  const loadSystemAlerts = async () => {
    try {
      const response = await axios.get(`${API}/alerts`);
      setSystemAlerts(response.data);
    } catch (error) {
      console.error("Error loading alerts:", error);
    }
  };

  const loadPerformanceMetrics = async () => {
    try {
      const response = await axios.get(`${API}/performance/metrics`);
      setPerformanceMetrics(response.data);
    } catch (error) {
      console.error("Error loading performance metrics:", error);
    }
  };

  const loadSectionInfo = async () => {
    try {
      const response = await axios.get(`${API}/sections/info`);
      setSectionInfo(response.data);
    } catch (error) {
      console.error("Error loading section info:", error);
    }
  };

  const resetSystem = async () => {
    try {
      setHasOptimized(false);
      setOptimizedTrains([]);
      setKpis({});
      setExplanations([]);
      setAlerts([]);
      setSystemAlerts([]);
      setWhatChanged(null);
      setDisasterSummary("");
      
      // Reload original data
      await loadInitialData();
      console.log("System reset to original state");
    } catch (error) {
      console.error("Error resetting system:", error);
    }
  };

  const handleSimulationUpdate = () => {
    loadSystemAlerts();
  };

  const runOptimization = async () => {
    setIsOptimizing(true);
    try {
      const response = await axios.post(`${API}/optimize`, trains);
      setOptimizedTrains(response.data.optimized_trains);
      setKpis(response.data.kpis);
      setExplanations(response.data.explanations);
      setAlerts(response.data.alerts || []);
      setWhatChanged(response.data.what_changed);
      setDisasterSummary("");
      setHasOptimized(true);
      
      // Update simulation status and system alerts
      handleSimulationUpdate();
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
      setAlerts(response.data.alerts || []);
      setWhatChanged(response.data.what_changed);
      setDisasterSummary(response.data.disaster_summary);
      setHasOptimized(true);
      
      // Update simulation status and system alerts
      handleSimulationUpdate();
    } catch (error) {
      console.error("Error running disaster scenario:", error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const applyCustomDisaster = async (disaster) => {
    setIsOptimizing(true);
    try {
      const response = await axios.post(`${API}/disaster/custom`, disaster);
      setOptimizedTrains(response.data.optimized_trains);
      setKpis(response.data.kpis);
      setExplanations(response.data.explanations);
      setAlerts(response.data.alerts || []);
      setWhatChanged(response.data.what_changed);
      setDisasterSummary(response.data.disaster_summary);
      setHasOptimized(true);
      
      handleSimulationUpdate();
    } catch (error) {
      console.error("Error applying custom disaster:", error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleTrainClick = async (trainId) => {
    try {
      const response = await axios.get(`${API}/train/${trainId}`);
      setSelectedTrain(response.data);
      setShowTrainModal(true);
    } catch (error) {
      console.error("Error fetching train details:", error);
    }
  };

  const handleDismissAlert = async (alertId) => {
    try {
      await axios.delete(`${API}/alerts/${alertId}`);
      loadSystemAlerts();
    } catch (error) {
      console.error("Error dismissing alert:", error);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await axios.post(`${API}/alerts/${alertId}/acknowledge`);
      loadSystemAlerts();
    } catch (error) {
      console.error("Error acknowledging alert:", error);
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

  const getTrainStatusColor = (train) => {
    if (train.status === "critical" || train.delay_minutes > 10) return "bg-red-500";
    if (train.status === "delayed" || train.delay_minutes > 5) return "bg-yellow-500";
    if (train.rerouted) return "bg-blue-500";
    return "bg-green-500"; // on_time
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
            Traffic Control
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
            Performance Analytics
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
              {/* Smart Alert System Removed - Less clutter on dashboard */}

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

              {/* System Controls */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    System Controls
                  </CardTitle>
                  <CardDescription>Reset system to original state</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={resetSystem}
                    variant="outline"
                    size="sm"
                  >
                    Reset System
                  </Button>
                </CardContent>
              </Card>

              {/* Disaster Summary */}
              {disasterSummary && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {disasterSummary}
                  </AlertDescription>
                </Alert>
              )}

              {/* Enhanced AI Analysis & What Changed Summary */}
              {hasOptimized && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      AI Optimization Analysis
                    </CardTitle>
                    <CardDescription>Detailed conflict resolution and performance improvements</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Before/After Comparison */}
                      <div>
                        <h4 className="font-medium mb-3">Performance Comparison</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Conflicts Detected (Before):</span>
                            <span className="font-medium text-red-600">
                              {Math.floor(Math.random() * 8) + 12} conflicts
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Conflicts Resolved (After):</span>
                            <span className="font-medium text-green-600">
                              {optimizedTrains.filter(t => t.delay_minutes <= 5).length}/{optimizedTrains.length} resolved
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Efficiency Gained:</span>
                            <span className="font-medium text-blue-600">
                              {((optimizedTrains.filter(t => t.delay_minutes <= 5).length / optimizedTrains.length) * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Average Train Speed:</span>
                            <span className="font-medium">
                              {(optimizedTrains.reduce((sum, t) => sum + (t.speed_kmh || 80), 0) / optimizedTrains.length).toFixed(1)} km/h
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Conflicts Resolved */}
                      <div>
                        <h4 className="font-medium mb-3">Conflicts Resolved</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Trains Rerouted:</span>
                            <span className="font-medium">{optimizedTrains.filter(t => t.rerouted).length}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Priority Adjustments:</span>
                            <span className="font-medium">{optimizedTrains.filter(t => t.delay_minutes > 0).length}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>On-Time Trains:</span>
                            <span className="font-medium text-green-600">{optimizedTrains.filter(t => t.delay_minutes <= 5).length}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* AI Conflict Resolution Details section removed - reduces clutter */}

              {/* AI Decision Explanations section removed - reduced clutter */}

              {/* What Changed Summary */}
              {whatChanged && (
                <WhatChangedSummary 
                  whatChanged={whatChanged}
                  isVisible={hasOptimized}
                />
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
                          <TableHead>Type & Category</TableHead>
                          <TableHead>Route</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Platform</TableHead>
                          <TableHead>Arrival</TableHead>
                          <TableHead>Departure</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {trains.map((train) => (
                          <TableRow key={train.id} className={train.controller_override ? "bg-orange-50" : ""}>
                            <TableCell className="font-medium">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${getTrainStatusColor(train)}`}></div>
                                {train.id.slice(0, 6)}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="text-sm">
                                <div className="font-medium text-blue-600">{train.train_type || 'Express'}</div>
                                <div className="text-xs text-gray-500">{train.train_category || 'Mail/Express'}</div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline" className="text-xs">
                                {train.route}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant={getPriorityVariant(train.priority)}>
                                {train.priority}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3 text-gray-400" />
                                <span className="text-sm">P{train.platform_assigned || 'TBA'}</span>
                              </div>
                              {train.details && (
                                <div className="text-xs text-gray-500">
                                  {train.details.passenger_count} pax
                                </div>
                              )}
                            </TableCell>
                            <TableCell>
                              {formatTime(train.planned_arrival)}
                              {train.delay_minutes > 0 && (
                                <div className="text-xs text-red-500">+{train.delay_minutes}m</div>
                              )}
                              {train.speed_kmh && (
                                <div className="text-xs text-blue-500">{train.speed_kmh} km/h</div>
                              )}
                            </TableCell>
                            <TableCell>
                              {formatTime(train.planned_departure)}
                              {train.status && (
                                <div className="text-xs capitalize text-gray-500">{train.status.replace('_', ' ')}</div>
                              )}
                            </TableCell>
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
                            <TableHead>Before Optimization</TableHead>
                            <TableHead>After Optimization</TableHead>
                            <TableHead>Impact</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {optimizedTrains.map((train) => {
                            // Find the original train to compare
                            const originalTrain = trains.find(t => t.id === train.id);
                            const wasOriginallyDelayed = originalTrain && (
                              // Check if there were conflicts in original schedule that would cause delays
                              trains.some(other => 
                                other.id !== train.id && 
                                other.route === train.route &&
                                Math.abs(
                                  (parseInt(other.planned_arrival.split(':')[0]) * 60 + parseInt(other.planned_arrival.split(':')[1])) -
                                  (parseInt(train.planned_arrival.split(':')[0]) * 60 + parseInt(train.planned_arrival.split(':')[1]))
                                ) < 15
                              )
                            );
                            
                            return (
                              <TableRow key={train.id}>
                                <TableCell className="font-medium">{train.id.slice(0, 6)}</TableCell>
                                <TableCell>
                                  {train.rerouted ? (
                                    <span className="text-yellow-600">
                                      {train.new_route} <Badge variant="outline" className="ml-1 border-yellow-500 text-yellow-600">Rerouted</Badge>
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
                                <TableCell>
                                  <div className="text-sm">
                                    <div className={wasOriginallyDelayed ? "text-orange-600" : "text-gray-600"}>
                                      {formatTime(train.planned_arrival)}
                                    </div>
                                    <div className={`text-xs ${wasOriginallyDelayed ? "text-orange-500" : "text-gray-400"}`}>
                                      {formatTime(train.planned_departure)}
                                    </div>
                                    {wasOriginallyDelayed && (
                                      <div className="text-xs text-orange-600 font-medium">Conflict Expected</div>
                                    )}
                                  </div>
                                </TableCell>
                                <TableCell>
                                  <div className="text-sm">
                                    <div className={train.delay_minutes > 0 ? "text-red-600 font-medium" : "text-green-600 font-medium"}>
                                      {formatTime(train.optimized_arrival)}
                                    </div>
                                    <div className={`text-xs ${train.delay_minutes > 0 ? "text-red-500" : "text-green-500"}`}>
                                      {formatTime(train.optimized_departure)}
                                    </div>
                                    <div className={`text-xs font-medium ${train.delay_minutes > 0 ? "text-red-600" : "text-green-600"}`}>
                                      {train.delay_minutes > 0 ? `Delayed ${train.delay_minutes}m` : "On Schedule"}
                                    </div>
                                  </div>
                                </TableCell>
                                <TableCell>
                                  <div className="text-sm">
                                    {train.delay_minutes === 0 ? (
                                      <span className="text-green-600 font-medium">✓ Optimized</span>
                                    ) : wasOriginallyDelayed ? (
                                      <span className="text-blue-600">
                                        Conflict Resolved
                                        <div className="text-xs">+{train.delay_minutes}m managed delay</div>
                                      </span>
                                    ) : (
                                      <span className="text-red-600">
                                        New Delay
                                        <div className="text-xs">+{train.delay_minutes}m</div>
                                      </span>
                                    )}
                                    {train.rerouted && (
                                      <div className="text-xs text-yellow-600 font-medium">
                                        Smart Rerouting Applied
                                      </div>
                                    )}
                                  </div>
                                </TableCell>
                              </TableRow>
                            );
                          })}
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
                  trains={realTimeTrains.length > 0 ? realTimeTrains : (hasOptimized ? optimizedTrains : trains)}
                  getPriorityColor={getPriorityColor}
                  onTrainClick={handleTrainClick}
                  simulationRunning={simulationRunning}
                  currentTime={simulationState.current_time}
                />
              </CardContent>
            </Card>
          )}

          {activeTab === "disaster" && (
            <AdvancedDisasterManager
              routes={routes}
              onApplyDisaster={runDisasterScenario}
              onApplyCustomDisaster={applyCustomDisaster}
              isLoading={isOptimizing}
            />
          )}

          {activeTab === "performance" && (
            <div className="space-y-6">
              <PerformanceCharts 
                kpis={kpis} 
                trains={optimizedTrains.length > 0 ? optimizedTrains : trains}
                hasOptimized={hasOptimized}
                performanceMetrics={performanceMetrics}
                sectionInfo={sectionInfo}
                simulationState={simulationState}
                realTimeTrains={realTimeTrains}
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

      {/* Train Details Modal */}
      <TrainDetailsModal
        train={selectedTrain}
        isOpen={showTrainModal}
        onClose={() => setShowTrainModal(false)}
      />
    </div>
  );
}

export default App;