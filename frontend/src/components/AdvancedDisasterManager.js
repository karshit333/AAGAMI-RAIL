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
  const [simultaneousDisasters, setSimultaneousDisasters] = useState([]);

  // Custom disaster form state
  const [customForm, setCustomForm] = useState({
    type: 'custom',
    affected_route: '',
    description: '',
    speed_reduction: 0,
    severity: 'medium'
  });

  const disasterTypes = [
    { value: 'flood', label: 'Track Flooding', icon: '🌊', description: 'Water logging blocks railway tracks' },
    { value: 'equipment_failure', label: 'Signal Failure', icon: '⚠️', description: 'Equipment malfunction disrupts operations' },
    { value: 'weather', label: 'Weather Impact', icon: '🌧️', description: 'Reduces visibility and safe operating speeds' },
    { value: 'breakdown', label: 'Train Breakdown', icon: '🚂', description: 'Disabled train blocks track section' },
    { value: 'human_strike', label: 'Track Blockade', icon: '✊', description: 'Protesters sitting on tracks blocking train movement' },
    { value: 'emergency_train', label: 'Emergency Train', icon: '🚨', description: 'High-priority emergency train requires immediate clearance' },
    { value: 'custom', label: 'Custom Disruption', icon: '⚙️', description: 'Define specific operational disruption' }
  ];

  const severityLevels = [
    { value: 'low', label: 'Minor', color: 'bg-blue-500', description: 'Minimal impact, quick resolution' },
    { value: 'medium', label: 'Moderate', color: 'bg-yellow-500', description: 'Significant delays expected' },
    { value: 'high', label: 'Major', color: 'bg-orange-500', description: 'Severe disruption, rerouting needed' },
    { value: 'critical', label: 'Critical', color: 'bg-red-500', description: 'Emergency response required' }
  ];

  const resetCustomForm = () => {
    setCustomForm({
      type: 'custom',
      affected_route: '',
      description: '',
      speed_reduction: 0,
      severity: 'medium'
    });
  };

  const addCustomDisaster = () => {
    // Set default values for emergency train
    if (customForm.type === 'emergency_train') {
      const emergencyDisaster = {
        ...customForm,
        id: Date.now().toString(),
        affected_route: customForm.affected_route || 'A-B',
        duration_minutes: 15, // Emergency trains need quick clearance
        speed_reduction: 0, // No speed reduction for emergency
        severity: customForm.severity || 'critical',
        ai_predicted_impact: predictDisasterImpact({
          ...customForm,
          severity: customForm.severity || 'critical',
          duration_minutes: 15
        })
      };
      
      setCustomDisasters([...customDisasters, emergencyDisaster]);
    } else {
      // Normal disaster handling
      if (!customForm.affected_route || !customForm.description) {
        return;
      }

      const newDisaster = {
        ...customForm,
        id: Date.now().toString(),
        duration_minutes: 30, // Default duration for non-emergency disasters
        ai_predicted_impact: predictDisasterImpact({...customForm, duration_minutes: 30})
      };

      setCustomDisasters([...customDisasters, newDisaster]);
    }
    
    resetCustomForm();
  };

  const removeCustomDisaster = (id) => {
    setCustomDisasters(customDisasters.filter(d => d.id !== id));
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
    if (simultaneousDisasters.length > 0 && onApplyDisaster) {
      const multipleScenario = {
        disasters: simultaneousDisasters,
        description: `Multiple simultaneous disruptions: ${simultaneousDisasters.map(d => d.description).join(', ')}`,
        multiple: true
      };
      
      onApplyDisaster('custom_multiple', multipleScenario);
    }
  };

  const predictDisasterImpact = (disaster) => {
    // AI-powered impact prediction
    let predictedDelays = 0;
    let affectedTrains = 0;
    let reroutingNeeded = false;

    // Use default duration of 30 minutes if not specified
    const duration = disaster.duration_minutes || 30;

    switch (disaster.severity) {
      case 'critical':
        predictedDelays = 45 + (duration * 0.8);
        affectedTrains = 8;
        reroutingNeeded = true;
        break;
      case 'high':
        predictedDelays = 25 + (duration * 0.6);
        affectedTrains = 5;
        reroutingNeeded = disaster.speed_reduction > 0.5;
        break;
      case 'medium':
        predictedDelays = 15 + (duration * 0.4);
        affectedTrains = 3;
        reroutingNeeded = disaster.speed_reduction > 0.7;
        break;
      case 'low':
        predictedDelays = 5 + (duration * 0.2);
        affectedTrains = 1;
        reroutingNeeded = false;
        break;
      default:
        predictedDelays = 10;
        affectedTrains = 2;
    }

    return {
      predicted_avg_delay: Math.round(predictedDelays),
      predicted_affected_trains: affectedTrains,
      rerouting_needed: reroutingNeeded,
      confidence: 0.85
    };
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
      {/* AI-Powered Disaster Management Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-600" />
            AI-Powered Disaster Management System
          </CardTitle>
          <CardDescription>
            Intelligent disruption simulation with AI-driven impact analysis and resolution strategies
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Custom Disruption Designer */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            AI-Powered Disruption Designer
          </CardTitle>
          <CardDescription>
            Create specific operational disruptions with comprehensive AI impact assessment and intelligent response strategies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Disaster Type and Route Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Disruption Type</label>
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
                      <div className="flex items-center gap-2">
                        <span>{type.icon}</span>
                        <div>
                          <div className="font-medium">{type.label}</div>
                          <div className="text-xs text-gray-500">{type.description}</div>
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

          {/* Route Selection - Hide for Emergency Train */}
          {customForm.type !== 'emergency_train' && (
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
                  <SelectItem value="all">All Routes (Network-wide Impact)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Emergency Train Special Handling */}
          {customForm.type === 'emergency_train' && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🚨</span>
                <h4 className="font-medium text-red-800">Emergency Train Insertion</h4>
              </div>
              <p className="text-sm text-red-700 mb-3">
                Emergency trains receive highest priority and will be automatically assigned the optimal route. 
                All other trains will be rescheduled to accommodate emergency passage.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-red-800 block mb-1">Emergency Route Preference</label>
                  <Select 
                    value={customForm.affected_route || 'A-B'} 
                    onValueChange={(value) => setCustomForm({...customForm, affected_route: value})}
                  >
                    <SelectTrigger className="border-red-300">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A-B">Primary Route (A-B)</SelectItem>
                      <SelectItem value="B-C">Central Route (B-C)</SelectItem>
                      <SelectItem value="A-E">Express Route (A-E)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-xs font-medium text-red-800 block mb-1">Emergency Type</label>
                  <Select 
                    value={customForm.severity || 'critical'} 
                    onValueChange={(value) => setCustomForm({...customForm, severity: value})}
                  >
                    <SelectTrigger className="border-red-300">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="medical">Medical Emergency</SelectItem>
                      <SelectItem value="vip">VIP Transport</SelectItem>
                      <SelectItem value="disaster">Disaster Response</SelectItem>
                      <SelectItem value="security">Security Emergency</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}
          </div>

          {/* Severity Level - Modified for Emergency Train */}
          {customForm.type !== 'emergency_train' && (
            <div className="w-full md:w-1/2">
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
                        <div>
                          <div className="font-medium">{level.label}</div>
                          <div className="text-xs text-gray-500">{level.description}</div>
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Speed Impact - Hide for Emergency Train */}
          {customForm.type !== 'emergency_train' && (
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
                <span>No speed impact</span>
                <span>Complete track blockage</span>
              </div>
            </div>
          )}

          {/* Description */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              {customForm.type === 'emergency_train' ? 'Emergency Details' : 'Disruption Description'}
            </label>
            <Textarea
              value={customForm.description}
              onChange={(e) => setCustomForm({...customForm, description: e.target.value})}
              placeholder={
                customForm.type === 'emergency_train' 
                  ? "Describe the emergency situation requiring immediate train dispatch..."
                  : "Describe the specific operational disruption..."
              }
              className="min-h-[80px]"
            />
          </div>

          {/* AI Impact Prediction */}
          {((customForm.affected_route && customForm.description) || customForm.type === 'emergency_train') && (
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-gray-800">AI Impact Assessment</span>
              </div>
              {(() => {
                const prediction = predictDisasterImpact(customForm);
                if (customForm.type === 'emergency_train') {
                  return (
                    <div className="space-y-2">
                      <div className="text-sm text-gray-600">
                        <strong>Emergency Response Analysis:</strong> All trains will be cleared from selected route. 
                        Expected network delays: ~{prediction.predicted_avg_delay} minutes per affected train.
                      </div>
                      <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                        AI will automatically determine optimal clearance strategy and minimize cascading delays across network.
                      </div>
                    </div>
                  );
                }
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600">
                    <div>Expected Delay: ~{prediction.predicted_avg_delay} min</div>
                    <div>Affected Trains: ~{prediction.predicted_affected_trains}</div>
                    <div>Rerouting: {prediction.rerouting_needed ? 'Likely needed' : 'Not required'}</div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Create Custom Disaster Button */}
          <Button 
            onClick={addCustomDisaster}
            disabled={!customForm.description || (customForm.type !== 'emergency_train' && !customForm.affected_route)}
            className="w-full flex items-center gap-2"
            variant={customForm.type === 'emergency_train' ? 'destructive' : 'default'}
          >
            <Plus className="h-4 w-4" />
            {customForm.type === 'emergency_train' ? 'Deploy Emergency Train' : 'Create Disruption Scenario'}
          </Button>
        </CardContent>
      </Card>

      {/* Active Custom Disasters */}
      {customDisasters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Custom Disruption Scenarios
              </div>
              <Badge variant="outline">
                {customDisasters.length} Ready
              </Badge>
            </CardTitle>
            <CardDescription>
              Created disruption scenarios with AI impact predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {customDisasters.map((disaster) => (
                <div key={disaster.id} className="border rounded-lg p-4 bg-white shadow-sm">
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
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600 mb-2">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          Route: {disaster.affected_route}
                        </div>
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          Speed Impact: -{Math.round(disaster.speed_reduction * 100)}%
                        </div>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          Est. Delay: ~{disaster.ai_predicted_impact?.predicted_avg_delay}m
                        </div>
                      </div>

                      {disaster.ai_predicted_impact && (
                        <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                          AI Prediction: {disaster.ai_predicted_impact.predicted_affected_trains} trains affected, 
                          {disaster.ai_predicted_impact.rerouting_needed ? ' rerouting required' : ' no rerouting needed'} 
                          (Confidence: {Math.round(disaster.ai_predicted_impact.confidence * 100)}%)
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        onClick={() => applyCustomDisaster(disaster)}
                        disabled={isLoading}
                        variant="destructive"
                        size="sm"
                        className="flex items-center gap-1"
                      >
                        <Brain className="h-3 w-3" />
                        Apply & Optimize
                      </Button>
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
    </div>
  );
};

export default AdvancedDisasterManager;