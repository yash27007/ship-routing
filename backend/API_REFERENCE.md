# API Reference & Configuration Guide

## Quick Reference: What API Do You Need?

| Provider | Purpose | API Key | Cost | Update | Status |
|----------|---------|---------|------|--------|--------|
| **NOAA GFS** | Primary weather | ❌ No | **FREE** | 6 hrs | ✅ Ready |
| **OpenWeatherMap** | Enhanced weather | ⭐ Optional | **FREE** | 10 min | ✅ Ready |
| **CMEMS** | Ocean data | ✅ Optional | **FREE** | 1 day | ✅ Integrated |

## ANSWER: You need NOTHING to start! 🎉

The system works 100% without any API keys using NOAA GFS (free, public).

---

## Setup Options

### Option 1: Minimal Setup (Recommended for Quick Start) ⭐

**What you need to do:** Nothing! Just run the system.

```bash
cd backend
uv run main.py
```

**What it provides:**
- ✅ NOAA GFS weather (free public API)
- ✅ All hazard detection
- ✅ All routing algorithms
- ✅ Full functionality

**Limitations:**
- Weather updates every 6 hours (vs 10 minutes)
- No advanced ocean data

---

### Option 2: Enhanced Setup (Recommended for Production)

**Step 1:** Get free OpenWeatherMap API key
1. Go to https://openweathermap.org/api
2. Click "Sign Up"
3. Create account (takes 2 minutes)
4. Go to dashboard
5. Copy "API Key"

**Step 2:** Configure
```bash
# Create or edit backend/.env
OPENWEATHER_API_KEY=sk_test_your_key_here
```

**Step 3:** Restart
```bash
cd backend
uv run main.py
```

**What you gain:**
- ✅ Weather updates every 10 minutes (vs 6 hours)
- ✅ More accurate wind/wave data
- ✅ Still 100% free (60 calls/minute free tier)

---

### Option 3: Full Setup (For Research/Advanced Features)

**Adds:**
1. CMEMS ocean data (currents, SST, sea level)
2. More detailed weather from multiple providers
3. Advanced hazard modeling

**Not needed for basic functionality, but enhances accuracy**

---

## Configuration File (.env)

### Minimal (.env with no APIs)
```bash
# No content needed - system works with defaults
# NOAA GFS will be used automatically
```

### Standard (.env with OpenWeatherMap)
```bash
# Weather Data
OPENWEATHER_API_KEY=your_api_key_from_openweathermap.org

# Optional: NOAA (usually not needed)
NOAA_API_KEY=

# Optional: CMEMS
CMEMS_USERNAME=
CMEMS_PASSWORD=
```

### Full (.env with all providers)
```bash
# ============================================
# WEATHER PROVIDERS
# ============================================

# NOAA GFS (automatic, no key needed)
# https://api.weather.gov
NOAA_API_KEY=

# OpenWeatherMap (free tier: 60 calls/min)
# https://openweathermap.org/api
OPENWEATHER_API_KEY=sk_test_abc123xyz...

# CMEMS (optional, for ocean data)
# https://marine.copernicus.eu/
CMEMS_USERNAME=your_username
CMEMS_PASSWORD=your_password

# ============================================
# ROUTING PARAMETERS
# ============================================

MAX_RRT_ITERATIONS=500          # RRT* planning iterations
RRT_STEP_SIZE=0.5               # Maximum step size in degrees
GOAL_SAMPLE_RATE=0.15           # Goal bias probability
WEATHER_CACHE_DURATION=600      # Cache TTL in seconds (10 min)

# ============================================
# HAZARD PARAMETERS
# ============================================

CURRENT_MONTH=11                # Used for seasonal hazards
MONSOON_SEVERITY=3.5            # Cost multiplier for monsoons
CYCLONE_SEVERITY=5.0            # Cost multiplier for cyclones
TRAFFIC_PREFERENCE=0.8          # Preference for traffic lanes (0.8 = 20% cheaper)
```

---

## Getting API Keys

### NOAA GFS (No Key Needed!)

**Status:** ✅ Already working
- Public API: `https://api.weather.gov`
- No registration required
- No rate limits (reasonable use)
- Global coverage

**Test it:**
```bash
curl https://api.weather.gov/points/13.19,80.28
```

### OpenWeatherMap (Optional)

**Step-by-step:**
1. Go to https://openweathermap.org/api
2. Click "Sign Up" (or log in)
3. Create free account
4. Go to "API keys" tab
5. Copy the key starting with "sk_"
6. Add to `.env`: `OPENWEATHER_API_KEY=sk_test_...`

**Free tier:**
- 60 calls per minute
- 5-day forecast
- Worldwide coverage
- 10-minute update frequency

**Test it:**
```bash
curl "https://api.openweathermap.org/data/2.5/weather?lat=13&lon=80&appid=YOUR_KEY"
```

### CMEMS (Optional, Advanced)

**Step-by-step:**
1. Go to https://marine.copernicus.eu/
2. Click "Login" or "Sign Up"
3. Create research account
4. Request data access
5. Get credentials

**What it provides:**
- Ocean currents
- Sea surface temperature
- Sea level anomalies
- Wind waves

**Note:** More complex setup, not required for basic routing

---

## Provider Fallback Chain

The system tries providers in this order:

```python
1. OpenWeatherMap (if API key available)
   ├─ Success? → Use and cache
   └─ Failed? → Try next

2. NOAA GFS (always available)
   ├─ Success? → Use and cache
   └─ Failed? → Try next

3. CMEMS (if credentials available)
   ├─ Success? → Use
   └─ Failed? → Use mock

4. Mock Weather (fallback)
   └─ Always works, based on latitude
```

**Result:** System ALWAYS has weather data!

