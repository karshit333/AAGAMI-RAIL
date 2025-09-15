import React from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Separator } from "./ui/separator";
import { 
  Train, 
  Users, 
  MapPin, 
  Clock, 
  Fuel, 
  Gauge,
  Route,
  AlertCircle
} from "lucide-react";

const TrainDetailsModal = ({ train, isOpen, onClose }) => {
  if (!train) return null;

  const getPriorityColor = (priority) => {
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

  const getStatusColor = (status) => {
    switch (status) {
      case "on_time":
        return "text-green-600";
      case "delayed":
        return "text-yellow-600";
      case "critical":
        return "text-red-600";
      case "rerouted":
        return "text-blue-600";
      case "blocked":
        return "text-red-800";
      default:
        return "text-gray-600";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "on_time":
        return "On Time";
      case "delayed":
        return "Delayed";
      case "critical":
        return "Critical Delay";
      case "rerouted":
        return "Rerouted";
      case "blocked":
        return "Blocked";
      default:
        return "Unknown";
    }
  };

  const calculateLoadPercentage = () => {
    if (!train.details) return 0;
    return Math.round((train.details.current_load / train.details.capacity) * 100);
  };

  const formatStops = () => {
    if (!train.details?.stops || train.details.stops.length === 0) {
      return "Non-stop service";
    }
    return train.details.stops.join(" → ");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Train className="h-5 w-5" />
            Train {train.id.slice(0, 8)}
            <Badge variant={getPriorityColor(train.priority)} className="ml-2">
              {train.priority} Priority
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Detailed train information and operational status
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Overview */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center justify-between">
                Current Status
                <span className={`font-semibold ${getStatusColor(train.status)}`}>
                  {getStatusText(train.status)}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Planned Arrival:</span>
                  <div className="font-medium">{train.planned_arrival}</div>
                </div>
                <div>
                  <span className="text-gray-600">Planned Departure:</span>
                  <div className="font-medium">{train.planned_departure}</div>
                </div>
                <div>
                  <span className="text-gray-600">Optimized Arrival:</span>
                  <div className="font-medium">{train.optimized_arrival || train.planned_arrival}</div>
                </div>
                <div>
                  <span className="text-gray-600">Optimized Departure:</span>
                  <div className="font-medium">{train.optimized_departure || train.planned_departure}</div>
                </div>
              </div>
              
              {train.delay_minutes > 0 && (
                <div className="flex items-center gap-2 p-2 bg-red-50 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-red-800">
                    Delayed by {train.delay_minutes} minutes
                  </span>
                </div>
              )}

              {train.rerouted && (
                <div className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg">
                  <Route className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-blue-800">
                    Rerouted from {train.route} to {train.new_route}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Route Information */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Route Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div>
                  <span className="text-gray-600">Origin:</span>
                  <div className="font-medium">{train.details?.origin || "Unknown"}</div>
                </div>
                <div>
                  <span className="text-gray-600">Destination:</span>
                  <div className="font-medium">{train.details?.destination || "Unknown"}</div>
                </div>
                <div>
                  <span className="text-gray-600">Route:</span>
                  <div className="font-medium">{train.rerouted ? train.new_route : train.route}</div>
                </div>
                <div>
                  <span className="text-gray-600">Stops:</span>
                  <div className="font-medium text-xs">{formatStops()}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Train Specifications */}
          {train.details && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Train className="h-4 w-4" />
                  Train Specifications
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-3">
                    <div>
                      <span className="text-gray-600">Engine Type:</span>
                      <div className="font-medium">{train.details.engine_type}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Coach Count:</span>
                      <div className="font-medium">{train.details.coach_count} coaches</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Max Speed:</span>
                      <div className="font-medium">{train.details.max_speed} km/h</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Current Speed:</span>
                      <div className="font-medium">{train.speed_kmh} km/h</div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <span className="text-gray-600">Capacity:</span>
                      <div className="font-medium">{train.details.capacity} passengers</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Current Load:</span>
                      <div className="font-medium flex items-center gap-2">
                        {train.details.current_load} passengers
                        <Badge variant={calculateLoadPercentage() > 90 ? "destructive" : "secondary"}>
                          {calculateLoadPercentage()}%
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Passenger Count:</span>
                      <div className="font-medium flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {train.details.passenger_count}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Fuel Consumption:</span>
                      <div className="font-medium flex items-center gap-1">
                        <Fuel className="h-3 w-3" />
                        {train.details.fuel_consumption} L/km
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Operational Metrics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Gauge className="h-4 w-4" />
                Operational Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Load Percentage Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Passenger Load</span>
                    <span>{calculateLoadPercentage()}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        calculateLoadPercentage() > 90 ? 'bg-red-500' : 
                        calculateLoadPercentage() > 75 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${calculateLoadPercentage()}%` }}
                    />
                  </div>
                </div>

                {/* Route Progress */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Route Progress</span>
                    <span>{Math.round((train.current_position || 0) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(train.current_position || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Explanation */}
          {train.explanation && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">AI Decision Explanation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 italic">
                  {train.explanation}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TrainDetailsModal;