# Ship Routing System

An advanced maritime route planning system that calculates optimal ship routes considering real-time weather, ocean currents, fuel consumption, and land avoidance.

## Features

- **Advanced Path-Finding Algorithms**
  - Hybrid Bidirectional RRT* (primary algorithm)
  - D* Lite for dynamic replanning
  - Real-time obstacle avoidance

- **Maritime-Specific Considerations**
  - Water-only routing with comprehensive land detection
  - Real-time weather and ocean current integration
  - Fuel consumption optimization
  - Wave height and wind speed analysis

- **Real-Time Processing**
  - Live route calculation status
  - Progress tracking and ETA updates
  - Dynamic rerouting capabilities

## Project Structure

```
ship-routing/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── algorithms/      # RRT*, D* routing algorithms
│   │   ├── services/        # Weather, land detection, grid services
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # Data schemas
│   │   └── core/           # Configuration and security
│   ├── main.py
│   └── pyproject.toml
│
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── services/       # API client services
│   │   ├── stores/         # State management
│   │   └── pages/          # Route pages
│   └── package.json
│
└── docs/             # Documentation
    ├── ALGORITHM_COMPLEXITY_ANALYSIS.md
    ├── API_DOCUMENTATION.md
    └── SCIENTIFIC_BASIS.md
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the server:**
   ```bash
   python main.py
   ```
   Server runs at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```
   Frontend runs at: `http://localhost:5173`

## API Endpoints

- `POST /api/routes/calculate` - Calculate optimal route
- `GET /api/routes/status/{route_id}` - Get route calculation status
- `GET /api/routes/{route_id}` - Get calculated route details
- `GET /api/ports` - List available ports

For detailed API documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Algorithm Performance

- **Average calculation time:** 22-26 seconds for long routes (1,500+ nautical miles)
- **Success rate:** >95%
- **Time complexity:** O(n²×m) for RRT*, O(V log V) for D*
- **Space complexity:** O(n) for RRT*, O(V) for D*

For detailed complexity analysis, see [ALGORITHM_COMPLEXITY_ANALYSIS.md](./ALGORITHM_COMPLEXITY_ANALYSIS.md)

## Technical Documentation

- **[ALGORITHM_COMPLEXITY_ANALYSIS.md](./ALGORITHM_COMPLEXITY_ANALYSIS.md)** - Detailed algorithmic complexity and performance analysis
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference
- **[SCIENTIFIC_BASIS.md](./SCIENTIFIC_BASIS.md)** - Scientific foundation and methodologies
- **[backend/README.md](./backend/README.md)** - Backend-specific documentation
- **[backend/MARITIME_ROUTING_GUIDE.md](./backend/MARITIME_ROUTING_GUIDE.md)** - Maritime routing implementation guide

## Key Technologies

### Backend
- Python 3.11+
- FastAPI (web framework)
- NumPy (numerical computations)
- Custom RRT* and D* implementations

### Frontend
- React 18
- TypeScript
- Leaflet (map visualization)
- Tailwind CSS

## Environment Variables

Required environment variables (in `backend/.env`):

```env
# API Keys
CMEMS_USERNAME=your_username
CMEMS_PASSWORD=your_password

# Security
SECRET_KEY=your_secret_key
API_KEY=your_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

See `backend/.env.example` for full configuration options.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

[Add your license information here]

## Authors

[Add author information here]

## Acknowledgments

- CMEMS (Copernicus Marine Environment Monitoring Service) for weather data
- OpenStreetMap for coastline data
- Academic research on RRT* and D* algorithms
