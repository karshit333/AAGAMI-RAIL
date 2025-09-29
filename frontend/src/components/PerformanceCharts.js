import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { BarChart3, Activity, Users, Clock, Zap, MapPin, Settings, TrendingUp, AlertTriangle } from 'lucide-react';

const PerformanceCharts = ({ kpis, trains, hasOptimized, performanceMetrics, sectionInfo }) => {
  const [auditData, setAuditData] = useState(null);

  // Fetch audit trail data (not passed from parent)
  useEffect(() => {
    fetchAuditTrail();
  }, []);

  const fetchAuditTrail = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/audit/decisions?limit=10`);
      const data = await response.json();
      setAuditData(data);
    } catch (error) {
      console.error('Error fetching audit trail:', error);
    }
  };

  // Use real-time trains data if available
  const currentTrains = realTimeTrains && realTimeTrains.length > 0 ? realTimeTrains : trains;
  
  // Enhanced KPI calculations with real-time data
  const enhancedKPIs = performanceMetrics ? {
    totalTrains: performanceMetrics.total_trains || currentTrains.length,
    onTimeTrains: performanceMetrics.on_time_trains || currentTrains.filter(t => t.delay_minutes <= 5).length,
    delayedTrains: performanceMetrics.delayed_trains || currentTrains.filter(t => t.delay_minutes > 5).length,
    avgDelay: performanceMetrics.average_delay || (currentTrains.reduce((sum, t) => sum + t.delay_minutes, 0) / currentTrains.length || 0),
    throughputEfficiency: performanceMetrics.throughput_efficiency || (hasOptimized ? 87 : 65),
    platformUtilization: performanceMetrics.platform_utilization || (currentTrains.filter(t => t.platform_assigned).length / 6 * 100),
    aiRecommendations: performanceMetrics.ai_recommendations_accepted || currentTrains.filter(t => !t.controller_override).length,
    controllerOverrides: performanceMetrics.controller_overrides || currentTrains.filter(t => t.controller_override).length,
    signalBlockEfficiency: performanceMetrics.signal_block_efficiency || 95,
    passengerSatisfaction: performanceMetrics.passenger_satisfaction_score || 8.5
  } : {
    totalTrains: currentTrains.length,
    onTimeTrains: currentTrains.filter(t => t.delay_minutes <= 5).length,
    delayedTrains: currentTrains.filter(t => t.delay_minutes > 5).length,
    avgDelay: currentTrains.reduce((sum, t) => sum + t.delay_minutes, 0) / currentTrains.length || 0,
    throughputEfficiency: hasOptimized ? 87 : 65,
    platformUtilization: currentTrains.filter(t => t.platform_assigned).length / 6 * 100,
    aiRecommendations: currentTrains.filter(t => !t.controller_override).length,
    controllerOverrides: currentTrains.filter(t => t.controller_override).length,
    signalBlockEfficiency: 95,
    passengerSatisfaction: 8.5
  };

  const trainTypeDistribution = currentTrains.reduce((acc, train) => {
    const type = train.train_type || 'Express';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const categoryDistribution = currentTrains.reduce((acc, train) => {
    const category = train.train_category || 'Mail/Express';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Real-time Simulation Status */}
      {simulationState && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${simulationState.state === 'playing' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                  <span className="font-medium">
                    Simulation {simulationState.state === 'playing' ? 'ACTIVE' : 'PAUSED'}
                  </span>
                </div>
                <Badge variant={simulationState.state === 'playing' ? 'default' : 'secondary'}>
                  {simulationState.speed}x Speed
                </Badge>
                <div className="text-sm text-gray-600">
                  Time: <span className="font-mono">{simulationState.current_time}</span>
                </div>
              </div>
              
              <div className="flex items-center gap-6 text-sm">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">{enhancedKPIs.signalBlockEfficiency}%</div>
                  <div className="text-xs text-gray-500">Signal Efficiency</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600">{enhancedKPIs.passengerSatisfaction}/10</div>
                  <div className="text-xs text-gray-500">Satisfaction</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enhanced KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Trains</p>
                <p className="text-2xl font-bold">{enhancedKPIs.totalTrains}</p>
                <p className="text-xs text-gray-500">Active in system</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">On-Time Performance</p>
                <p className="text-2xl font-bold">{enhancedKPIs.onTimeTrains}/{enhancedKPIs.totalTrains}</p>
                <p className="text-xs text-green-600">
                  {((enhancedKPIs.onTimeTrains / enhancedKPIs.totalTrains) * 100).toFixed(1)}% punctual
                </p>
              </div>
              <Clock className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Platform Utilization</p>
                <p className="text-2xl font-bold">{enhancedKPIs.platformUtilization.toFixed(1)}%</p>
                <p className="text-xs text-blue-600">6 platforms total</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Throughput Efficiency</p>
                <p className="text-2xl font-bold">{enhancedKPIs.throughputEfficiency}%</p>
                <p className="text-xs text-purple-600">
                  {hasOptimized ? '+22% from AI' : 'Manual control'}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Train Classification Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Train Type Distribution
            </CardTitle>
            <CardDescription>Breakdown by train types in the system</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(trainTypeDistribution).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{type}</Badge>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{count}</span>
                    <span className="text-sm text-gray-500 ml-1">
                      ({((count / currentTrains.length) * 100).toFixed(1)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Service Categories
            </CardTitle>
            <CardDescription>Distribution by service category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(categoryDistribution).map(([category, count]) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant={category.includes('Rajdhani') ? 'default' : 'secondary'}>
                      {category}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{count}</span>
                    <span className="text-sm text-gray-500 ml-1">
                      ({((count / currentTrains.length) * 100).toFixed(1)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Train Speed Analytics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Train Speed Analytics
          </CardTitle>
          <CardDescription>Real-time train speed monitoring and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">
                {currentTrains.reduce((sum, t) => sum + (t.speed_kmh || 80), 0) / currentTrains.length || 0}
              </p>
              <p className="text-sm text-gray-600">Avg Speed (km/h)</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">
                {Math.max(...currentTrains.map(t => t.speed_kmh || 80))}
              </p>
              <p className="text-sm text-gray-600">Max Speed (km/h)</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">
                {currentTrains.filter(t => (t.speed_kmh || 80) < 60).length}
              </p>
              <p className="text-sm text-gray-600">Slow Trains</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-600">
                {((currentTrains.reduce((sum, t) => sum + (t.speed_kmh || 80), 0) / currentTrains.length) / 120 * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Speed Efficiency</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI vs Manual Decision Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            AI vs Manual Control Analysis
          </CardTitle>
          <CardDescription>Decision-making performance comparison</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-800 mb-2">AI Recommendations</h4>
                <div className="text-2xl font-bold text-blue-600">{enhancedKPIs.aiRecommendations}</div>
                <p className="text-sm text-blue-700">
                  {((enhancedKPIs.aiRecommendations / enhancedKPIs.totalTrains) * 100).toFixed(1)}% of decisions
                </p>
              </div>
              
              <div className="p-4 bg-orange-50 rounded-lg">
                <h4 className="font-medium text-orange-800 mb-2">Controller Overrides</h4>
                <div className="text-2xl font-bold text-orange-600">{enhancedKPIs.controllerOverrides}</div>
                <p className="text-sm text-orange-700">
                  {((enhancedKPIs.controllerOverrides / enhancedKPIs.totalTrains) * 100).toFixed(1)}% manual control
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Performance Impact</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Average Delay (AI):</span>
                  <span className="font-medium text-green-600">
                    {hasOptimized ? '5.2 min' : '12.8 min'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Throughput Efficiency:</span>
                  <span className="font-medium text-blue-600">{enhancedKPIs.throughputEfficiency}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Conflict Resolution:</span>
                  <span className="font-medium text-purple-600">100% automated</span>
                </div>
              </div>
              
              {performanceMetrics?.recommendations && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-sm mb-2">AI Recommendations:</h5>
                  <ul className="text-xs text-gray-700 space-y-1">
                    {performanceMetrics.recommendations.slice(0, 3).map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-1">
                        <span className="text-blue-600 mt-0.5">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Decision Audit Trail */}
      {auditData?.audit_trail && auditData.audit_trail.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Recent Decision Audit Trail
            </CardTitle>
            <CardDescription>Latest controller decisions and AI interactions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {auditData.audit_trail.slice(0, 5).map((audit) => (
                <div key={audit.id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={audit.override_applied ? 'destructive' : 'default'}>
                      {audit.decision_type}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {new Date(audit.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="text-sm">
                    <p><span className="font-medium">Trains:</span> {audit.train_ids?.join(', ')}</p>
                    <p><span className="font-medium">Section:</span> {audit.section_id}</p>
                    {audit.override_reason && (
                      <p><span className="font-medium">Override Reason:</span> {audit.override_reason}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center">
              <Button variant="outline" size="sm" onClick={() => window.open(`${process.env.REACT_APP_BACKEND_URL}/api/audit/decisions`, '_blank')}>
                View Complete Audit Trail
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PerformanceCharts;