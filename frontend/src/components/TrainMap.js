import React, { useState, useEffect } from 'react';

const TrainMap = ({ stations, routes, trains, getPriorityColor }) => {
  const [animatedTrains, setAnimatedTrains] = useState([]);

  useEffect(() => {
    // Initialize train positions for animation
    if (trains && routes) {
      const trainPositions = trains.map((train, index) => ({
        ...train,
        position: { x: 0, y: 0 },
        progress: (index * 0.1) % 1, // Stagger initial positions
        routeData: routes.find(r => r.id === train.route)
      }));
      setAnimatedTrains(trainPositions);
    }
  }, [trains, routes]);

  useEffect(() => {
    // Animation loop
    const interval = setInterval(() => {
      setAnimatedTrains(prevTrains => 
        prevTrains.map(train => {
          if (!train.routeData) return train;
          
          // Update progress (0 to 1 along the route)
          const newProgress = (train.progress + 0.01) % 1;
          
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
    }, 100);

    return () => clearInterval(interval);
  }, []);

  if (!stations || !routes || stations.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <p className="text-gray-500">Loading map data...</p>
      </div>
    );
  }

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
              <path
                d={`M ${route.path[0].x} ${route.path[0].y} ${route.path.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')}`}
                stroke="#6b7280"
                strokeWidth="3"
                fill="none"
                strokeDasharray="8,4"
                opacity="0.6"
              />
            )}
            {/* Route label */}
            {route.path.length >= 2 && (
              <text
                x={(route.path[0].x + route.path[route.path.length - 1].x) / 2}
                y={(route.path[0].y + route.path[route.path.length - 1].y) / 2 - 10}
                textAnchor="middle"
                fontSize="12"
                fill="#374151"
                fontWeight="500"
              >
                {route.id}
              </text>
            )}
          </g>
        ))}

        {/* Stations - Draw circles for each station */}
        {stations.map((station) => (
          <g key={station.id}>
            <circle
              cx={station.x}
              cy={station.y}
              r="20"
              fill="#ffffff"
              stroke="#3b82f6"
              strokeWidth="3"
            />
            <text
              x={station.x}
              y={station.y + 5}
              textAnchor="middle"
              fontSize="14"
              fontWeight="600"
              fill="#1f2937"
            >
              {station.name.split(' ')[1]}
            </text>
            <text
              x={station.x}
              y={station.y + 35}
              textAnchor="middle"
              fontSize="10"
              fill="#6b7280"
            >
              {station.name}
            </text>
          </g>
        ))}

        {/* Trains - Draw animated train positions */}
        {animatedTrains.map((train) => {
          if (!train.position || !train.routeData) return null;
          
          return (
            <g key={train.id}>
              <circle
                cx={train.position.x}
                cy={train.position.y}
                r="8"
                fill={getPriorityColor(train.priority)}
                stroke="#ffffff"
                strokeWidth="2"
                opacity="0.9"
              >
                <animate
                  attributeName="r"
                  values="8;10;8"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
              {/* Train ID label */}
              <text
                x={train.position.x}
                y={train.position.y - 15}
                textAnchor="middle"
                fontSize="8"
                fill="#1f2937"
                fontWeight="500"
              >
                {train.id.slice(0, 6)}
              </text>
              {/* Delay indicator */}
              {train.delay_minutes > 0 && (
                <text
                  x={train.position.x}
                  y={train.position.y + 20}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#dc2626"
                  fontWeight="600"
                >
                  +{train.delay_minutes}m
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Train Priority</h4>
        <div className="space-y-1">
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
      </div>

      {/* Network Info */}
      <div className="absolute bottom-4 left-4 bg-white bg-opacity-95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <h4 className="text-sm font-semibold text-gray-700 mb-1">Network Status</h4>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Stations: {stations.length}</div>
          <div>Routes: {routes.length}</div>
          <div>Active Trains: {animatedTrains.length}</div>
        </div>
      </div>
    </div>
  );
};

export default TrainMap;