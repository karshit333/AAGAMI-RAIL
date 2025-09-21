import React, { useState, useEffect } from 'react';

const TrainMap = ({ stations, routes, trains, getPriorityColor, onTrainClick }) => {
  const [animatedTrains, setAnimatedTrains] = useState([]);

  useEffect(() => {
    // Initialize train positions for animation
    if (trains && routes) {
      const trainPositions = trains.map((train, index) => {
        const routeId = train.rerouted ? train.new_route : train.route;
        const routeData = routes.find(r => r.id === routeId);
        
        return {
          ...train,
          position: { x: 0, y: 0 },
          progress: (index * 0.1) % 1, // Stagger initial positions
          routeData: routeData,
          actualRoute: routeId
        };
      });
      setAnimatedTrains(trainPositions);
    }
  }, [trains, routes]);

  useEffect(() => {
    // Animation loop
    const interval = setInterval(() => {
      setAnimatedTrains(prevTrains => 
        prevTrains.map(train => {
          if (!train.routeData) return train;
          
          // Slower animation for delayed trains
          const speedMultiplier = train.delay_minutes > 0 ? 0.5 : 1.0;
          const progressIncrement = 0.008 * speedMultiplier;
          
          // Update progress (0 to 1 along the route)
          const newProgress = (train.progress + progressIncrement) % 1;
          
          // Calculate position along route path
          const pathLength = train.routeData.path.length;
          if (pathLength < 2) return { ...train, progress: newProgress };
          
          const segmentIndex = Math.floor(newProgress * (pathLength - 1));
          const segmentProgress = (newProgress * (pathLength - 1)) % 1;
          
          const currentPoint = train.routeData.path[segmentIndex];
          const nextPoint = train.routeData.path[Math.min(segmentIndex + 1, pathLength - 1)];
          
          const x = currentPoint.x + (nextPoint.x - currentPoint.x) * segmentProgress;
          const y = currentPoint.y + (nextPoint.y - currentPoint.y) * segmentProgress;
          
          return {
            ...train,
            progress: newProgress,
            position: { x, y }
          };
        })
      );
    }, 150);

    return () => clearInterval(interval);
  }, []);

  if (!stations || !routes || stations.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <p className="text-gray-500">Loading map data...</p>
      </div>
    );
  }

  // Get blocked routes
  const blockedRoutes = routes.filter(route => route.blocked);
  const slowRoutes = routes.filter(route => route.speed_reduction > 0);

  return (
    <div className="relative w-full h-96 bg-gradient-to-br from-blue-50 to-gray-50 rounded-lg border overflow-hidden">
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 800 300"
        className="absolute inset-0"
      >
        {/* Routes - Draw lines between stations */}
        {routes.map((route) => (
          <g key={route.id}>
            {route.path.length >= 2 && (
              <>
                {/* Main route line */}
                <path
                  d={`M ${route.path[0].x} ${route.path[0].y} ${route.path.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')}`}
                  stroke={route.blocked ? "#1f2937" : route.speed_reduction > 0 ? "#fbbf24" : "#6b7280"}
                  strokeWidth={route.blocked ? "6" : route.speed_reduction > 0 ? "5" : "4"}
                  fill="none"
                  strokeDasharray={route.blocked ? "0" : route.speed_reduction > 0 ? "8,4" : "8,4"}
                  opacity={route.blocked ? "0.9" : route.speed_reduction > 0 ? "0.8" : "0.6"}
                />
                
                {/* Blocked route indicator */}
                {route.blocked && (
                  <>
                    <text
                      x={(route.path[0].x + route.path[route.path.length - 1].x) / 2}
                      y={(route.path[0].y + route.path[route.path.length - 1].y) / 2 - 20}
                      textAnchor="middle"
                      fontSize="11"
                      fill="#ffffff"
                      fontWeight="700"
                      className="animate-pulse"
                    >
                      ❌ BLOCKED
                    </text>
                    {/* Dark overlay for blocked routes */}
                    <path
                      d={`M ${route.path[0].x} ${route.path[0].y} ${route.path.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')}`}
                      stroke="#000000"
                      strokeWidth="3"
                      fill="none"
                      opacity="0.7"
                    />
                  </>
                )}
                
                {/* Speed reduction indicator */}
                {route.speed_reduction > 0 && !route.blocked && (
                  <text
                    x={(route.path[0].x + route.path[route.path.length - 1].x) / 2}
                    y={(route.path[0].y + route.path[route.path.length - 1].y) / 2 - 20}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#d97706"
                    fontWeight="600"
                  >
                    ⚠️ SLOW -{Math.round(route.speed_reduction * 100)}%
                  </text>
                )}
              </>
            )}
            
            {/* Route label */}
            {route.path.length >= 2 && !route.blocked && route.speed_reduction === 0 && (
              <text
                x={(route.path[0].x + route.path[route.path.length - 1].x) / 2}
                y={(route.path[0].y + route.path[route.path.length - 1].y) / 2 - 10}
                textAnchor="middle"
                fontSize="11"
                fill="#374151"
                fontWeight="500"
              >
                {route.id}
              </text>
            )}
          </g>
        ))}

        {/* Rerouted paths - show in bright yellow with enhanced visibility */}
        {animatedTrains.filter(train => train.rerouted).map((train, index) => {
          if (!train.routeData || train.routeData.path.length < 2) return null;
          
          return (
            <g key={`reroute-${index}`}>
              {/* Enhanced rerouted path with glow effect */}
              <path
                d={`M ${train.routeData.path[0].x} ${train.routeData.path[0].y} ${train.routeData.path.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')}`}
                stroke="#fbbf24"
                strokeWidth="8"
                fill="none"
                opacity="0.3"
              />
              <path
                d={`M ${train.routeData.path[0].x} ${train.routeData.path[0].y} ${train.routeData.path.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')}`}
                stroke="#f59e0b"
                strokeWidth="4"
                fill="none"
                strokeDasharray="6,3"
                opacity="0.9"
              />
              {/* Rerouted route label */}
              <text
                x={(train.routeData.path[0].x + train.routeData.path[train.routeData.path.length - 1].x) / 2}
                y={(train.routeData.path[0].y + train.routeData.path[train.routeData.path.length - 1].y) / 2 + 15}
                textAnchor="middle"
                fontSize="9"
                fill="#d97706"
                fontWeight="600"
              >
                🔄 REROUTED VIA {train.new_route}
              </text>
            </g>
          );
        })}

        {/* Stations - Draw circles for each station */}
        {stations.map((station) => (
          <g key={station.id}>
            <circle
              cx={station.x}
              cy={station.y}
              r="22"
              fill="#ffffff"
              stroke="#3b82f6"
              strokeWidth="3"
              className="drop-shadow-sm"
            />
            <text
              x={station.x}
              y={station.y + 5}
              textAnchor="middle"
              fontSize="14"
              fontWeight="600"
              fill="#1f2937"
            >
              {station.id}
            </text>
            <text
              x={station.x}
              y={station.y + 38}
              textAnchor="middle"
              fontSize="9"
              fill="#6b7280"
            >
              {station.name.split(' ')[0]}
            </text>
          </g>
        ))}

        {/* Trains - Draw animated train positions */}
        {animatedTrains.map((train) => {
          if (!train.position || !train.routeData) return null;
          
          const trainColor = getPriorityColor(train.priority).replace('bg-', '');
          let fillColor = '#6b7280';
          if (trainColor.includes('red')) fillColor = '#ef4444';
          else if (trainColor.includes('blue')) fillColor = '#3b82f6';
          else if (trainColor.includes('gray')) fillColor = '#6b7280';
          
          return (
            <g key={train.id} onClick={() => onTrainClick && onTrainClick(train.id)} className="cursor-pointer">
              {/* Train dot with priority color and enhanced styling */}
              <circle
                cx={train.position.x}
                cy={train.position.y}
                r="12"
                fill={fillColor}
                stroke="#ffffff"
                strokeWidth="3"
                opacity="0.95"
                className="drop-shadow-md hover:r-15 transition-all"
              >
                <animate
                  attributeName="r"
                  values={train.rerouted ? "12;15;12" : "12;14;12"}
                  dur={train.rerouted ? "2s" : "3s"}
                  repeatCount="indefinite"
                />
              </circle>
              
              {/* Special indicator for rerouted trains */}
              {train.rerouted && (
                <circle
                  cx={train.position.x}
                  cy={train.position.y}
                  r="18"
                  fill="none"
                  stroke="#fbbf24"
                  strokeWidth="2"
                  strokeDasharray="3,3"
                  opacity="0.7"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    values={`0 ${train.position.x} ${train.position.y}; 360 ${train.position.x} ${train.position.y}`}
                    dur="4s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}
              
              {/* Train ID label with enhanced visibility */}
              <text
                x={train.position.x}
                y={train.position.y - 22}
                textAnchor="middle"
                fontSize="9"
                fill="#1f2937"
                fontWeight="600"
                className="drop-shadow-sm"
              >
                {train.id.slice(0, 6)}
              </text>
              
              {/* Delay indicator with enhanced styling */}
              {train.delay_minutes > 0 && (
                <text
                  x={train.position.x}
                  y={train.position.y + 28}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#dc2626"
                  fontWeight="700"
                  className="animate-pulse"
                >
                  ⏰ +{train.delay_minutes}m
                </text>
              )}
              
              {/* Reroute indicator with improved visibility */}
              {train.rerouted && (
                <>
                  <circle
                    cx={train.position.x + 15}
                    cy={train.position.y - 15}
                    r="4"
                    fill="#fbbf24"
                    stroke="#ffffff"
                    strokeWidth="1"
                  />
                  <text
                    x={train.position.x + 15}
                    y={train.position.y - 12}
                    textAnchor="middle"
                    fontSize="6"
                    fill="#000000"
                    fontWeight="700"
                  >
                    R
                  </text>
                </>
              )}
              
              {/* Priority indicator */}
              {train.priority === 'High' && (
                <text
                  x={train.position.x}
                  y={train.position.y + 6}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#ffffff"
                  fontWeight="700"
                >
                  ★
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-95 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-xs">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Legend</h4>
        
        {/* Train Priority */}
        <div className="space-y-1 mb-3">
          <div className="text-xs font-medium text-gray-600">Train Priority:</div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-xs text-gray-600">High Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-xs text-gray-600">Medium Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500"></div>
            <span className="text-xs text-gray-600">Low Priority</span>
          </div>
        </div>

        {/* Route Status */}
        <div className="space-y-1">
          <div className="text-xs font-medium text-gray-600">Route Status:</div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-gray-400" style={{borderTop: '2px dashed'}}></div>
            <span className="text-xs text-gray-600">Normal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-black rounded"></div>
            <span className="text-xs text-gray-600">Blocked</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-yellow-500" style={{borderTop: '2px dashed'}}></div>
            <span className="text-xs text-gray-600">Speed Reduced</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-yellow-500" style={{borderTop: '3px dashed'}}></div>
            <span className="text-xs text-gray-600">Rerouted</span>
          </div>
        </div>
      </div>

      {/* Network Status */}
      <div className="absolute bottom-4 left-4 bg-white bg-opacity-95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <h4 className="text-sm font-semibold text-gray-700 mb-1">Network Status</h4>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Stations: {stations.length}</div>
          <div>Routes: {routes.length}</div>
          <div>Active Trains: {animatedTrains.length}</div>
          <div>Blocked Routes: {blockedRoutes.length}</div>
          <div>Speed Restricted: {slowRoutes.length}</div>
        </div>
      </div>
    </div>
  );
};

export default TrainMap;