import requests

# 1. Mock Database
crop_database = {
    "Tomato": {
        "ideal_weather": {"min_temp": 18, "max_temp": 30, "max_wind": 20},
        "diseases": {
            "Early Blight": "Copper Fungicide",
            "Late Blight": "Mancozeb"
        }
    }
}

def get_current_weather(lat, lon):
    """Fetches real-time weather from Open-Meteo"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
    try:
        response = requests.get(url).json()
        current = response['current']
        return {
            "temp": current['temperature_2m'],
            "wind": current['wind_speed_10m']
        }
    except Exception as e:
        print("Error fetching weather data:", e)
        return None

def calculate_success(crop_name, current_weather):
    """Calculates crop success probability based on weather stress"""
    ideal = crop_database[crop_name]["ideal_weather"]
    curr_temp = current_weather["temp"]
    curr_wind = current_weather["wind"]
    
    # Base probability for a diseased crop trying to recover
    probability = 70 
    
    # Penalty if weather is too hot or too cold
    if curr_temp < ideal["min_temp"] or curr_temp > ideal["max_temp"]:
        probability -= 15
        
    # Penalty if wind is too high (pesticide will blow away)
    if curr_wind > ideal["max_wind"]:
        probability -= 15
        
    return max(probability, 10) # Ensure it doesn't drop below 10%

# --- SIMULATION ---
# User choices
selected_crop = "Tomato"
selected_disease = "Early Blight"
lat, lon = 17.3850, 78.4867 # Example coordinates (Hyderabad)

# Execution
pesticide = crop_database[selected_crop]["diseases"].get(selected_disease, "Unknown")
weather = get_current_weather(lat, lon)

if weather:
    prob = calculate_success(selected_crop, weather)
    
    print(f"--- FARM ADVISOR REPORT ---")
    print(f"Crop: {selected_crop} | Disease: {selected_disease}")
    print(f"Recommended Pesticide: {pesticide}\n")
    print(f"Current Weather: {weather['temp']}°C, Wind: {weather['wind']} km/h")
    print(f"Ideal Weather: {crop_database[selected_crop]['ideal_weather']['min_temp']}°C to {crop_database[selected_crop]['ideal_weather']['max_temp']}°C")
    print(f"Estimated Success Probability: {prob}%")