---

## Code Example: Using the APIs

```python
from app.services.real_time_weather import get_weather_service

# Get the weather service (uses best available provider)
weather_service = get_weather_service()

# Get weather at a point
weather = weather_service.get_weather_point(
    lat=13.1939,      # Chennai
    lon=80.2822,
    forecast_hours=0   # Current (0) or future (24, 48, etc.)
)

print(f"Source: {weather['source']}")           # OpenWeatherMap, NOAA_GFS, or MOCK
print(f"Wind: {weather['wind_speed_knots']} knots")
print(f"Waves: {weather['wave_height_m']} m")
print(f"Temperature: {weather['temperature_c']}°C")

# Get weather along entire route
waypoints = [
    (13.1939, 80.2822),   # Start: Chennai
    (10.0, 90.0),         # Middle: Bay of Bengal
    (1.3550, 103.8198)    # End: Singapore
]

weather_data = weather_service.get_weather_route(waypoints)
for i, weather in enumerate(weather_data):
    print(f"Point {i}: Wind {weather['wind_speed_knots']} knots")
```

---

## Testing Your Configuration

### Test 1: NOAA GFS (Should Always Work)

```bash
cd backend
python3 << 'EOF'
from app.services.real_time_weather import NOAAGFSProvider

provider = NOAAGFSProvider()
weather = provider.get_weather_point(13.19, 80.28)

if weather:
    print("✓ NOAA GFS working")
    print(f"  Wind: {weather['wind_speed_knots']:.1f} knots")
    print(f"  Source: {weather['source']}")
else:
    print("✗ NOAA GFS failed")
EOF
```

### Test 2: OpenWeatherMap (If Key Configured)

```bash
cd backend
python3 << 'EOF'
from app.services.real_time_weather import OpenWeatherMapProvider

provider = OpenWeatherMapProvider()
weather = provider.get_weather_point(13.19, 80.28)

if weather:
    print("✓ OpenWeatherMap working")
    print(f"  Source: {weather['source']}")
else:
    print("⚠ OpenWeatherMap not available (check API key)")
EOF
```

### Test 3: Full Service (Tries All)

```bash
cd backend
python3 << 'EOF'
from app.services.real_time_weather import RealTimeWeatherService

service = RealTimeWeatherService()
weather = service.get_weather_point(13.19, 80.28)

print(f"✓ Weather available")
print(f"  Source: {weather['source']}")
print(f"  Data: Wind {weather['wind_speed_knots']:.1f} knots, Waves {weather['wave_height_m']:.1f}m")
EOF
```

---

## Troubleshooting

### Issue: "Weather not available"
**Cause:** Internet connectivity issue
**Solution:** Check internet connection, try different network

### Issue: "OpenWeatherMap not working"
**Cause:** Invalid API key
**Solution:** 
1. Verify key is correct in .env
2. Test key directly: `curl https://api.openweathermap.org/data/2.5/weather?lat=0&lon=0&appid=YOUR_KEY`
3. Check API key hasn't expired

### Issue: "NOAA GFS very slow (500ms+)"
**Cause:** Network latency or NOAA server load
**Solution:** Results are cached for 1 hour, so not a repeated issue

### Issue: "All providers failing"
**Cause:** No internet connectivity
**Solution:** System falls back to mock weather (LOCATION-BASED)

---

## Production Deployment

### AWS Lambda

```python
# No special setup needed
# NOAA is public API - works in Lambda
# Weather caching: Use ElastiCache or DynamoDB
```

### Docker

```dockerfile
FROM python:3.11

# No API keys needed in image
# Add at runtime via environment variables
ENV OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ship-routing-config
data:
  # NOAA automatically used (no config needed)
  # Only add OpenWeatherMap if available
  OPENWEATHER_API_KEY: ""  # Add your key here

---
apiVersion: v1
kind: Deployment
metadata:
  name: ship-routing-api
spec:
  template:
    spec:
      containers:
      - name: api
        env:
        - name: OPENWEATHER_API_KEY
          valueFrom:
            configMapKeyRef:
              name: ship-routing-config
              key: OPENWEATHER_API_KEY
```

---

## Cost Analysis

### Your Cost: $0 (Forever!) 🎉

| Component | Provider | Cost | Usage |
|-----------|----------|------|-------|
| Weather | NOAA GFS | **FREE** | Unlimited |
| Weather | OpenWeatherMap | **FREE** (60/min tier) | ~100/min for typical routing |
| Ocean data | CMEMS | **FREE** (research) | ~10/day |
| **Total** | | **$0** | ✅ All free tier |

**Why so cheap?**
- NOAA is taxpayer-funded, freely available
- OpenWeatherMap free tier covers realistic usage (60 calls/min > 100 calls/min routing)
- CMEMS research access is free

---

## Summary

### 🚀 You need: NOTHING to start!

The system works immediately with:
- ✅ NOAA GFS (free, public, no key)
- ✅ All routing algorithms
- ✅ All hazard detection
- ✅ Full functionality

### ⭐ To optimize: Get free OpenWeatherMap key (5 min)

Provides:
- 10-minute weather updates (vs NOAA's 6 hours)
- Still 100% free (60 calls/minute)
- Better accuracy in coastal areas

### 📊 To fully enhance: CMEMS (optional)

Provides:
- Ocean currents
- Sea surface temperature
- Advanced hazard modeling

**Not required, but helps for research**

---

## Next Steps

1. ✅ Do nothing - system works now with NOAA
2. (Optional) Get OpenWeatherMap key - takes 5 minutes
3. Integrate into your API
4. Test the routes
5. Deploy

---

**You're all set!** 🚢⚓

No API keys needed to get started. Everything is free.
