import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { BarChart3, TrendingUp, Users, Clock, Route, AlertTriangle } from "lucide-react";

const PerformanceCharts = ({ kpis, trains, hasOptimized }) => {
  // Calculate priority distribution
  const getPriorityDistribution = () => {
    if (!trains || trains.length === 0) return {};
    
    const distribution = trains.reduce((acc, train) => {
      acc[train.priority] = (acc[train.priority] || 0) + 1;
      return acc;
    }, {});
    
    return distribution;
  };

  // Calculate route throughput
  const getRouteThroughput = () => {
    if (!trains || trains.length === 0) return {};
    
    const throughput = trains.reduce((acc, train) => {
      const route = train.rerouted ? train.new_route : train.route;
      if (train.delay_minutes < 30) { // Consider as successful if delay < 30 min
        acc[route] = (acc[route] || 0) + 1;
      }
      return acc;
    }, {});
    
    return throughput;
  };

  // Calculate delay distribution
  const getDelayDistribution = () => {
    if (!trains || trains.length === 0) return { onTime: 0, delayed: 0, critical: 0 };
    
    return trains.reduce((acc, train) => {
      if (train.delay_minutes === 0) {
        acc.onTime += 1;
      } else if (train.delay_minutes <= 15) {
        acc.delayed += 1;
      } else {
        acc.critical += 1;
      }
      return acc;
    }, { onTime: 0, delayed: 0, critical: 0 });
  };

  const priorityDistribution = getPriorityDistribution();
  const routeThroughput = getRouteThroughput();
  const delayDistribution = getDelayDistribution();

  // Simple bar chart component
  const SimpleBarChart = ({ data, title, color = "bg-blue-500" }) => {
    const maxValue = Math.max(...Object.values(data));
    
    return (
      <div className="space-y-3">
        <h4 className="font-medium text-sm text-gray-700">{title}</h4>
        <div className="space-y-2">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex items-center gap-3">
              <span className="text-xs w-16 text-gray-600">{key}</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${color} transition-all duration-300`}
                  style={{ width: `${maxValue > 0 ? (value / maxValue) * 100 : 0}%` }}
                />
              </div>
              <span className="text-xs font-medium w-8 text-gray-700">{value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Simple pie chart visualization using CSS
  const SimplePieChart = ({ data, title }) => {
    const total = Object.values(data).reduce((sum, val) => sum + val, 0);
    const colors = {
      'High': 'bg-red-500',
      'Medium': 'bg-blue-500', 
      'Low': 'bg-gray-500',
      'onTime': 'bg-green-500',
      'delayed': 'bg-yellow-500',
      'critical': 'bg-red-500'
    };
    
    return (
      <div className="space-y-3">
        <h4 className="font-medium text-sm text-gray-700">{title}</h4>
        <div className="flex flex-col space-y-2">
          {Object.entries(data).map(([key, value]) => {
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
            return (
              <div key={key} className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${colors[key] || 'bg-gray-400'}`} />
                <span className="text-xs flex-1">{key}</span>
                <span className="text-xs font-medium">{value} ({percentage}%)</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Performance Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Trains</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total_trains || trains.length}</div>
            <p className="text-xs text-muted-foreground">
              Active in system
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Delay</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.avg_delay_minutes || 0} min</div>
            <p className="text-xs text-muted-foreground">
              {hasOptimized ? "After optimization" : "Current estimate"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rerouted Trains</CardTitle>
            <Route className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.rerouted_trains || 0}</div>
            <p className="text-xs text-muted-foreground">
              Due to disruptions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disaster Impact</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.disaster_impact || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active scenarios
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Route Throughput Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Route Throughput
            </CardTitle>
            <CardDescription>Successful trains per route (delay {"<"} 30 min)</CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(routeThroughput).length > 0 ? (
              <SimpleBarChart 
                data={routeThroughput} 
                title="Trains per Route"
                color="bg-green-500"
              />
            ) : (
              <div className="flex items-center justify-center h-32 text-gray-500 text-sm">
                Run optimization to see throughput data
              </div>
            )}
          </CardContent>
        </Card>

        {/* Priority Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Users className="h-4 w-4" />
              Train Priorities
            </CardTitle>
            <CardDescription>Distribution by priority level</CardDescription>
          </CardHeader>
          <CardContent>
            <SimplePieChart 
              data={priorityDistribution} 
              title="Priority Breakdown"
            />
          </CardContent>
        </Card>

        {/* Delay Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Delay Analysis
            </CardTitle>
            <CardDescription>Train performance categories</CardDescription>
          </CardHeader>
          <CardContent>
            <SimplePieChart 
              data={{
                'On Time': delayDistribution.onTime,
                'Minor Delay': delayDistribution.delayed,
                'Critical Delay': delayDistribution.critical
              }} 
              title="Delay Categories"
            />
          </CardContent>
        </Card>
      </div>

      {/* Performance Comparison */}
      {hasOptimized && (
        <Card>
          <CardHeader>
            <CardTitle>Optimization Performance Summary</CardTitle>
            <CardDescription>Before vs After AI Optimization</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-700">{kpis.on_time_trains || 0}</div>
                <div className="text-sm text-blue-600">Trains On Time</div>
                <div className="text-xs text-gray-600 mt-1">
                  {kpis.total_trains ? ((kpis.on_time_trains / kpis.total_trains) * 100).toFixed(1) : 0}% success rate
                </div>
              </div>
              
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-700">{kpis.delayed_trains || 0}</div>
                <div className="text-sm text-yellow-600">Delayed Trains</div>
                <div className="text-xs text-gray-600 mt-1">
                  Avg {kpis.avg_delay_minutes || 0} min delay
                </div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-700">{kpis.rerouted_trains || 0}</div>
                <div className="text-sm text-green-600">Smart Reroutes</div>
                <div className="text-xs text-gray-600 mt-1">
                  Avoiding disruptions
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PerformanceCharts;