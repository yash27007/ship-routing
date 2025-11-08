import { create } from "zustand";

interface RouteData {
  start_lat: number;
  start_lon: number;
  end_lat: number;
  end_lon: number;
  waypoints: Array<{
    latitude: number;
    longitude: number;
    bearing: number;
    distance: number;
    waypoint_index: number;
  }>;
  total_distance_nm: number;
  total_distance_km: number;
  straight_line_distance_nm: number;
  distance_efficiency_percent: number;
  estimated_time_hours: number;
  estimated_time_days: number;
  estimated_time_hms: string;
  fuel_consumption_tons: number;
  fuel_consumption_liters: number;
  fuel_per_nm_actual: number;
  co2_emissions_tons: number;
  co2_emissions_kg: number;
  co2_per_nm: number;
  fuel_cost_usd: number;
  vessel_type: string;
  vessel_name: string;
  design_speed_knots: number;
  operating_speed_knots: number;
  speed_ratio_percent: number;
  speed_optimization_reason: string;
  weather: {
    weather_factor: number;
    average_wind_speed_knots: number;
    average_wave_height_m: number;
    average_current_speed_ms: number;
    weather_source: string;
  };
  weather_optimization_reason: string;
  monsoon_season: {
    active_season: string;
    warning: string;
  };
  cyclone_risk: {
    probability: number;
    recommendation: string;
  };
  algorithm_used: string;
  algorithm_info: {
    note: string;
    asymptotically_optimal: boolean;
    probabilistically_complete: boolean;
    bidirectional: boolean;
    forward_backward_search: boolean;
  };
  optimization_basis: {
    algorithm_name: string;
    optimization_method: string;
    convergence_guarantee: string;
    distance_efficiency_percent: number;
    fuel_efficiency_percent: number;
    why_optimal: string;
    mathematical_basis: string;
    rrt_star_iterations: number;
    rrt_star_convergence: string;
    d_star_readiness: string;
  };
  metrics: {
    computational_complexity: string;
    space_complexity: string;
    waypoint_count: number;
    rrt_iterations: number;
    convergence_status: string;
  };
  scientific_basis: {
    fuel_model: string;
    weather_data: string;
    resistance_formula: string;
    validation: string;
  };
  // Mapped properties for backward compatibility
  total_distance?: number;
  fuel_consumption?: number;
  co2_emissions?: number;
  weather_impact?: number;
}

interface RouteState {
  currentRoute: RouteData | null;
  routeHistory: RouteData[];
  isCalculating: boolean;
  setCurrentRoute: (route: RouteData | null) => void;
  addToHistory: (route: RouteData) => void;
  setIsCalculating: (calculating: boolean) => void;
  clearHistory: () => void;
}

export const useRouteStore = create<RouteState>((set) => ({
  currentRoute: null,
  routeHistory: [],
  isCalculating: false,
  setCurrentRoute: (route) => {
    if (route) {
      // Map new field names to old ones for backward compatibility
      route.total_distance = route.total_distance_nm;
      route.fuel_consumption = route.fuel_consumption_tons;
      route.co2_emissions = route.co2_emissions_tons;
      route.weather_impact = route.weather?.weather_factor || 1.0;
    }
    set({ currentRoute: route });
  },
  addToHistory: (route) =>
    set((state) => ({
      routeHistory: [route, ...state.routeHistory.slice(0, 19)],
    })),
  setIsCalculating: (calculating) => set({ isCalculating: calculating }),
  clearHistory: () => set({ routeHistory: [] }),
}));
