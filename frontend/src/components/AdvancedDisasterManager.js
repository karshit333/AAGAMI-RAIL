import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Slider } from "./ui/slider";
import { Separator } from "./ui/separator";
import { 
  AlertTriangle, 
  Plus, 
  Trash2, 
  MapPin, 
  Clock, 
  Zap,
  CloudRain,
  Settings,
  Layers,
  Brain,
  TrendingUp
} from "lucide-react";

const AdvancedDisasterManager = ({ 
  routes, 
  onApplyDisaster, 
  onApplyCustomDisaster,
  isLoading = false 
}) => {
  const [selectedDisaster, setSelectedDisaster] = useState("");
  const [customDisasters, setCustomDisasters] = useState([]);
  const [activeCustomDisaster, setActiveCustomDisaster] = useState(null);
  const [multipleMode, setMultipleMode] = useState(false);
  const [simultaneousDisasters, setSimultaneousDisasters] = useState([]);

  // Custom disaster form state
  const [customForm, setCustomForm] = useState({
    type: 'custom',
    affected_route: '',
    duration_minutes: 30,
    description: '',
    speed_reduction: 0,
    severity: 'medium'
  });

  const disasterTypes = [
    { value: 'flood', label: 'Flood', icon: '🌊', description: 'Water logging blocks route' },
    { value: 'equipment_failure', label: 'Equipment Failure', icon: '⚠️', description: 'Signal or equipment malfunction' },
    { value: 'weather', label: 'Weather', icon: '🌧️', description: 'Weather reduces visibility/speed' },
    { value: 'breakdown', label: 'Train Breakdown', icon: '🚂', description: 'Train blocks section' },
    { value: 'custom', label: 'Custom Disaster', icon: '⚙️', description: 'Define custom disruption' }
  ];

  const severityLevels = [
    { value: 'low', label: 'Low', color: 'bg-blue-500' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
    { value: 'high', label: 'High', color: 'bg-orange-500' },
    { value: 'critical', label: 'Critical', color: 'bg-red-500' }
  ];

  const resetCustomForm = () => {
    setCustomForm({
      type: 'custom',
      affected_route: '',
      duration_minutes: 30,
      description: '',
      speed_reduction: 0,
      severity: 'medium'
    });
  };

  const addCustomDisaster = () => {
    if (!customForm.affected_route || !customForm.description) {
      return;
    }

    const newDisaster = {
      ...customForm,
      id: Date.now().toString(),
      coordinates: null // Can be extended for map drawing
    };

    if (multipleMode) {
      setSimultaneousDisasters([...simultaneousDisasters, newDisaster]);
    } else {
      setCustomDisasters([...customDisasters, newDisaster]);
    }

    resetCustomForm();
  };

  const removeCustomDisaster = (id) => {
    if (multipleMode) {
      setSimultaneousDisasters(simultaneousDisasters.filter(d => d.id !== id));
    } else {
      setCustomDisasters(customDisasters.filter(d => d.id !== id));
    }
  };

  const applySelectedDisaster = () => {
    if (selectedDisaster && onApplyDisaster) {
      onApplyDisaster(selectedDisaster);
    }
  };

  const applyCustomDisaster = (disaster) => {
    if (onApplyCustomDisaster) {
      onApplyCustomDisaster(disaster);
    }
  };

  const applyMultipleDisasters = () => {
    if (simultaneousDisasters.length > 0 && onApplyCustomDisaster) {
      // Create a scenario with multiple disasters
      const multipleScenario = {
        disasters: simultaneousDisasters,
        description: `Multiple disasters: ${simultaneousDisasters.map(d => d.description).join(', ')}`,
        multiple: true
      };
      
      onApplyDisaster('custom_multiple', multipleScenario);
    }
  };

  const getSeverityColor = (severity) => {
    const severityInfo = severityLevels.find(s => s.value === severity);
    return severityInfo?.color || 'bg-gray-500';
  };

  const getDisasterIcon = (type) => {
    const disasterInfo = disasterTypes.find(d => d.value === type);
    return disasterInfo?.icon || '⚠️';
  };

  return (
    <div className="space-y-6">
      {/* Mode Toggle */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Disaster Management Mode
            </div>
            <Button
              variant={multipleMode ? "default" : "outline"}
              size="sm"
              onClick={() => setMultipleMode(!multipleMode)}
              className="flex items-center gap-2"
            >
              <Layers className="h-4 w-4" />
              {multipleMode ? "Multiple Disasters" : "Single Disaster"}
            </Button>
          </CardTitle>
          <CardDescription>
            {multipleMode 
              ? "Simulate multiple simultaneous disasters" 
              : "Apply single disaster scenarios"
            }
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Predefined Scenarios */}
      <Card>
        <CardHeader>
          <CardTitle>Predefined Disaster Scenarios</CardTitle>
          <CardDescription>Quick-apply common disaster scenarios</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Select value={selectedDisaster} onValueChange={setSelectedDisaster}>
              <SelectTrigger>
                <SelectValue placeholder="Select disaster scenario" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="flood_ab">🌊 Flood on A-B Route</SelectItem>
                <SelectItem value="equipment_failure">⚠️ Equipment Failure B-C</SelectItem>
                <SelectItem value="weather_slow">🌧️ Weather Disruption (Network)</SelectItem>
                <SelectItem value="vip_train">🚨 Emergency VIP Train</SelectItem>
                <SelectItem value="breakdown_ce">🚂 Train Breakdown C-D</SelectItem>
                <SelectItem value="multiple_disasters">🌪️ Multiple Disasters</SelectItem>
              </SelectContent>
            </Select>
            
            <Button 
              onClick={applySelectedDisaster}
              disabled={!selectedDisaster || isLoading}
              variant="destructive"
              className="flex items-center gap-2"
            >
              <AlertTriangle className="h-4 w-4" />
              {isLoading ? "Applying..." : "Apply Scenario"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Custom Disaster Creator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Custom Disaster Creator
          </CardTitle>
          <CardDescription>
            Create custom disaster scenarios with specific parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Disaster Type Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Disaster Type</label>
              <Select 
                value={customForm.type} 
                onValueChange={(value) => setCustomForm({...customForm, type: value})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {disasterTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Affected Route</label>
              <Select 
                value={customForm.affected_route} 
                onValueChange={(value) => setCustomForm({...customForm, affected_route: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select route" />
                </SelectTrigger>
                <SelectContent>
                  {routes?.map(route => (
                    <SelectItem key={route.id} value={route.id}>
                      Route {route.id}
                    </SelectItem>
                  ))}
                  <SelectItem value="all">All Routes (Network-wide)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Duration and Severity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Duration: {customForm.duration_minutes} minutes
              </label>
              <Slider
                value={[customForm.duration_minutes]}
                onValueChange={([value]) => setCustomForm({...customForm, duration_minutes: value})}
                max={180}
                min={5}
                step={5}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>5 min</span>
                <span>3 hours</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Severity Level</label>
              <Select 
                value={customForm.severity} 
                onValueChange={(value) => setCustomForm({...customForm, severity: value})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {severityLevels.map(level => (
                    <SelectItem key={level.value} value={level.value}>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${level.color}`} />
                        {level.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Speed Reduction */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              Speed Reduction: {Math.round(customForm.speed_reduction * 100)}%
            </label>
            <Slider
              value={[customForm.speed_reduction]}
              onValueChange={([value]) => setCustomForm({...customForm, speed_reduction: value})}
              max={1.0}
              min={0.0}
              step={0.1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>No reduction</span>
              <span>100% (Complete stop)</span>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="text-sm font-medium mb-2 block">Description</label>
            <Textarea
              value={customForm.description}
              onChange={(e) => setCustomForm({...customForm, description: e.target.value})}
              placeholder="Describe the disaster scenario..."
              className="min-h-[80px]"
            />
          </div>

          {/* Add Custom Disaster Button */}
          <Button 
            onClick={addCustomDisaster}
            disabled={!customForm.affected_route || !customForm.description}
            className="w-full flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            {multipleMode ? "Add to Multiple Disasters" : "Create Custom Disaster"}
          </Button>
        </CardContent>
      </Card>

      {/* Active Custom Disasters */}
      {(customDisasters.length > 0 || simultaneousDisasters.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                {multipleMode ? "Simultaneous Disasters" : "Custom Disasters"}
              </div>
              {multipleMode && simultaneousDisasters.length > 0 && (
                <Button 
                  onClick={applyMultipleDisasters}
                  disabled={isLoading}
                  variant="destructive"
                  size="sm"
                >
                  Apply All ({simultaneousDisasters.length})
                </Button>
              )}
            </CardTitle>
            <CardDescription>
              {multipleMode 
                ? `${simultaneousDisasters.length} disasters ready to apply simultaneously`
                : "Created custom disaster scenarios"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(multipleMode ? simultaneousDisasters : customDisasters).map((disaster) => (
                <div key={disaster.id} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">{getDisasterIcon(disaster.type)}</span>
                        <h4 className="font-medium">{disaster.description}</h4>
                        <Badge 
                          variant="outline" 
                          className={`${getSeverityColor(disaster.severity)} text-white border-0`}
                        >
                          {disaster.severity}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          Route: {disaster.affected_route}
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Duration: {disaster.duration_minutes}m
                        </div>
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          Speed: -{Math.round(disaster.speed_reduction * 100)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      {!multipleMode && (
                        <Button
                          onClick={() => applyCustomDisaster(disaster)}
                          disabled={isLoading}
                          variant="destructive"
                          size="sm"
                        >
                          Apply
                        </Button>
                      )}
                      <Button
                        onClick={() => removeCustomDisaster(disaster.id)}
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Interactive Map Drawing (Placeholder) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Interactive Disaster Mapping
          </CardTitle>
          <CardDescription>
            Click on map sections to create location-specific disasters (Coming Soon)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center text-gray-500">
              <MapPin className="h-8 w-8 mx-auto mb-2" />
              <p className="text-sm">Interactive map drawing feature</p>
              <p className="text-xs">Click and drag to define affected areas</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdvancedDisasterManager;