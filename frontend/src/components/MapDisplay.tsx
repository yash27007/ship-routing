import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import { useRouteStore } from '../stores/route'
import 'leaflet/dist/leaflet.css'
import '../styles/map.css'

interface MapDisplayProps {
    routeStatus?: {
        status: string
        current_algorithm: string
        progress: number
        waypoints_found: number
        is_rerouting: boolean
        message: string
    } | null
}

// Fix Leaflet default icons
const defaultIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
})

L.Marker.prototype.setIcon(defaultIcon)

export default function MapDisplay({ routeStatus }: MapDisplayProps) {
    const { currentRoute, isCalculating } = useRouteStore()

    if (!currentRoute) {
        return (
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6 mb-6 h-96 flex items-center justify-center">
                <p className="text-slate-500 dark:text-slate-400">Calculate a route to see it on the map</p>
            </div>
        )
    }

    const startLat = currentRoute.start_lat
    const startLon = currentRoute.start_lon
    const endLat = currentRoute.end_lat
    const endLon = currentRoute.end_lon
    const waypoints = currentRoute.waypoints || []

    // Calculate center of map
    const centerLat = (startLat + endLat) / 2
    const centerLon = (startLon + endLon) / 2

    // Convert waypoints to [lat, lon] format
    const routeCoordinates: [number, number][] = waypoints.map((wp) => [wp.latitude, wp.longitude])

    return (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg overflow-hidden mb-6">
            <div className="h-screen w-full relative">
                <MapContainer
                    center={[centerLat, centerLon]}
                    zoom={4}
                    style={{ height: '100%', width: '100%' }}
                    className="z-10"
                >
                    {/* OpenStreetMap tiles */}
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />

                    {/* Start Port Marker */}
                    <Marker position={[startLat, startLon]} icon={defaultIcon}>
                        <Popup className="font-bold">
                            Start Port<br />
                            Lat: {startLat.toFixed(2)}, Lon: {startLon.toFixed(2)}
                        </Popup>
                    </Marker>

                    {/* End Port Marker */}
                    <Marker position={[endLat, endLon]} icon={defaultIcon}>
                        <Popup className="font-bold">
                            End Port<br />
                            Lat: {endLat.toFixed(2)}, Lon: {endLon.toFixed(2)}
                        </Popup>
                    </Marker>

                    {/* Route Path */}
                    <Polyline
                        positions={routeCoordinates}
                        color="#3b82f6"
                        weight={3}
                        opacity={0.8}
                        dashArray="5, 5"
                    />

                    {/* Waypoints */}
                    {routeCoordinates.map((coord, idx) => (
                        <CircleMarker
                            key={idx}
                            center={coord}
                            radius={5}
                            fill={true}
                            fillColor="#10b981"
                            fillOpacity={0.7}
                            color="#059669"
                            weight={2}
                            opacity={0.8}
                        >
                            <Popup>
                                Waypoint {idx + 1}<br />
                                Lat: {coord[0].toFixed(2)}, Lon: {coord[1].toFixed(2)}
                            </Popup>
                        </CircleMarker>
                    ))}
                </MapContainer>

                {/* Route Calculation Overlay */}
                {isCalculating && routeStatus && (
                    <div className="absolute top-4 right-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg p-4 z-20 max-w-sm">
                        <div className="flex items-center gap-3 mb-3">
                            <div className={`w-3 h-3 rounded-full animate-pulse ${routeStatus.current_algorithm === 'RRT*' ? 'bg-green-500' : 'bg-orange-500'
                                }`}></div>
                            <div>
                                <h4 className="font-semibold text-slate-900 dark:text-white">
                                    {routeStatus.current_algorithm} Active
                                </h4>
                                <p className="text-xs text-slate-600 dark:text-slate-400 capitalize">
                                    {routeStatus.status}
                                </p>
                            </div>
                        </div>

                        <div className="mb-3">
                            <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400 mb-1">
                                <span>Progress</span>
                                <span>{routeStatus.progress.toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                                <div
                                    className={`h-2 rounded-full transition-all duration-500 ${routeStatus.current_algorithm === 'RRT*'
                                            ? 'bg-gradient-to-r from-green-400 to-green-600'
                                            : 'bg-gradient-to-r from-orange-400 to-orange-600'
                                        }`}
                                    style={{ width: `${routeStatus.progress}%` }}
                                ></div>
                            </div>
                        </div>

                        {routeStatus.is_rerouting && (
                            <div className="bg-orange-100 dark:bg-orange-900 border border-orange-300 dark:border-orange-700 rounded p-2 mb-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-orange-600 dark:text-orange-400">🔄</span>
                                    <span className="text-xs font-medium text-orange-800 dark:text-orange-200">
                                        D* Rerouting Active
                                    </span>
                                </div>
                            </div>
                        )}

                        <div className="text-xs text-slate-600 dark:text-slate-400">
                            <p><strong>Waypoints:</strong> {routeStatus.waypoints_found}</p>
                            <p className="mt-1 italic">{routeStatus.message}</p>
                        </div>
                    </div>
                )}

                {/* Algorithm Legend */}
                <div className="absolute top-4 left-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg p-3 z-20">
                    <div className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Algorithms</div>
                    <div className="space-y-1 text-xs">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span className="text-slate-600 dark:text-slate-400">RRT* - Global Planning</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                            <span className="text-slate-600 dark:text-slate-400">D* - Dynamic Rerouting</span>
                        </div>
                    </div>
                </div>

                {/* Legend */}
                <div className="absolute bottom-4 left-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg p-4 z-20">
                    <div className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Route Legend</div>
                    <div className="space-y-2 text-xs">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-blue-500 rounded-full border border-blue-600"></div>
                            <span className="text-slate-600 dark:text-slate-400">Route Path</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-green-500 rounded-full border border-green-600"></div>
                            <span className="text-slate-600 dark:text-slate-400">Waypoints</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                            <span className="text-slate-600 dark:text-slate-400">Start/End Ports</span>
                        </div>
                    </div>

                    {/* Route Info */}
                    <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-600">
                        <div className="text-xs text-slate-600 dark:text-slate-400">
                            <p className="font-semibold text-slate-900 dark:text-white mb-1">Route Info</p>
                            <p>Distance: {currentRoute.total_distance} nm</p>
                            <p>Time: {currentRoute.estimated_time_hours} hrs</p>
                            <p>Waypoints: {routeCoordinates.length}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
