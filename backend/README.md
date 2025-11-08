# Ship Routing Backend

FastAPI-based backend for maritime route optimization with real-time weather integration and advanced path-finding algorithms.

## Features

- **Hybrid Bidirectional RRT*** - Primary path-finding algorithm with bidirectional search
- **D* Lite** - Dynamic replanning for real-time route adjustments
- **Land Detection** - Comprehensive polygon-based land avoidance system
- **Weather Integration** - Real-time ocean currents, wave heights, and wind data from CMEMS
- **Fuel Optimization** - Advanced fuel consumption modeling based on weather conditions
- **Real-time Status** - WebSocket-like polling for route calculation progress

## Installation

### Using pip

```bash
pip install -e .
```

### Using uv (recommended)

```bash
uv pip install -e .
```

## Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure `.env` file:**
   ```env
   # CMEMS API Credentials (Required for weather data)
   CMEMS_USERNAME=your_username
   CMEMS_PASSWORD=your_password

   # Security
   SECRET_KEY=your_secret_key_here
   API_KEY=your_api_key_here

   # Server
   HOST=0.0.0.0
   PORT=8000
   ```

For detailed weather API setup, see [WEATHER_API_SETUP.md](./WEATHER_API_SETUP.md)

## Running the Server

```bash
python main.py
```

Server will start at: `http://localhost:8000`

API Documentation available at: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── algorithms/           # Path-finding algorithms
│   │   ├── hybrid_bidirectional_rrt_star.py
│   │   ├── d_star.py
│   │   └── maritime_astar.py
│   ├── services/             # Core services
│   │   ├── land_detection.py      # Polygon-based land detection
│   │   ├── ocean_grid.py          # Ocean grid classification
│   │   ├── real_time_weather.py   # Weather data integration
│   │   ├── route_calculator.py    # Route calculation orchestration
│   │   └── fuel_model.py          # Fuel consumption modeling
│   ├── api/                  # API endpoints
│   │   └── routes/
│   ├── models/               # Pydantic schemas
│   │   └── schemas.py
│   └── core/                 # Configuration
│       ├── config.py
│       └── security.py
├── main.py                   # Application entry point
└── pyproject.toml           # Dependencies
```

## API Endpoints

### Route Calculation

**Calculate Route**
```http
POST /api/routes/calculate
Content-Type: application/json

{
  "start_port": "INMAA",
  "end_port": "SGSIN",
  "cargo_weight": 50000,
  "departure_time": "2024-01-15T00:00:00Z"
}
```

**Get Route Status**
```http
GET /api/routes/status/{route_id}
```

**Get Route Details**
```http
GET /api/routes/{route_id}
```

For complete API reference, see [API_REFERENCE.md](./API_REFERENCE.md)

## Algorithm Performance

| Metric | Value |
|--------|-------|
| Average Calculation Time | 22-26 seconds |
| Success Rate | >95% |
| Max Distance Tested | 1,575 nautical miles |
| RRT* Time Complexity | O(n²×m) |
| D* Time Complexity | O(V log V) |

## Key Services

### Land Detection Service
- Polygon-based land detection for 30+ major landmasses
- Ray-casting algorithm for point-in-polygon tests
- Special handling for straits (e.g., Strait of Malacca)
- Performance: ~0.1ms per point check

### Weather Service
- Real-time data from CMEMS (Copernicus Marine)
- Ocean currents (u, v components)
- Significant wave height
- Wind speed (u10, v10 components)
- 6-hour forecast intervals

### Route Calculator
- Orchestrates algorithm selection (RRT* → D* fallback)
- Manages calculation state and progress
- Validates water-only paths
- Provides real-time status updates

## Documentation

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation
- **[MARITIME_ROUTING_GUIDE.md](./MARITIME_ROUTING_GUIDE.md)** - Maritime routing implementation details
- **[WEATHER_API_SETUP.md](./WEATHER_API_SETUP.md)** - Weather API configuration guide
- **[PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md)** - Performance tuning guide
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Detailed project structure

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Dependencies

Key dependencies:
- FastAPI - Web framework
- NumPy - Numerical computations
- Pydantic - Data validation
- python-dotenv - Environment management
- httpx - HTTP client for weather APIs

See `pyproject.toml` for complete dependency list.

## Troubleshooting

### Route calculation fails
- Check CMEMS credentials in `.env`
- Verify ports are valid and in water
- Check backend logs for detailed error messages

### Weather data unavailable
- Verify CMEMS API credentials
- Check network connectivity
- See [WEATHER_API_SETUP.md](./WEATHER_API_SETUP.md) for detailed setup

### Land detection issues
- Algorithm automatically avoids land using polygon-based detection
- For issues with specific straits, check `land_detection.py` polygon definitions

## License

[Add your license information here]
