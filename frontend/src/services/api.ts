import axios from "axios";
import { useAuthStore } from "../stores/auth";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  register: (email: string, password: string) =>
    api.post("/auth/register", { email, password }),
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  getMe: () => api.get("/auth/me"),
};

export const routeApi = {
  calculateRoute: (
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    vesselType: string = "container_ship",
    algorithm: string = "rrt_star"
  ) =>
    api.post("/routes/calculate", undefined, {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon,
        vessel_type: vesselType,
        algorithm,
      },
    }),
  getVesselTypes: () => api.get("/routes/vessel-types"),
  getAlgorithmAnalysis: () => api.get("/routes/algorithm-analysis"),
  getRouteStatus: (routeId: string) => api.get(`/routes/status/${routeId}`),
  triggerReplanning: (routeId: string, obstacles: number[][] = []) =>
    api.post(`/routes/replan/${routeId}`, { obstacles }),
};

export const weatherApi = {
  getCurrentWeather: (latitude: number, longitude: number) =>
    api.get("/weather/current", { params: { latitude, longitude } }),
  getRouteWeather: (
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number
  ) =>
    api.get("/weather/route", {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon,
      },
    }),
};

export default api;
