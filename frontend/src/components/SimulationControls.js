import React, { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  Play, 
  Pause, 
  Square, 
  SkipForward, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from "lucide-react";

const SimulationControls = ({ onSimulationUpdate, simulationStatus }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState("1");
  const [currentTime, setCurrentTime] = useState("08:00");
  const [nextConflictTime, setNextConflictTime] = useState(null);

  useEffect(() => {
    // Update local state when simulation status changes
    if (simulationStatus) {
      setIsPlaying(simulationStatus.simulation?.state === 'playing');
      setSpeed(simulationStatus.simulation?.speed?.toString() || "1");
      setCurrentTime(simulationStatus.simulation?.current_time || "08:00");
    }
  }, [simulationStatus]);

  useEffect(() => {
    // Auto-advance time when playing
    let interval;
    if (isPlaying) {
      interval = setInterval(() => {
        advanceTime();
      }, 1000 / parseFloat(speed)); // Adjust interval based on speed
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, speed]);

  const advanceTime = () => {
    setCurrentTime(prevTime => {
      const [hours, minutes] = prevTime.split(':').map(Number);
      const totalMinutes = hours * 60 + minutes + 1;
      const newHours = Math.floor(totalMinutes / 60) % 24;
      const newMinutes = totalMinutes % 60;
      
      const newTime = `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
      
      // Update backend
      updateSimulationControl('playing', parseFloat(speed), newTime);
      
      return newTime;
    });
  };

  const updateSimulationControl = async (state, speedValue, time) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/simulation/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state: state,
          speed: speedValue,
          current_time: time,
          auto_advance: true
        }),
      });

      if (response.ok && onSimulationUpdate) {
        onSimulationUpdate();
      }
    } catch (error) {
      console.error('Error updating simulation control:', error);
    }
  };

  const handlePlayPause = () => {
    const newState = isPlaying ? 'paused' : 'playing';
    setIsPlaying(!isPlaying);
    updateSimulationControl(newState, parseFloat(speed), currentTime);
  };

  const handleStop = () => {
    setIsPlaying(false);
    setCurrentTime("08:00");
    updateSimulationControl('stopped', parseFloat(speed), "08:00");
  };

  const handleSpeedChange = (newSpeed) => {
    setSpeed(newSpeed);
    updateSimulationControl(isPlaying ? 'playing' : 'paused', parseFloat(newSpeed), currentTime);
  };

  const jumpToNextConflict = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/simulation/jump-to-conflict`, {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'jumped') {
          setCurrentTime(result.new_time);
          if (onSimulationUpdate) {
            onSimulationUpdate();
          }
        }
      }
    } catch (error) {
      console.error('Error jumping to next conflict:', error);
    }
  };

  const getSystemHealthColor = () => {
    if (!simulationStatus?.system_health) return 'bg-gray-500';
    
    switch (simulationStatus.system_health) {
      case 'healthy':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'critical':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getSystemHealthIcon = () => {
    if (!simulationStatus?.system_health) return <Clock className="h-4 w-4" />;
    
    switch (simulationStatus.system_health) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Real-Time Simulation Controls
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${getSystemHealthColor()}`} />
              <span className="text-sm text-gray-600">
                System: {simulationStatus?.system_health || 'Unknown'}
              </span>
            </div>
            <div className="text-2xl font-mono font-bold text-blue-600">
              {currentTime}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Play/Pause/Stop Controls */}
            <div className="flex items-center gap-2">
              <Button
                onClick={handlePlayPause}
                variant={isPlaying ? "default" : "outline"}
                size="sm"
                className="flex items-center gap-2"
              >
                {isPlaying ? (
                  <>
                    <Pause className="h-4 w-4" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Play
                  </>
                )}
              </Button>
              
              <Button
                onClick={handleStop}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <Square className="h-4 w-4" />
                Stop
              </Button>
            </div>

            {/* Speed Control */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Speed:</span>
              <Select value={speed} onValueChange={handleSpeedChange}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0.5">0.5x</SelectItem>
                  <SelectItem value="1">1x</SelectItem>
                  <SelectItem value="2">2x</SelectItem>
                  <SelectItem value="5">5x</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Jump to Conflict */}
            <Button
              onClick={jumpToNextConflict}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <SkipForward className="h-4 w-4" />
              Jump to Next Conflict
            </Button>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                {getSystemHealthIcon()}
                {simulationStatus?.total_trains || 0} Trains
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge 
                variant={simulationStatus?.active_disasters > 0 ? "destructive" : "secondary"}
                className="flex items-center gap-1"
              >
                <AlertTriangle className="h-3 w-3" />
                {simulationStatus?.active_disasters || 0} Disasters
              </Badge>
            </div>

            <div className="flex items-center gap-2">
              <Badge 
                variant={simulationStatus?.active_alerts?.length > 0 ? "destructive" : "secondary"}
                className="flex items-center gap-1"
              >
                <AlertTriangle className="h-3 w-3" />
                {simulationStatus?.active_alerts?.length || 0} Alerts
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SimulationControls;