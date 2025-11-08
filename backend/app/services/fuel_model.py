"""
Scientifically-Rigorous Fuel Consumption Model for Maritime Vessels

Based on:
- Vettor & Soares (2016): Development of a ship weather routing system
- Lin et al. (2013, 2015): Multi-dynamic elements in weather routing
- Molland et al. (2011): Ship resistance and propulsion

Non-linear fuel consumption: Fuel ∝ Speed³ (cubic relationship)
This accounts for resistance increasing exponentially with velocity
"""

from typing import Dict, Optional
from enum import Enum


class VesselType(Enum):
    """Standard vessel classifications for maritime routing."""
    
    CONTAINER_4000_TEU = "container_4000"
    CONTAINER_10000_TEU = "container_10000"
    CONTAINER_14000_TEU = "container_14000"
    
    BULK_CARRIER_50000 = "bulk_50k"
    BULK_CARRIER_75000 = "bulk_75k"
    
    TANKER_AFRAMAX = "tanker_aframax"
    TANKER_VLCC = "tanker_vlcc"
    
    GENERAL_CARGO = "general_cargo"
    RO_RO_SHIP = "roro"


class VesselSpecifications:
    """Vessel specifications database with real maritime data."""
    
    SPECIFICATIONS = {
        # Container Ships - Most economically important
        VesselType.CONTAINER_4000_TEU: {
            "name": "Container Ship 4000 TEU",
            "teu_capacity": 4000,
            "length_m": 228,
            "beam_m": 32.2,
            "draft_m": 10.5,
            "deadweight_t": 40000,
            "fuel_tank_capacity_t": 3000,
            
            # Propulsion
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 11980,
            "max_speed_knots": 20,
            "design_speed_knots": 17.5,
            
            # Fuel consumption at design speed (knots)
            "fuel_consumption_g_per_kWh": 168,  # grams per kWh
            "nominal_fuel_consumption_t_per_day": 58,
            
            # Hull characteristics (Froude analysis)
            "wetted_surface_m2": 6800,
            "block_coefficient": 0.58,  # Froude number factor
            
            # Wind/Wave sensitivity (empirical)
            "wave_sensitivity_factor": 1.2,  # Amplification in waves
        },
        
        VesselType.CONTAINER_10000_TEU: {
            "name": "Container Ship 10000 TEU",
            "teu_capacity": 10000,
            "length_m": 294,
            "beam_m": 32.8,
            "draft_m": 11.5,
            "deadweight_t": 85000,
            "fuel_tank_capacity_t": 4750,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 44544,
            "max_speed_knots": 20.5,
            "design_speed_knots": 19,
            
            "fuel_consumption_g_per_kWh": 172,
            "nominal_fuel_consumption_t_per_day": 220,
            
            "wetted_surface_m2": 9200,
            "block_coefficient": 0.60,
            "wave_sensitivity_factor": 1.3,
        },
        
        VesselType.CONTAINER_14000_TEU: {
            "name": "Container Ship 14000 TEU (Neo-Panamax)",
            "teu_capacity": 14000,
            "length_m": 400,
            "beam_m": 54,
            "draft_m": 12,
            "deadweight_t": 160000,
            "fuel_tank_capacity_t": 6000,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 49440,
            "max_speed_knots": 22,
            "design_speed_knots": 19.5,
            
            "fuel_consumption_g_per_kWh": 175,
            "nominal_fuel_consumption_t_per_day": 280,
            
            "wetted_surface_m2": 14000,
            "block_coefficient": 0.62,
            "wave_sensitivity_factor": 1.25,
        },
        
        # Bulk Carriers
        VesselType.BULK_CARRIER_50000: {
            "name": "Bulk Carrier 50000 DWT",
            "teu_capacity": 0,
            "length_m": 190,
            "beam_m": 30,
            "draft_m": 9.8,
            "deadweight_t": 50000,
            "fuel_tank_capacity_t": 2500,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 8550,
            "max_speed_knots": 15,
            "design_speed_knots": 14,
            
            "fuel_consumption_g_per_kWh": 162,
            "nominal_fuel_consumption_t_per_day": 42,
            
            "wetted_surface_m2": 5000,
            "block_coefficient": 0.75,  # Higher block coefficient - slower, more efficient
            "wave_sensitivity_factor": 1.15,
        },
        
        VesselType.BULK_CARRIER_75000: {
            "name": "Bulk Carrier 75000 DWT (Capesize)",
            "teu_capacity": 0,
            "length_m": 228,
            "beam_m": 32,
            "draft_m": 11.5,
            "deadweight_t": 75000,
            "fuel_tank_capacity_t": 3500,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 14000,
            "max_speed_knots": 14.5,
            "design_speed_knots": 13.5,
            
            "fuel_consumption_g_per_kWh": 160,
            "nominal_fuel_consumption_t_per_day": 65,
            
            "wetted_surface_m2": 7500,
            "block_coefficient": 0.78,
            "wave_sensitivity_factor": 1.18,
        },
        
        # Tankers
        VesselType.TANKER_AFRAMAX: {
            "name": "Tanker Aframax (40000 DWT)",
            "teu_capacity": 0,
            "length_m": 228,
            "beam_m": 32,
            "draft_m": 10.2,
            "deadweight_t": 40000,
            "fuel_tank_capacity_t": 2300,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 8000,
            "max_speed_knots": 15.5,
            "design_speed_knots": 14.5,
            
            "fuel_consumption_g_per_kWh": 165,
            "nominal_fuel_consumption_t_per_day": 38,
            
            "wetted_surface_m2": 5200,
            "block_coefficient": 0.76,
            "wave_sensitivity_factor": 1.20,
        },
        
        VesselType.TANKER_VLCC: {
            "name": "Tanker VLCC (300000 DWT)",
            "teu_capacity": 0,
            "length_m": 333,
            "beam_m": 60,
            "draft_m": 14.8,
            "deadweight_t": 300000,
            "fuel_tank_capacity_t": 8000,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 32000,
            "max_speed_knots": 15.5,
            "design_speed_knots": 15,
            
            "fuel_consumption_g_per_kWh": 158,
            "nominal_fuel_consumption_t_per_day": 210,
            
            "wetted_surface_m2": 18000,
            "block_coefficient": 0.82,  # Highest - massive cargo ships
            "wave_sensitivity_factor": 1.22,
        },
        
        # Other types
        VesselType.GENERAL_CARGO: {
            "name": "General Cargo Ship 26700 DWT",
            "teu_capacity": 0,
            "length_m": 175,
            "beam_m": 25.4,
            "draft_m": 9.5,
            "deadweight_t": 26700,
            "fuel_tank_capacity_t": 1800,
            
            "main_engine_type": "Diesel 4-Stroke",
            "main_engine_power_kw": 5000,
            "max_speed_knots": 16,
            "design_speed_knots": 14.5,
            
            "fuel_consumption_g_per_kWh": 170,
            "nominal_fuel_consumption_t_per_day": 31,
            
            "wetted_surface_m2": 3800,
            "block_coefficient": 0.65,
            "wave_sensitivity_factor": 1.25,
        },
        
        VesselType.RO_RO_SHIP: {
            "name": "Ro-Ro Ship 5000 CEU",
            "teu_capacity": 0,
            "length_m": 200,
            "beam_m": 25,
            "draft_m": 7.0,
            "deadweight_t": 15000,
            "fuel_tank_capacity_t": 2000,
            
            "main_engine_type": "Diesel 2-Stroke",
            "main_engine_power_kw": 12800,
            "max_speed_knots": 22,
            "design_speed_knots": 20,
            
            "fuel_consumption_g_per_kWh": 170,
            "nominal_fuel_consumption_t_per_day": 95,
            
            "wetted_surface_m2": 4500,
            "block_coefficient": 0.55,  # Lower - faster ships
            "wave_sensitivity_factor": 1.35,  # More sensitive to waves (higher draft)
        },
    }
    
    @classmethod
    def get_specs(cls, vessel_type: VesselType) -> Dict:
        """Get vessel specifications."""
        return cls.SPECIFICATIONS.get(vessel_type, {})


