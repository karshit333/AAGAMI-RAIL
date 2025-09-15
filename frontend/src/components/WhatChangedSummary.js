import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { 
  TrendingUp, 
  TrendingDown, 
  Brain, 
  CheckCircle, 
  AlertTriangle,
  Route,
  Clock,
  Users,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Target
} from "lucide-react";

const WhatChangedSummary = ({ whatChanged, isVisible = true }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!whatChanged || !isVisible) {
    return null;
  }

  const {
    ai_decisions,
    impact_analysis,
    insights,
    recommendations,
    summary_stats
  } = whatChanged;

  const getImpactIcon = (impact) => {
    switch (impact) {
      case 'positive':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'negative':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <TrendingUp className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'positive':
        return 'border-green-200 bg-green-50';
      case 'negative':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-yellow-200 bg-yellow-50';
    }
  };

  const getEffectivenessColor = (effectiveness) => {
    if (effectiveness >= 80) return 'text-green-600';
    if (effectiveness >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEffectivenessBadge = (effectiveness) => {
    if (effectiveness >= 80) return 'default';
    if (effectiveness >= 60) return 'secondary';
    return 'destructive';
  };

  return (
    <Card className={`${getImpactColor(impact_analysis.overall_impact)} transition-all duration-300`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-600" />
            What Changed? - AI Analysis
            {getImpactIcon(impact_analysis.overall_impact)}
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={getEffectivenessBadge(summary_stats.optimization_effectiveness)}>
              {summary_stats.optimization_effectiveness}% Effective
            </Badge>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="ml-2"
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </CardTitle>
        <CardDescription>
          Comprehensive analysis of AI optimization decisions and their impact
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Impact Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Delay Impact</span>
            </div>
            <div className={`text-lg font-bold ${
              summary_stats.total_delay_change <= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {summary_stats.total_delay_change > 0 ? '+' : ''}{summary_stats.total_delay_change} min
            </div>
            <div className="text-xs text-gray-600">
              {impact_analysis.delay_impact.description}
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center gap-2 mb-1">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">On-Time Performance</span>
            </div>
            <div className={`text-lg font-bold ${
              summary_stats.on_time_change >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {summary_stats.on_time_change > 0 ? '+' : ''}{summary_stats.on_time_change} trains
            </div>
            <div className="text-xs text-gray-600">
              {impact_analysis.on_time_performance.description}
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Route className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Operational Changes</span>
            </div>
            <div className="text-lg font-bold text-blue-600">
              {impact_analysis.operational_changes.total_affected}
            </div>
            <div className="text-xs text-gray-600">
              trains affected ({summary_stats.rerouted_trains} rerouted)
            </div>
          </div>
        </div>

        {/* AI Insights */}
        {insights && insights.length > 0 && (
          <div className="space-y-2">
            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <Lightbulb className="h-4 w-4" />
              AI Insights
            </h4>
            <div className="space-y-2">
              {insights.map((insight, index) => (
                <div key={index} className="text-sm p-2 bg-blue-50 border-l-4 border-blue-400 rounded">
                  {insight}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Expanded Details */}
        {isExpanded && (
          <>
            <Separator />
            
            {/* AI Decisions Breakdown */}
            <div className="space-y-4">
              <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <Brain className="h-4 w-4" />
                AI Decision Breakdown
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Rerouting Decisions */}
                {ai_decisions.rerouting_decisions && ai_decisions.rerouting_decisions.length > 0 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <h5 className="font-medium text-green-800 mb-2 flex items-center gap-2">
                      <Route className="h-4 w-4" />
                      Smart Rerouting ({ai_decisions.rerouting_decisions.length})
                    </h5>
                    <div className="space-y-1">
                      {ai_decisions.rerouting_decisions.slice(0, 3).map((decision, index) => (
                        <div key={index} className="text-xs text-green-700">
                          <strong>Train {decision.train}:</strong> {decision.action}
                          <div className="text-green-600 italic">{decision.reason}</div>
                        </div>
                      ))}
                      {ai_decisions.rerouting_decisions.length > 3 && (
                        <div className="text-xs text-green-600 italic">
                          +{ai_decisions.rerouting_decisions.length - 3} more rerouting decisions
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Delay Minimization */}
                {ai_decisions.delay_minimization && ai_decisions.delay_minimization.length > 0 && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h5 className="font-medium text-yellow-800 mb-2 flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Strategic Delays ({ai_decisions.delay_minimization.length})
                    </h5>
                    <div className="space-y-1">
                      {ai_decisions.delay_minimization.slice(0, 3).map((decision, index) => (
                        <div key={index} className="text-xs text-yellow-700">
                          <strong>Train {decision.train}:</strong> {decision.action}
                          <div className="text-yellow-600 italic">{decision.reason}</div>
                        </div>
                      ))}
                      {ai_decisions.delay_minimization.length > 3 && (
                        <div className="text-xs text-yellow-600 italic">
                          +{ai_decisions.delay_minimization.length - 3} more delay optimizations
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Recommendations */}
            {recommendations && recommendations.length > 0 && (
              <div className="space-y-2">
                <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                  <Target className="h-4 w-4" />
                  AI Recommendations
                </h4>
                <div className="space-y-2">
                  {recommendations.map((recommendation, index) => (
                    <div key={index} className="text-sm p-2 bg-purple-50 border-l-4 border-purple-400 rounded flex items-start gap-2">
                      <Target className="h-3 w-3 text-purple-600 mt-0.5 flex-shrink-0" />
                      {recommendation}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-700">{summary_stats.trains_processed}</div>
                <div className="text-xs text-gray-600">Trains Processed</div>
              </div>
              <div className="text-center">
                <div className={`text-lg font-bold ${getEffectivenessColor(summary_stats.optimization_effectiveness)}`}>
                  {summary_stats.optimization_effectiveness}%
                </div>
                <div className="text-xs text-gray-600">Optimization Score</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">{summary_stats.rerouted_trains}</div>
                <div className="text-xs text-gray-600">Smart Reroutes</div>
              </div>
              <div className="text-center">
                <div className={`text-lg font-bold ${
                  summary_stats.total_delay_change <= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {summary_stats.total_delay_change > 0 ? '+' : ''}{summary_stats.total_delay_change}
                </div>
                <div className="text-xs text-gray-600">Delay Change (min)</div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default WhatChangedSummary;