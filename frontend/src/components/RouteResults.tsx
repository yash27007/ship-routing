import { useRouteStore } from '../stores/route'

export default function RouteResults() {
    const { currentRoute } = useRouteStore()

    if (!currentRoute) {
        return null
    }

    // Backend returns fields like: total_distance_nm, fuel_consumption_tons, co2_emissions_tons, etc.
    const distance = currentRoute.total_distance_nm ?? currentRoute.total_distance ?? 0
    const distanceKm = currentRoute.total_distance_km ?? (distance * 1.852)
    const timeHrs = currentRoute.estimated_time_hours ?? 0
    const timeHms = currentRoute.estimated_time_hms ?? ''
    const fuelTons = currentRoute.fuel_consumption_tons ?? currentRoute.fuel_consumption ?? 0
    const fuelLiters = currentRoute.fuel_consumption_liters ?? null
    const fuelCostUSD = currentRoute.fuel_cost_usd ?? null
    const co2Tons = currentRoute.co2_emissions_tons ?? currentRoute.co2_emissions ?? 0
    const waypointsCount = currentRoute.waypoints?.length ?? 0

    return (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6 space-y-4">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Route Results</h2>

            {/* Main Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-4 rounded-lg">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300">Distance</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{Number(distance).toLocaleString(undefined, { maximumFractionDigits: 1 })} nm</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{Number(distanceKm).toLocaleString(undefined, { maximumFractionDigits: 0 })} km</div>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-4 rounded-lg">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300">Voyage Time</div>
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">{Number(timeHrs).toLocaleString(undefined, { maximumFractionDigits: 1 })} hrs</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{timeHms}</div>
                </div>

                <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900 dark:to-orange-800 p-4 rounded-lg">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300">Fuel Consumption</div>
                    <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{Number(fuelTons).toLocaleString(undefined, { maximumFractionDigits: 2 })} t</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{fuelLiters ? `${Number(fuelLiters).toLocaleString()} L` : ''}{fuelCostUSD ? ` • $${Number(fuelCostUSD).toLocaleString(undefined, { maximumFractionDigits: 0 })}` : ''}</div>
                </div>

                <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900 dark:to-red-800 p-4 rounded-lg">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300">CO₂ Emissions</div>
                    <div className="text-2xl font-bold text-red-600 dark:text-red-400">{Number(co2Tons).toLocaleString(undefined, { maximumFractionDigits: 2 })} t</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">{(Number(co2Tons) / 1000).toFixed(2)} kt CO₂</div>
                </div>
            </div>

            {/* Route efficiency & operating metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-50 dark:bg-slate-700 p-4 rounded-lg border border-slate-200 dark:border-slate-600">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Route Efficiency</div>
                    <div className="text-lg font-bold text-slate-900 dark:text-white">{currentRoute.distance_efficiency_percent ?? (currentRoute as unknown as Record<string, unknown>)['efficiency_percent'] ?? 0}%</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400">vs straight-line</div>
                </div>

                <div className="bg-slate-50 dark:bg-slate-700 p-4 rounded-lg border border-slate-200 dark:border-slate-600">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Operating Speed</div>
                    <div className="text-lg font-bold text-slate-900 dark:text-white">{currentRoute.operating_speed_knots ?? (currentRoute as unknown as Record<string, unknown>)['cruise_speed_knots'] ?? '--'} kts</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400">{currentRoute.speed_ratio_percent ?? ''}% of design</div>
                </div>

                <div className="bg-slate-50 dark:bg-slate-700 p-4 rounded-lg border border-slate-200 dark:border-slate-600">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Weather Factor</div>
                    <div className="text-lg font-bold text-slate-900 dark:text-white">{currentRoute.weather?.weather_factor?.toFixed(3) ?? '1.000'}x</div>
                    <div className="text-xs text-slate-600 dark:text-slate-400">{currentRoute.weather?.weather_source ?? ''}</div>
                </div>
            </div>

            {/* Algorithm & vessel details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900 dark:to-indigo-800 p-4 rounded-lg border border-indigo-200 dark:border-indigo-700">
                    <div className="text-sm font-medium text-indigo-700 dark:text-indigo-300 mb-3 flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-full ${String(currentRoute.algorithm_used ?? '').includes('rrt') ? 'bg-green-500' : 'bg-orange-500'
                            }`}></span>
                        Algorithm Performance
                    </div>
                    <div className="text-sm text-indigo-600 dark:text-indigo-400 space-y-2">
                        <div className="flex justify-between">
                            <span>Algorithm:</span>
                            <span className="font-medium">{String(currentRoute.algorithm_used ?? 'RRT*').replace(/_/g, ' ').toUpperCase()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Waypoints:</span>
                            <span className="font-medium">{waypointsCount}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Water-Only:</span>
                            <span className="font-medium text-green-600 dark:text-green-400">✓ Guaranteed</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Optimality:</span>
                            <span className="font-medium">
                                {currentRoute.algorithm_info?.asymptotically_optimal ? 'Asymptotically Optimal' : 'Heuristic'}
                            </span>
                        </div>
                    </div>

                    {/* Algorithm Features */}
                    <div className="mt-4 pt-3 border-t border-indigo-200 dark:border-indigo-600">
                        <div className="text-xs text-indigo-700 dark:text-indigo-300 font-medium mb-2">Features Used:</div>
                        <div className="flex flex-wrap gap-1">
                            <span className="px-2 py-1 bg-indigo-200 dark:bg-indigo-700 text-indigo-800 dark:text-indigo-200 rounded-md text-xs">
                                Water-Only Routing
                            </span>
                            {String(currentRoute.algorithm_used ?? '').includes('rrt') && (
                                <span className="px-2 py-1 bg-green-200 dark:bg-green-700 text-green-800 dark:text-green-200 rounded-md text-xs">
                                    Global Optimization
                                </span>
                            )}
                            {String(currentRoute.algorithm_used ?? '').includes('d_star') && (
                                <span className="px-2 py-1 bg-orange-200 dark:bg-orange-700 text-orange-800 dark:text-orange-200 rounded-md text-xs">
                                    Dynamic Rerouting
                                </span>
                            )}
                            <span className="px-2 py-1 bg-blue-200 dark:bg-blue-700 text-blue-800 dark:text-blue-200 rounded-md text-xs">
                                Weather Integration
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
                    <div className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Vessel Details</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400 space-y-1">
                        <p><strong>Vessel:</strong> {currentRoute.vessel_name ?? currentRoute.vessel_type ?? '—'}</p>
                        <p><strong>Design Speed:</strong> {currentRoute.design_speed_knots ?? '--'} knots</p>
                        <p><strong>Fuel per NM:</strong> {currentRoute.fuel_per_nm_actual ? `${Number(currentRoute.fuel_per_nm_actual).toFixed(4)} t/nm` : '--'}</p>
                    </div>
                </div>
            </div>

            {/* Environmental warnings */}
            {(currentRoute.monsoon_season?.warning || (currentRoute.cyclone_risk?.probability ?? 0) > 0) && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 p-4 rounded-lg">
                    <div className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">⚠️ Environmental Warnings</div>
                    <div className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                        {currentRoute.monsoon_season?.warning && (
                            <p><strong>Monsoon:</strong> {currentRoute.monsoon_season.warning} — Season: {currentRoute.monsoon_season.active_season}</p>
                        )}
                        {(currentRoute.cyclone_risk?.probability ?? 0) > 0 && (
                            <p><strong>Cyclone Risk:</strong> {(currentRoute.cyclone_risk.probability * 100).toFixed(1)}% — {currentRoute.cyclone_risk.recommendation}</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