class FuelConsumptionModel:
    """
    Scientific fuel consumption model based on maritime research.
    
    Key Formula:
    Fuel_actual = Fuel_base × (V_actual / V_design)³ × f_weather
    
    Where:
    - Fuel_base: Fuel at design speed (t/day)
    - V_actual: Current operating speed (knots)
    - V_design: Design speed (knots)
    - f_weather: Weather impact factor (1.0 = calm water)
    """
    
    def __init__(self, vessel_type: VesselType):
        """Initialize model for specific vessel type."""
        self.vessel_type = vessel_type
        self.specs = VesselSpecifications.get_specs(vessel_type)
        
    def calculate_fuel_consumption(
        self,
        speed_knots: float,
        weather_factor: float = 1.0,
        load_factor: float = 1.0
    ) -> Dict:
        """
        Calculate actual fuel consumption given speed and weather.
        
        Args:
            speed_knots: Current operating speed (knots)
            weather_factor: Multiplier for weather (1.0 = calm)
            load_factor: Cargo load factor (0.0-1.0)
            
        Returns:
            Comprehensive fuel calculation with breakdown
        """
        
        design_speed = self.specs["design_speed_knots"]
        base_consumption = self.specs["nominal_fuel_consumption_t_per_day"]
        
        # Speed ratio cubed (non-linear relationship from resistance equation)
        # This is the key principle: doubling speed ~8x the fuel required
        speed_ratio = speed_knots / design_speed
        speed_factor = speed_ratio ** 3
        
        # Adjust for load (heavier = more fuel, but with efficiency gains from ballast)
        # Typical: 0.5-1.0 load factor
        load_adjusted = 0.6 + (0.4 * load_factor)  # 60-100% of base
        
        # Calculate components
        calm_water_consumption = base_consumption * speed_factor * load_adjusted
        weather_increased_consumption = calm_water_consumption * weather_factor
        
        # Co2 calculation (typical: 3.17 tons CO2 per ton fuel burned)
        co2_per_fuel = 3.17
        co2_emissions = weather_increased_consumption * co2_per_fuel
        
        return {
            "vessel_type": self.vessel_type.value,
            "vessel_name": self.specs["name"],
            
            "operating_parameters": {
                "speed_knots": speed_knots,
                "design_speed_knots": design_speed,
                "speed_ratio": round(speed_ratio, 3),
                "load_factor": load_factor,
                "weather_factor": weather_factor,
            },
            
            "fuel_consumption": {
                "base_consumption_t_day": base_consumption,
                "calm_water_consumption_t_day": round(calm_water_consumption, 2),
                "actual_consumption_t_day": round(weather_increased_consumption, 2),
                "unit": "metric_tons_per_day"
            },
            
            "emissions": {
                "co2_emissions_t_day": round(co2_emissions, 2),
                "unit": "metric_tons_CO2_per_day"
            },
            
            "efficiency": {
                "fuel_per_nm": round(weather_increased_consumption / 24 / design_speed, 4),
                "consumption_factor": round(speed_factor, 3),
                "note": "Fuel consumption is cubic function of speed"
            }
        }
    
    def estimate_voyage_fuel(
        self,
        distance_nm: float,
        avg_speed_knots: float,
        weather_factor: float = 1.0,
        load_factor: float = 1.0
    ) -> Dict:
        """
        Estimate total fuel consumption for a voyage.
        
        Args:
            distance_nm: Total distance (nautical miles)
            avg_speed_knots: Average speed over voyage
            weather_factor: Overall weather impact
            load_factor: Cargo load factor
            
        Returns:
            Voyage-level fuel estimation
        """
        
        # Calculate daily consumption
        daily_consumption = self.calculate_fuel_consumption(
            avg_speed_knots, weather_factor, load_factor
        )
        
        # Estimate voyage time
        voyage_time_hours = (distance_nm / avg_speed_knots) if avg_speed_knots > 0 else 0
        voyage_time_days = voyage_time_hours / 24
        
        # Total fuel needed
        total_fuel_tons = daily_consumption["fuel_consumption"]["actual_consumption_t_day"] * voyage_time_days
        total_co2_tons = daily_consumption["emissions"]["co2_emissions_t_day"] * voyage_time_days
        
        # Tank requirements
        fuel_tank_capacity = self.specs["fuel_tank_capacity_t"]
        tanks_needed = total_fuel_tons / fuel_tank_capacity if fuel_tank_capacity > 0 else 0
        sufficient_fuel = total_fuel_tons <= fuel_tank_capacity
        
        return {
            "vessel_type": self.vessel_type.value,
            "voyage_parameters": {
                "distance_nm": distance_nm,
                "avg_speed_knots": avg_speed_knots,
                "weather_factor": weather_factor,
                "load_factor": load_factor,
            },
            
            "voyage_estimates": {
                "estimated_time_days": round(voyage_time_days, 2),
                "estimated_time_hours": round(voyage_time_hours, 1),
                "total_fuel_tons": round(total_fuel_tons, 2),
                "daily_consumption_tons": round(
                    daily_consumption["fuel_consumption"]["actual_consumption_t_day"], 2
                ),
            },
            
            "emissions": {
                "total_co2_tons": round(total_co2_tons, 2),
                "daily_co2_tons": round(
                    daily_consumption["emissions"]["co2_emissions_t_day"], 2
                ),
            },
            
            "tank_requirements": {
                "fuel_tank_capacity_t": fuel_tank_capacity,
                "fuel_needed_tons": round(total_fuel_tons, 2),
                "sufficient_fuel": sufficient_fuel,
                "refueling_recommended": not sufficient_fuel,
                "tanks_needed": round(tanks_needed, 1) if tanks_needed > 0 else 0,
            },
            
            "cost_estimate": {
                "fuel_cost_usd": round(total_fuel_tons * 450, 2),  # ~$450/ton average
                "unit": "USD",
                "note": "Based on $450/metric ton fuel cost (volatile)"
            }
        }
    
    def compare_speed_scenarios(
        self,
        distance_nm: float,
        speeds_knots: list,
        weather_factor: float = 1.0
    ) -> Dict:
        """
        Compare fuel consumption across different speed scenarios.
        
        Useful for: Should we slow down to save fuel?
        """
        
        scenarios = []
        
        for speed in speeds_knots:
            voyage_estimate = self.estimate_voyage_fuel(
                distance_nm, speed, weather_factor, 1.0
            )
            
            scenarios.append({
                "speed_knots": speed,
                "time_days": voyage_estimate["voyage_estimates"]["estimated_time_days"],
                "fuel_tons": voyage_estimate["voyage_estimates"]["total_fuel_tons"],
                "co2_tons": voyage_estimate["emissions"]["total_co2_tons"],
                "cost_usd": voyage_estimate["cost_estimate"]["fuel_cost_usd"],
            })
        
        # Find most economical
        most_economical = min(scenarios, key=lambda x: x["fuel_tons"])
        fastest = min(scenarios, key=lambda x: x["time_days"])
        
        return {
            "vessel_type": self.vessel_type.value,
            "distance_nm": distance_nm,
            "weather_factor": weather_factor,
            "scenarios": scenarios,
            "recommendations": {
                "most_economical_speed": most_economical["speed_knots"],
                "fuel_savings_vs_fastest": round(
                    scenarios[-1]["fuel_tons"] - most_economical["fuel_tons"], 2
                ),
                "fastest_speed": fastest["speed_knots"],
                "note": "Consider operational pressures and scheduling requirements"
            }
        }


# ===== Public API Functions =====

def get_fuel_consumption(
    vessel_type: VesselType,
    speed_knots: float,
    weather_factor: float = 1.0,
    load_factor: float = 1.0
) -> Dict:
    """Public API: Get fuel consumption for vessel at given speed/weather."""
    
    model = FuelConsumptionModel(vessel_type)
    return model.calculate_fuel_consumption(speed_knots, weather_factor, load_factor)


def estimate_voyage_fuel(
    vessel_type: VesselType,
    distance_nm: float,
    avg_speed_knots: float,
    weather_factor: float = 1.0
) -> Dict:
    """Public API: Estimate total fuel for a voyage."""
    
    model = FuelConsumptionModel(vessel_type)
    return model.estimate_voyage_fuel(distance_nm, avg_speed_knots, weather_factor)


def compare_speeds(
    vessel_type: VesselType,
    distance_nm: float,
    speeds_knots: list,
    weather_factor: float = 1.0
) -> Dict:
    """Public API: Compare different speed scenarios."""
    
    model = FuelConsumptionModel(vessel_type)
    return model.compare_speed_scenarios(distance_nm, speeds_knots, weather_factor)
