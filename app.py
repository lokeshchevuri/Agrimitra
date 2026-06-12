import webbrowser
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import uvicorn
import json
app = FastAPI(title="Agrimitra Unified Engine")

# Enable CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Diagnostic Database
# CROP_DB = {
#     "Tomato": {
#         "ideal_temp": (21, 29),
#         "ideal_humidity": (60, 80),
#         "diseases": {
#             "Early Blight": "Copper Fungicide",
#             "Late Blight": "Mancozeb",
#             "Powdery Mildew": "Sulfur-based Fungicide"
#         }
#     },
#     "Rice": {
#         "ideal_temp": (25, 35),
#         "ideal_humidity": (70, 90),
#         "diseases": {
#             "Rice Blast": "Tricyclazole",
#             "Sheath Blight": "Hexaconazole"
#         }
#     }
# }
# trying json for crops databse
try:
    with open("crops.json", "r", encoding="utf-8") as file:
        CROP_DB = json.load(file)
except FileNotFoundError:
    print("Error: The crops.json file was not found.")
    CROP_DB = {}
# 2. Dropdown UI States and Municipalities Registry
# REGIONAL_DB = {
#     "Andhra Pradesh": ["Tadepalligudem", "Vijayawada", "Guntur", "Visakhapatnam","Eluru","Tanuku","Bhimavaram","Narasapuram","Amaravathi"],
#     "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
#     "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"]
# }
#trying cities in json
try:
    with open("places.json", "r", encoding="utf-8") as file:
        REGIONAL_DB = json.load(file)
except FileNotFoundError:
    print("Error: The places.json file was not found.")
    REGIONAL_DB = {}

# --- SERVICE LAYER  ---

def calculate_environmental_factor(current: float, ideal_range: tuple, max_tolerance_deviation: float) -> float:
    """
    Calculates a continuous performance factor (scaled between 0.2 and 1.0) 
    based on how close the weather metrics are to the ideal target ranges.
    """
    low, high = ideal_range
    if low <= current <= high:
        return 1.0
    
    # Measure distance from closest acceptable upper or lower boundary
    deviation = min(abs(current - low), abs(current - high))
    
    # Degrade score linearly matching biological tolerance levels
    factor = 1.0 - (deviation / max_tolerance_deviation)
    return max(0.2, factor)


# --- API ROUTE HANDLERS ---

@app.get("/api/meta")
def get_meta_options():
    """Serves system metadata collections directly down to administrative frontend inputs."""
    return {
        "crops": {crop: list(data["diseases"].keys()) for crop, data in CROP_DB.items()},
        "locations": REGIONAL_DB
    }

@app.get("/api/geocode")
def get_dynamic_coordinates(city: str, state: str):
    """Securely interfaces behind local proxies to map string geographic parameters into coordinate arrays."""
    search_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        response = requests.get(search_url).json()
        results = response.get("results", [])
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Location {city} not found on map registries.")
            
        for match in results:
            if match.get("country") == "India":
                return {"lat": match["latitude"], "lon": match["longitude"]}
                
        return {"lat": results[0]["latitude"], "lon": results[0]["longitude"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding platform offline: {str(e)}")

@app.get("/api/analyze")
def analyze_crop_health(crop: str, disease: str, lat: float, lon: float):
    """Processes historical parameters alongside real-time live variables to compute success models."""
    if crop not in CROP_DB:
        raise HTTPException(status_code=400, detail="Requested crop variant missing from registry.")
        
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
    
    try:
        response = requests.get(weather_url).json()
        current = response.get("current", {})
        curr_temp = current.get("temperature_2m")
        curr_humidity = current.get("relative_humidity_2m", 65) 
        
        if curr_temp is None:
            raise HTTPException(status_code=502, detail="Weather parameters missing.")
            
        crop_specs = CROP_DB[crop]
        ideal_temp = crop_specs["ideal_temp"]
        ideal_hum = crop_specs["ideal_humidity"]
        
        pesticide = "None Required"
        base_health = 100
        
        if disease != "None / Healthy Crop":
            if disease in crop_specs["diseases"]:
                pesticide = crop_specs["diseases"][disease]
                base_health = 70
                
        # Improved continuous success index formulas instead of steep cliff reductions
        temp_factor = calculate_environmental_factor(curr_temp, ideal_temp, max_tolerance_deviation=12.0)
        hum_factor = calculate_environmental_factor(curr_humidity, ideal_hum, max_tolerance_deviation=30.0)
        
        # Weighted metric blend (60% Temperature dependency priority, 40% Humidity dependency priority)
        environmental_score = (temp_factor * 0.6) + (hum_factor * 0.4)
        success_probability = round(base_health * environmental_score, 1)
        
        temp_ok = ideal_temp[0] <= curr_temp <= ideal_temp[1]
        hum_ok = ideal_hum[0] <= curr_humidity <= ideal_hum[1]
        
        return {
            "disease_remedy": {
                "disease": disease,
                "prescribed_pesticide": pesticide
            },
            "weather_metrics": {
                "current_temp": curr_temp,
                "ideal_temp_range": ideal_temp,
                "temp_status": "Ideal" if temp_ok else "Suboptimal",
                "current_humidity": curr_humidity,
                "ideal_humidity_range": ideal_hum,
                "humidity_status": "Ideal" if hum_ok else "Suboptimal"
            },
            "success_probability": success_probability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WEB STATIC FILE ROUTING
@app.get("/app.js")
def serve_js():
    return FileResponse("app.js")

@app.get("/")
def serve_website():
    return FileResponse("index.html")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🌾 AGRIMITRA SYSTEM ACTIVE: CLICK http://localhost:8000")
    print("="*50 + "\n")
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)