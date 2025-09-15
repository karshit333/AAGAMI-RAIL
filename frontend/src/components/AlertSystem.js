import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Separator } from "./ui/separator";
import { 
  AlertTriangle, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  Bell, 
  BellRing,
  Clock,
  Route,
  Train,
  Activity
} from "lucide-react";

const AlertSystem = ({ alerts = [], onDismissAlert, onAcknowledgeAlert }) => {
  const [sortedAlerts, setSortedAlerts] = useState([]);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    // Sort alerts by severity and timestamp
    const sorted = [...alerts].sort((a, b) => {
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      const severityDiff = (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
      
      if (severityDiff !== 0) return severityDiff;
      
      // If same severity, sort by timestamp (most recent first)
      return new Date(`2023-01-01 ${b.timestamp}`) - new Date(`2023-01-01 ${a.timestamp}`);
    });

    setSortedAlerts(sorted);
  }, [alerts]);

  const getAlertIcon = (type, severity) => {
    const iconSize = "h-4 w-4";
    
    switch (type) {
      case 'critical_delay':
        return <Clock className={`${iconSize} text-red-600`} />;
      case 'route_blockage':
        return <Route className={`${iconSize} text-red-600`} />;
      case 'vip_train':
        return <Train className={`${iconSize} text-purple-600`} />;
      case 'system_health':
        return <Activity className={`${iconSize} text-blue-600`} />;
      case 'disaster':
        return <AlertTriangle className={`${iconSize} text-orange-600`} />;
      default:
        return severity === 'critical' ? 
          <AlertCircle className={`${iconSize} text-red-600`} /> :
          <AlertTriangle className={`${iconSize} text-yellow-600`} />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500 bg-red-50';
      case 'high':
        return 'border-orange-500 bg-orange-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  const getSeverityBadgeVariant = (severity) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getTypeDisplayName = (type) => {
    switch (type) {
      case 'critical_delay':
        return 'Critical Delay';
      case 'route_blockage':
        return 'Route Blockage';
      case 'vip_train':
        return 'VIP Train';
      case 'system_health':
        return 'System Health';
      case 'disaster':
        return 'Disaster';
      default:
        return 'Alert';
    }
  };

  const filteredAlerts = filterType === 'all' ? 
    sortedAlerts : 
    sortedAlerts.filter(alert => alert.type === filterType);

  const handleDismiss = (alertId) => {
    if (onDismissAlert) {
      onDismissAlert(alertId);
    }
  };

  const handleAcknowledge = (alertId) => {
    if (onAcknowledgeAlert) {
      onAcknowledgeAlert(alertId);
    }
  };

  const unacknowledgedCount = alerts.filter(alert => !alert.acknowledged).length;
  const criticalCount = alerts.filter(alert => alert.severity === 'critical').length;

  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            System Status: All Clear
          </CardTitle>
          <CardDescription>No active alerts or warnings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>All systems operating normally</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {unacknowledgedCount > 0 ? (
              <BellRing className="h-5 w-5 text-red-600" />
            ) : (
              <Bell className="h-5 w-5 text-gray-600" />
            )}
            Smart Alert System
            {unacknowledgedCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unacknowledgedCount} New
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
              <Badge variant="destructive">
                {criticalCount} Critical
              </Badge>
            )}
            <Badge variant="outline">
              {alerts.length} Total
            </Badge>
          </div>
        </CardTitle>
        <CardDescription>
          Real-time system alerts and notifications
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Alert Type Filter */}
        <div className="flex flex-wrap gap-2 mb-4">
          <Button
            variant={filterType === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('all')}
          >
            All ({alerts.length})
          </Button>
          <Button
            variant={filterType === 'critical_delay' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('critical_delay')}
          >
            Delays ({alerts.filter(a => a.type === 'critical_delay').length})
          </Button>
          <Button
            variant={filterType === 'route_blockage' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('route_blockage')}
          >
            Blockages ({alerts.filter(a => a.type === 'route_blockage').length})
          </Button>
          <Button
            variant={filterType === 'vip_train' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('vip_train')}
          >
            VIP Trains ({alerts.filter(a => a.type === 'vip_train').length})
          </Button>
        </div>

        <Separator className="mb-4" />

        {/* Alert List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredAlerts.map((alert, index) => (
            <Alert key={alert.id} className={`${getSeverityColor(alert.severity)} transition-all duration-200`}>
              <div className="flex items-start justify-between w-full">
                <div className="flex items-start gap-3 flex-1">
                  {getAlertIcon(alert.type, alert.severity)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        {alert.title}
                      </h4>
                      <Badge variant={getSeverityBadgeVariant(alert.severity)} className="text-xs">
                        {alert.severity.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {getTypeDisplayName(alert.type)}
                      </Badge>
                    </div>
                    <AlertDescription className="text-sm text-gray-700 mb-2">
                      {alert.message}
                    </AlertDescription>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {alert.timestamp}
                      </span>
                      {alert.train_id && (
                        <span className="flex items-center gap-1">
                          <Train className="h-3 w-3" />
                          Train {alert.train_id.slice(0, 6)}
                        </span>
                      )}
                      {alert.route_id && (
                        <span className="flex items-center gap-1">
                          <Route className="h-3 w-3" />
                          Route {alert.route_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 ml-4">
                  {!alert.acknowledged && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleAcknowledge(alert.id)}
                      className="text-xs"
                    >
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Ack
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDismiss(alert.id)}
                    className="text-xs text-gray-500 hover:text-red-600"
                  >
                    <XCircle className="h-3 w-3" />
                  </Button>
                </div>
              </div>
              
              {alert.acknowledged && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <span className="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle className="h-3 w-3" />
                    Acknowledged
                  </span>
                </div>
              )}
            </Alert>
          ))}
        </div>

        {filteredAlerts.length === 0 && filterType !== 'all' && (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No {filterType.replace('_', ' ')} alerts found</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertSystem;