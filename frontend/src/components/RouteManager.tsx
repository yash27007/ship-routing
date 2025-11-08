import { useState, useEffect } from 'react'
import { routeApi } from '../services/api'
import { useRouteStore } from '../stores/route'
import { MAJOR_PORTS, getPortLabel, type Port } from '../data/ports'
import MapDisplay from './MapDisplay'

interface RouteStatus {
    route_id: string
    status: string
    current_algorithm: string
    progress: number
    waypoints_found: number
    is_rerouting: boolean
    rerouting_reason: string | null
    estimated_completion_seconds: number
    message: string
}

export default function RouteManager() {
    const [startPort, setStartPort] = useState<Port>(MAJOR_PORTS[0])
    const [endPort, setEndPort] = useState<Port>(MAJOR_PORTS[1])
    const [vesselType, setVesselType] = useState('container_ship')
    const [error, setError] = useState('')
    const [routeStatus, setRouteStatus] = useState<RouteStatus | null>(null)
    const [currentRouteId, setCurrentRouteId] = useState<string | null>(null)
    const { setCurrentRoute, addToHistory, setIsCalculating, isCalculating } = useRouteStore()

    // Poll for route status during calculation
    useEffect(() => {
        let interval: number | null = null

        if (currentRouteId && isCalculating) {
            interval = window.setInterval(async () => {
                try {
                    const status = await routeApi.getRouteStatus(currentRouteId)
                    setRouteStatus(status.data)

                    // Stop polling if calculation is complete
                    if (status.data.status === 'completed' || status.data.status === 'failed') {
                        setIsCalculating(false)
                        setCurrentRouteId(null)
                        if (interval) clearInterval(interval)
                    }
                } catch (err) {
                    console.error('Failed to get route status:', err)
                }
            }, 1000) // Poll every second
        }

        return () => {
            if (interval) clearInterval(interval)
        }
    }, [currentRouteId, isCalculating, setIsCalculating])

    const handleCalculate = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setIsCalculating(true)

        // Generate unique route ID for status tracking
        const routeId = `route_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        setCurrentRouteId(routeId)

        // Initialize status
        setRouteStatus({
            route_id: routeId,
            status: 'initializing',
            current_algorithm: 'RRT*',
            progress: 0,
            waypoints_found: 0,
            is_rerouting: false,
            rerouting_reason: null,
            estimated_completion_seconds: 30,
            message: 'Initializing route calculation...'
        })

        try {
            // Always use RRT* first for initial planning
            const response = await routeApi.calculateRoute(
                startPort.lat,
                startPort.lon,
                endPort.lat,
                endPort.lon,
                vesselType,
                'rrt_star'  // Use RRT* for initial global route planning
            )

            // Add start/end coordinates to response
            const routeData = {
                ...response.data,
                start_lat: startPort.lat,
                start_lon: startPort.lon,
                end_lat: endPort.lat,
                end_lon: endPort.lon
            }

            setCurrentRoute(routeData)
            addToHistory(routeData)

            // Mark as completed
            setRouteStatus(prev => prev ? {
                ...prev,
                status: 'completed',
                progress: 100,
                message: 'Route calculation completed successfully!'
            } : null)

        } catch (err) {
            setError('Failed to calculate route. Please try again.')
            console.error(err)

            setRouteStatus(prev => prev ? {
                ...prev,
                status: 'failed',
                message: 'Route calculation failed. Please try again.'
            } : null)
        } finally {
            setIsCalculating(false)
            setCurrentRouteId(null)
        }
    }

    return (
        <div className="space-y-6">
            {/* Route Calculator */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Ship Route Planner</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">
                    Select ports and vessel type. RRT* handles initial planning, D* handles dynamic re-routing on weather changes.
                </p>

                <form onSubmit={handleCalculate} className="space-y-6">
                    {/* Port Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                                Starting Port
                            </label>
                            <select
                                value={startPort.code}
                                onChange={(e) => {
                                    const port = MAJOR_PORTS.find(p => p.code === e.target.value)
                                    if (port) setStartPort(port)
                                }}
                                className="w-full px-4 py-3 border-2 border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
                            >
                                {MAJOR_PORTS.map((port) => (
                                    <option key={port.code} value={port.code}>
                                        {getPortLabel(port)}
                                    </option>
                                ))}
                            </select>
                            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                                Lat: {startPort.lat.toFixed(2)}, Lon: {startPort.lon.toFixed(2)}
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                                Destination Port
                            </label>
                            <select
                                value={endPort.code}
                                onChange={(e) => {
                                    const port = MAJOR_PORTS.find(p => p.code === e.target.value)
                                    if (port) setEndPort(port)
                                }}
                                className="w-full px-4 py-3 border-2 border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
                            >
                                {MAJOR_PORTS.map((port) => (
                                    <option key={port.code} value={port.code}>
                                        {getPortLabel(port)}
                                    </option>
                                ))}
                            </select>
                            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                                Lat: {endPort.lat.toFixed(2)}, Lon: {endPort.lon.toFixed(2)}
                            </p>
                        </div>
                    </div>

                    {/* Vessel Type Selection */}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                            Vessel Type
                        </label>
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                            {[
                                { value: 'container_ship', label: 'Container' },
                                { value: 'bulk_carrier', label: 'Bulk Carrier' },
                                { value: 'tanker', label: 'Tanker' },
                                { value: 'general_cargo', label: 'General Cargo' },
                                { value: 'roro_ship', label: 'RoRo Ship' }
                            ].map((type) => (
                                <button
                                    key={type.value}
                                    type="button"
                                    onClick={() => setVesselType(type.value)}
                                    className={`py-3 px-4 rounded-lg font-medium transition ${vesselType === type.value
                                        ? 'bg-blue-600 text-white shadow-lg'
                                        : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-600'
                                        }`}
                                >
                                    {type.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Algorithm Info Box */}
                    <div className="bg-blue-50 dark:bg-blue-900 border-l-4 border-blue-500 p-4 rounded">
                        <p className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                            Intelligent Algorithm Selection
                        </p>
                        <p className="text-xs text-blue-800 dark:text-blue-200 mt-2">
                            <strong>RRT*:</strong> Global route planning for optimal initial path<br />
                            <strong>D*:</strong> Activated automatically on weather changes for dynamic re-routing
                        </p>
                    </div>

                    {/* Real-time Route Status */}
                    {routeStatus && isCalculating && (
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
                                    Route Calculation in Progress
                                </h3>
                                <div className="flex items-center gap-2">
                                    <span className={`inline-block w-3 h-3 rounded-full animate-pulse ${routeStatus.current_algorithm === 'RRT*' ? 'bg-green-500' : 'bg-orange-500'
                                        }`}></span>
                                    <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                                        {routeStatus.current_algorithm}
                                    </span>
                                </div>
                            </div>

                            {/* Progress Bar */}
                            <div className="mb-4">
                                <div className="flex justify-between text-sm text-blue-700 dark:text-blue-300 mb-2">
                                    <span>Progress: {routeStatus.progress.toFixed(1)}%</span>
                                    <span>ETA: {routeStatus.estimated_completion_seconds}s</span>
                                </div>
                                <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-3">
                                    <div
                                        className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-500 ease-out"
                                        style={{ width: `${routeStatus.progress}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Status Details */}
                            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                                <div>
                                    <span className="text-blue-600 dark:text-blue-400 font-medium">Waypoints Found:</span>
                                    <span className="ml-2 text-blue-900 dark:text-blue-100">{routeStatus.waypoints_found}</span>
                                </div>
                                <div>
                                    <span className="text-blue-600 dark:text-blue-400 font-medium">Status:</span>
                                    <span className="ml-2 text-blue-900 dark:text-blue-100 capitalize">{routeStatus.status}</span>
                                </div>
                            </div>

                            {/* Rerouting Alert */}
                            {routeStatus.is_rerouting && (
                                <div className="bg-orange-100 dark:bg-orange-900 border border-orange-300 dark:border-orange-700 rounded-lg p-3 mb-4">
                                    <div className="flex items-center gap-2">
                                        <span className="text-orange-600 dark:text-orange-400 text-lg">🔄</span>
                                        <div>
                                            <p className="font-medium text-orange-800 dark:text-orange-200">
                                                D* Dynamic Rerouting Active
                                            </p>
                                            {routeStatus.rerouting_reason && (
                                                <p className="text-sm text-orange-700 dark:text-orange-300">
                                                    Reason: {routeStatus.rerouting_reason}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Current Message */}
                            <p className="text-sm text-blue-800 dark:text-blue-200 italic">
                                {routeStatus.message}
                            </p>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg flex items-start gap-3">
                            <span className="text-lg">⚠</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Calculate Button */}
                    <button
                        type="submit"
                        disabled={isCalculating}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition shadow-lg disabled:opacity-50 disabled:bg-slate-400"
                    >
                        {isCalculating ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="inline-block animate-spin">⚙</span>
                                {routeStatus ? (
                                    `${routeStatus.current_algorithm} Planning... ${routeStatus.progress.toFixed(0)}%`
                                ) : (
                                    'Calculating Optimal Route...'
                                )}
                            </span>
                        ) : (
                            'Calculate Optimal Route'
                        )}
                    </button>
                </form>
            </div>

            {/* Map Display with Route Status */}
            <MapDisplay routeStatus={routeStatus} />
        </div>
    )
}