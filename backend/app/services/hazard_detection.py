"""
Comprehensive Maritime Hazard Detection Service

Integrates multiple hazard types:
1. Land/Coastline detection
2. Shallow water detection (<50m depth)
3. Monsoon zones (seasonal)
4. Cyclone-prone areas (seasonal)
5. Traffic separation schemes (preferred routes)
6. Real-time weather hazards

References:
- IMO (International Maritime Organization) guidelines
- WMO (World Meteorological Organization) warnings
- NOAA/NHC cyclone tracking
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from datetime import datetime
from app.services.land_detection import LandDetectionService
from app.services.ocean_grid import OceanGrid, CellType


class HazardType(Enum):
    """Maritime hazard classifications"""
    LAND = "land"
    SHALLOW_WATER = "shallow_water"
    MONSOON = "monsoon"
    CYCLONE = "cyclone"
    TRAFFIC_CONGESTION = "traffic_congestion"
    ICE = "ice"
    PIRACY = "piracy"
    WEATHER_STORM = "weather_storm"


class HazardLevel(Enum):
    """Hazard severity levels"""
    NONE = 0           # No hazard
    LOW = 1            # Manageable, minor cost increase
    MODERATE = 2       # Significant routing impact
    HIGH = 3           # Major routing impact, route diversion recommended
    CRITICAL = 4       # Impassable, must avoid


class HazardZone:
    """Represents a geographic hazard zone"""
    
    def __init__(self, name: str, hazard_type: HazardType, 
                 center_lat: float, center_lon: float, radius_deg: float,
                 severity: HazardLevel = HazardLevel.MODERATE,
                 active_months: Optional[List[int]] = None,
                 cost_multiplier: float = 1.0):
        self.name = name
        self.hazard_type = hazard_type
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_deg = radius_deg
        self.severity = severity
        self.active_months = active_months or list(range(1, 13))  # Active all year by default
        self.cost_multiplier = cost_multiplier
        self.created_at = datetime.utcnow()
    
    def contains_point(self, lat: float, lon: float) -> bool:
        """Check if point is within hazard zone"""
        dist = math.sqrt((lat - self.center_lat)**2 + (lon - self.center_lon)**2)
        return dist <= self.radius_deg
    
    def is_active(self, month: int) -> bool:
        """Check if hazard is active in given month"""
        return month in self.active_months
    
    def get_severity_for_point(self, lat: float, lon: float) -> Tuple[HazardLevel, float]:
        """
        Get hazard severity for a point (0 if outside, degrades with distance from edge).
        
        Returns:
            (severity_level, cost_multiplier)
        """
        dist = math.sqrt((lat - self.center_lat)**2 + (lon - self.center_lon)**2)
        
        if dist > self.radius_deg:
            return (HazardLevel.NONE, 1.0)
        
        # Severity increases closer to center
        proximity_factor = (self.radius_deg - dist) / self.radius_deg
        severity_value = int(self.severity.value * proximity_factor)
        
        if severity_value >= self.severity.value:
            return (self.severity, self.cost_multiplier)
        elif severity_value == 0:
            return (HazardLevel.NONE, 1.0)
        else:
            return (HazardLevel(severity_value), 1.0 + (self.cost_multiplier - 1.0) * (proximity_factor * 0.5))


class HazardDetectionService:
    """
    Comprehensive maritime hazard detection and routing impact calculation.
    
    Combines multiple hazard sources with real-time weather integration.
    """
    
    def __init__(self, ocean_grid: Optional[OceanGrid] = None):
        """
        Initialize hazard detection service.
        
        Args:
            ocean_grid: Pre-initialized OceanGrid, or creates new one
        """
        self.ocean_grid = ocean_grid or OceanGrid(level=1)
        self.hazard_zones: List[HazardZone] = []
        self.dynamic_hazards: Dict[str, HazardZone] = {}  # Real-time hazards (cyclones, storms)
        
        # Initialize static hazard zones
        self._initialize_static_hazards()
        self._initialize_monsoon_zones()
        self._initialize_cyclone_zones()
        self._initialize_traffic_schemes()
        self._initialize_piracy_zones()
        self._initialize_ice_zones()
    
    def _initialize_static_hazards(self):
        """Add permanent geographical hazard zones"""
        # Suez Canal - shallow water and congestion
        self.hazard_zones.append(HazardZone(
            name="Suez Canal Approach",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=30.5,
            center_lon=32.3,
            radius_deg=0.5,
            severity=HazardLevel.MODERATE,
            cost_multiplier=2.0
        ))
        
        # Red Sea - shallow water and congestion
        self.hazard_zones.append(HazardZone(
            name="Red Sea Narrows",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=19.0,
            center_lon=40.0,
            radius_deg=1.0,
            severity=HazardLevel.MODERATE,
            cost_multiplier=1.8
        ))
        
        # Strait of Malacca - shallow and congestion
        self.hazard_zones.append(HazardZone(
            name="Strait of Malacca",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=2.0,
            center_lon=101.0,
            radius_deg=1.5,
            severity=HazardLevel.HIGH,
            cost_multiplier=2.5
        ))
        
        # Singapore Strait
        self.hazard_zones.append(HazardZone(
            name="Singapore Strait",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=1.3,
            center_lon=103.8,
            radius_deg=0.8,
            severity=HazardLevel.HIGH,
            cost_multiplier=2.3
        ))
        
        # Sunda Strait (between Java and Sumatra)
        self.hazard_zones.append(HazardZone(
            name="Sunda Strait",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=-6.5,
            center_lon=105.8,
            radius_deg=1.0,
            severity=HazardLevel.MODERATE,
            cost_multiplier=2.0
        ))
        
        # English Channel
        self.hazard_zones.append(HazardZone(
            name="English Channel",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=50.0,
            center_lon=-2.0,
            radius_deg=1.5,
            severity=HazardLevel.MODERATE,
            cost_multiplier=1.8
        ))
        
        # Gulf of Mexico shallow areas
        self.hazard_zones.append(HazardZone(
            name="Gulf of Mexico Shallows",
            hazard_type=HazardType.SHALLOW_WATER,
            center_lat=25.0,
            center_lon=-90.0,
            radius_deg=3.0,
            severity=HazardLevel.LOW,
            cost_multiplier=1.3
        ))
    
    def _initialize_monsoon_zones(self):
        """Add seasonal monsoon hazard zones"""
        # Southwest Monsoon (May-September): Dangerous in Arabian Sea and Bay of Bengal
        
        # Arabian Sea
        self.hazard_zones.append(HazardZone(
            name="Arabian Sea Southwest Monsoon",
            hazard_type=HazardType.MONSOON,
            center_lat=12.0,
            center_lon=65.0,
            radius_deg=12.0,
            severity=HazardLevel.HIGH,
            active_months=[5, 6, 7, 8, 9],
            cost_multiplier=3.5
        ))
        
        # Bay of Bengal
        self.hazard_zones.append(HazardZone(
            name="Bay of Bengal Southwest Monsoon",
            hazard_type=HazardType.MONSOON,
            center_lat=15.0,
            center_lon=90.0,
            radius_deg=10.0,
            severity=HazardLevel.HIGH,
            active_months=[5, 6, 7, 8, 9],
            cost_multiplier=3.3
        ))
        
        # Eastern Indian Ocean
        self.hazard_zones.append(HazardZone(
            name="Eastern Indian Ocean Southwest Monsoon",
            hazard_type=HazardType.MONSOON,
            center_lat=5.0,
            center_lon=105.0,
            radius_deg=8.0,
            severity=HazardLevel.MODERATE,
            active_months=[5, 6, 7, 8, 9],
            cost_multiplier=2.8
        ))
        
        # Northeast Monsoon transition periods (October-November, March-April)
        self.hazard_zones.append(HazardZone(
            name="Arabian Sea Monsoon Transition",
            hazard_type=HazardType.MONSOON,
            center_lat=12.0,
            center_lon=65.0,
            radius_deg=10.0,
            severity=HazardLevel.MODERATE,
            active_months=[10, 11, 3, 4],
            cost_multiplier=2.0
        ))
    
    def _initialize_cyclone_zones(self):
        """Add cyclone-prone areas"""
        # Bay of Bengal cyclone season (May-June, September-November)
        self.hazard_zones.append(HazardZone(
            name="Bay of Bengal Cyclone Zone",
            hazard_type=HazardType.CYCLONE,
            center_lat=15.0,
            center_lon=88.0,
            radius_deg=8.0,
            severity=HazardLevel.CRITICAL,
            active_months=[5, 6, 9, 10, 11],
            cost_multiplier=5.0
        ))
        
        # Arabian Sea cyclone season
        self.hazard_zones.append(HazardZone(
            name="Arabian Sea Cyclone Zone",
            hazard_type=HazardType.CYCLONE,
            center_lat=12.0,
            center_lon=62.0,
            radius_deg=8.0,
            severity=HazardLevel.CRITICAL,
            active_months=[5, 6, 9, 10, 11],
            cost_multiplier=5.0
        ))
        
        # Northwest Pacific typhoon season (June-November)
        self.hazard_zones.append(HazardZone(
            name="Northwest Pacific Typhoon Zone",
            hazard_type=HazardType.CYCLONE,
            center_lat=20.0,
            center_lon=130.0,
            radius_deg=15.0,
            severity=HazardLevel.HIGH,
            active_months=[6, 7, 8, 9, 10, 11],
            cost_multiplier=3.5
        ))
    
    def _initialize_traffic_schemes(self):
        """Add maritime traffic separation schemes (TSS) - these have LOWER cost to encourage use"""
        # Suez Canal TSS
        self.hazard_zones.append(HazardZone(
            name="Suez Canal TSS",
            hazard_type=HazardType.TRAFFIC_CONGESTION,
            center_lat=30.5,
            center_lon=32.3,
            radius_deg=1.0,
            severity=HazardLevel.LOW,
            cost_multiplier=0.8  # LOWER cost to prefer this lane
        ))
        
        # Singapore Strait TSS
        self.hazard_zones.append(HazardZone(
            name="Singapore Strait TSS",
            hazard_type=HazardType.TRAFFIC_CONGESTION,
            center_lat=1.3,
            center_lon=103.8,
            radius_deg=1.2,
            severity=HazardLevel.LOW,
            cost_multiplier=0.85
        ))
        
        # Malacca Strait TSS
        self.hazard_zones.append(HazardZone(
            name="Malacca Strait TSS",
            hazard_type=HazardType.TRAFFIC_CONGESTION,
            center_lat=2.0,
            center_lon=101.0,
            radius_deg=1.5,
            severity=HazardLevel.LOW,
            cost_multiplier=0.9
        ))
        
        # Indian Ocean main shipping lanes
        self.hazard_zones.append(HazardZone(
            name="Arabian Sea Shipping Lanes",
            hazard_type=HazardType.TRAFFIC_CONGESTION,
            center_lat=10.0,
            center_lon=60.0,
            radius_deg=3.0,
            severity=HazardLevel.LOW,
            cost_multiplier=0.95
        ))
    
    def _initialize_piracy_zones(self):
        """Add piracy-prone areas"""
        # Somali coast
        self.hazard_zones.append(HazardZone(
            name="Gulf of Aden - Piracy Risk",
            hazard_type=HazardType.PIRACY,
            center_lat=12.5,
            center_lon=48.0,
            radius_deg=4.0,
            severity=HazardLevel.MODERATE,
            cost_multiplier=1.8
        ))
        
        # Strait of Malacca piracy
        self.hazard_zones.append(HazardZone(
            name="Malacca Strait - Piracy Risk",
            hazard_type=HazardType.PIRACY,
            center_lat=2.0,
            center_lon=101.0,
            radius_deg=2.0,
            severity=HazardLevel.LOW,
            cost_multiplier=1.3
        ))
    
    def _initialize_ice_zones(self):
        """Add ice-prone areas"""
        # Arctic
        self.hazard_zones.append(HazardZone(
            name="Arctic Ice Zone",
            hazard_type=HazardType.ICE,
            center_lat=75.0,
            center_lon=0.0,
            radius_deg=20.0,
            severity=HazardLevel.HIGH,
            active_months=[1, 2, 3, 11, 12],  # Winter months
            cost_multiplier=4.0
        ))
        
        # Southern Ocean
        self.hazard_zones.append(HazardZone(
            name="Southern Ocean Ice Zone",
            hazard_type=HazardType.ICE,
            center_lat=-60.0,
            center_lon=0.0,
            radius_deg=15.0,
            severity=HazardLevel.MODERATE,
            active_months=[6, 7, 8, 9],  # Southern winter
            cost_multiplier=2.5
        ))
    
    def add_dynamic_hazard(self, hazard_id: str, hazard: HazardZone):
        """Add or update a dynamic real-time hazard (e.g., active cyclone)"""
        self.dynamic_hazards[hazard_id] = hazard
    
    def remove_dynamic_hazard(self, hazard_id: str):
        """Remove a dynamic hazard"""
        self.dynamic_hazards.pop(hazard_id, None)
    
    def get_all_hazards(self, current_month: Optional[int] = None) -> List[HazardZone]:
        """
        Get all active hazards for current month.
        
        Args:
            current_month: Month (1-12), defaults to current month
        
        Returns:
            List of active hazard zones
        """
        if current_month is None:
            current_month = datetime.utcnow().month
        
        active = [h for h in self.hazard_zones if h.is_active(current_month)]
        active.extend(self.dynamic_hazards.values())
        return active
    
    def evaluate_point_hazard(self, lat: float, lon: float, 
                             current_month: Optional[int] = None) -> Dict:
        """
        Evaluate all hazards at a point.
        
        Args:
            lat, lon: Coordinates
            current_month: Month (1-12)
        
        Returns:
            Dictionary with hazard information and combined cost multiplier
        """
        if current_month is None:
            current_month = datetime.utcnow().month
        
        # Check land first (highest priority)
        if LandDetectionService.is_point_on_land(lat, lon):
            return {
                "is_hazardous": True,
                "hazard_type": HazardType.LAND.value,
                "severity": HazardLevel.CRITICAL.name,
                "cost_multiplier": float('inf'),
                "hazards": [{"name": "Land", "type": "land", "severity": "CRITICAL"}]
            }
        
        # Evaluate grid-based hazards
        grid_cell = self.ocean_grid.get_cell(lat, lon)
        hazards = []
        max_cost = 1.0
        
        if grid_cell:
            if grid_cell.cell_type == CellType.SHALLOW:
                hazards.append({
                    "name": "Shallow Water",
                    "type": HazardType.SHALLOW_WATER.value,
                    "severity": HazardLevel.MODERATE.name,
                    "depth_m": grid_cell.depth_m
                })
                max_cost = max(max_cost, grid_cell.cost)
        
        # Check zone-based hazards
        active_zones = self.get_all_hazards(current_month)
        for zone in active_zones:
            if zone.contains_point(lat, lon):
                severity, cost = zone.get_severity_for_point(lat, lon)
                if severity != HazardLevel.NONE:
                    hazards.append({
                        "name": zone.name,
                        "type": zone.hazard_type.value,
                        "severity": severity.name,
                        "distance_from_center": math.sqrt((lat - zone.center_lat)**2 + (lon - zone.center_lon)**2),
                        "cost_multiplier": cost
                    })
                    max_cost = max(max_cost, cost)
        
        return {
            "is_hazardous": len(hazards) > 0,
            "hazard_count": len(hazards),
            "cost_multiplier": max_cost,
            "hazards": hazards,
            "latitude": lat,
            "longitude": lon
        }
    
    def evaluate_route_hazards(self, waypoints: List[Tuple[float, float]], 
                              current_month: Optional[int] = None) -> Dict:
        """
        Evaluate hazards along an entire route.
        
        Args:
            waypoints: List of (lat, lon) coordinates
            current_month: Month (1-12)
        
        Returns:
            Route hazard summary with critical hazards and total cost
        """
        if current_month is None:
            current_month = datetime.utcnow().month
        
        total_cost = 0.0
        max_severity = HazardLevel.NONE
        hazard_points = []
        critical_hazards = []
        
        for lat, lon in waypoints:
            evaluation = self.evaluate_point_hazard(lat, lon, current_month)
            cost = evaluation["cost_multiplier"]
            total_cost += cost
            
            if evaluation["is_hazardous"]:
                hazard_points.append(evaluation)
                for hazard in evaluation["hazards"]:
                    sev = HazardLevel[hazard["severity"]]
                    if sev.value > max_severity.value:
                        max_severity = sev
                    
                    if sev in [HazardLevel.CRITICAL, HazardLevel.HIGH]:
                        critical_hazards.append(hazard)
        
        return {
            "waypoint_count": len(waypoints),
            "hazard_waypoints": len(hazard_points),
            "total_hazard_cost": total_cost,
            "average_cost_multiplier": total_cost / len(waypoints) if waypoints else 1.0,
            "max_severity": max_severity.name,
            "critical_hazards": critical_hazards,
            "hazard_points": hazard_points,
            "risk_assessment": "HIGH" if max_severity in [HazardLevel.CRITICAL, HazardLevel.HIGH] else "MODERATE" if max_severity == HazardLevel.MODERATE else "LOW"
        }
