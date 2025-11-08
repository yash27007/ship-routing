"""
Global Grid Cache - Initialize ocean grid once and reuse it

This singleton pattern ensures the expensive grid initialization
happens only once, dramatically improving performance for subsequent requests.
"""

from typing import Optional
from app.services.ocean_grid import OceanGrid
from app.services.hazard_detection import HazardDetectionService

class GridCache:
    """Singleton grid cache - initialize once, reuse forever"""
    
    _grid_level1: Optional[OceanGrid] = None
    _grid_level2: Optional[OceanGrid] = None
    _hazard_service: Optional[HazardDetectionService] = None
    _initialized = False
    
    @classmethod
    def get_grid_level1(cls) -> OceanGrid:
        """Get or create Level-1 grid (1° × 1°)"""
        if cls._grid_level1 is None:
            print("[GridCache] Initializing Level-1 grid (first request only)...")
            cls._grid_level1 = OceanGrid(level=1, use_cached_depth=True)
            print(f"[GridCache] Level-1 grid ready: {len(cls._grid_level1.cells)} cells")
        return cls._grid_level1
    
    @classmethod
    def get_grid_level2(cls) -> OceanGrid:
        """Get or create Level-2 grid (0.1° × 0.1°) - on demand"""
        if cls._grid_level2 is None:
            print("[GridCache] Initializing Level-2 grid (first refinement)...")
            cls._grid_level2 = OceanGrid(level=2, use_cached_depth=True)
            print(f"[GridCache] Level-2 grid ready: {len(cls._grid_level2.cells)} cells")
        return cls._grid_level2
    
    @classmethod
    def get_hazard_service(cls) -> HazardDetectionService:
        """Get or create hazard detection service"""
        if cls._hazard_service is None:
            print("[GridCache] Initializing hazard detection service...")
            grid = cls.get_grid_level1()
            cls._hazard_service = HazardDetectionService(grid)
            print("[GridCache] Hazard service ready with 20+ zones")
        return cls._hazard_service
    
    @classmethod
    def initialize_all(cls):
        """Pre-initialize all grids and services (call on startup)"""
        if cls._initialized:
            return
        print("[GridCache] Pre-initializing all grids on startup...")
        cls.get_grid_level1()
        cls.get_hazard_service()
        cls._initialized = True
        print("[GridCache] All grids initialized and cached!")
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data (for testing/reset)"""
        cls._grid_level1 = None
        cls._grid_level2 = None
        cls._hazard_service = None
        cls._initialized = False
        print("[GridCache] Cache cleared")
