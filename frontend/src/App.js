import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";
import TrainMap from "./components/TrainMap";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [trains, setTrains] = useState([]);
  const [optimizedTrains, setOptimizedTrains] = useState([]);
  const [kpis, setKpis] = useState({});
  const [stations, setStations] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [hasOptimized, setHasOptimized] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [trainsRes, stationsRes, routesRes] = await Promise.all([
        axios.get(`${API}/trains`),
        axios.get(`${API}/stations`),
        axios.get(`${API}/routes`)
      ]);

      setTrains(trainsRes.data);
      setStations(stationsRes.data);
      setRoutes(routesRes.data);
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
      setHasOptimized(true);
    } catch (error) {
      console.error("Error running optimization:", error);
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

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AAGAMI RAIL</h1>
              <p className="text-sm text-gray-600 mt-1">AI Train Optimization - SIH 2025 Prototype</p>
            </div>
            <Button 
              onClick={runOptimization}
              disabled={isOptimizing}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isOptimizing ? "Optimizing..." : "Run AI Optimization"}
            </Button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
              <TabsTrigger value="map">Map View</TabsTrigger>
              <TabsTrigger value="about">About</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsContent value="dashboard" className="space-y-8">
            {/* KPI Cards */}
            {hasOptimized && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Trains</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpis.total_trains}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg Delay</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpis.avg_delay_minutes} min</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Throughput</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpis.throughput_percentage}%</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">On Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpis.on_time_trains}</div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Schedule Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
                        <TableHead>Train ID</TableHead>
                        <TableHead>Route</TableHead>
                        <TableHead>Priority</TableHead>
                        <TableHead>Arrival</TableHead>
                        <TableHead>Departure</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {trains.map((train) => (
                        <TableRow key={train.id}>
                          <TableCell className="font-medium">{train.id.slice(0, 8)}</TableCell>
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
                      ? "Conflicts resolved with priority-based optimization" 
                      : "Run optimization to see results"
                    }
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {hasOptimized ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Train ID</TableHead>
                          <TableHead>Route</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Arrival</TableHead>
                          <TableHead>Departure</TableHead>
                          <TableHead>Delay</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {optimizedTrains.map((train) => (
                          <TableRow key={train.id}>
                            <TableCell className="font-medium">{train.id.slice(0, 8)}</TableCell>
                            <TableCell>{train.route}</TableCell>
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
          </TabsContent>

          <TabsContent value="map">
            <Card>
              <CardHeader>
                <CardTitle>Railway Network Map</CardTitle>
                <CardDescription>Real-time train positions and route visualization</CardDescription>
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
          </TabsContent>

          <TabsContent value="about">
            <div className="space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>About AAGAMI RAIL</CardTitle>
                  <CardDescription>AI-Powered Train Optimization System</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Background</h3>
                    <p className="text-gray-700">
                      Indian Railways faces significant challenges with train scheduling and congestion management. 
                      Manual decision-making has limitations in handling complex optimization scenarios with multiple 
                      constraints and real-time changes.
                    </p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Solution - AAGAMI RAIL</h3>
                    <p className="text-gray-700">
                      AAGAMI RAIL is an AI-powered train optimization system that uses intelligent algorithms 
                      to resolve scheduling conflicts, minimize delays, and maximize throughput. The system 
                      considers train priorities, route constraints, and operational efficiency.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Key Features</h3>
                    <ul className="list-disc list-inside text-gray-700 space-y-1">
                      <li>AI-powered schedule optimization with priority-based conflict resolution</li>
                      <li>Real-time map visualization with animated train movements</li>
                      <li>Comprehensive KPI dashboard for performance monitoring</li>
                      <li>Clean, professional interface designed for railway operators</li>
                      <li>Before/after schedule comparison for impact analysis</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Future Scope</h3>
                    <ul className="list-disc list-inside text-gray-700 space-y-1">
                      <li>Integration with real Indian Railways datasets and APIs</li>
                      <li>Real-time disruption handling and dynamic re-optimization</li>
                      <li>Weather and disaster impact management</li>
                      <li>Passenger load balancing and demand prediction</li>
                      <li>Multi-objective optimization (cost, time, passenger satisfaction)</li>
                      <li>Mobile application for field operators</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            AAGAMI RAIL – SIH 2025 Prototype. Decision Support for Indian Railways.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;