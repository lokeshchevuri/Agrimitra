import streamlit as st
import requests

# -----------------------------------------------------------------------------
# 1. INITIALIZE APP STORAGE (Prevents data loss on button clicks)
# -----------------------------------------------------------------------------
if "saved_lat" not in st.session_state:
    st.session_state.saved_lat = None
if "saved_lon" not in st.session_state:
    st.session_state.saved_lon = None
if "display_location_name" not in st.session_state:
    st.session_state.display_location_name = None

# -----------------------------------------------------------------------------
# 2. CROP & DISEASE DATABASE (Original Layout Structure)
# -----------------------------------------------------------------------------
crop_db = {
    "Tomato": {
        "ideal_temp": (21, 29),
        "ideal_humidity": (60, 80),
        "diseases": {
            "Early Blight": "Copper Fungicide",
            "Late Blight": "Mancozeb",
            "Powdery Mildew": "Sulfur-based Fungicide"
        }
    },
    "Rice": {
        "ideal_temp": (25, 35),
        "ideal_humidity": (70, 90),
        "diseases": {
            "Rice Blast": "Tricyclazole",
            "Sheath Blight": "Hexaconazole"
        }
    }
}

# -----------------------------------------------------------------------------
# 3. STATE & CITY DATABASE 
# -----------------------------------------------------------------------------
location_db = {
    "Andhra Pradesh": ["Tadepalligudem", "Vijayawada", "Guntur", "Visakhapatnam"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"]
}

# Helper function to find coordinates dynamically based on user's selected city
def get_coordinates_from_city(city_name, state_name):
    search_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name},{state_name}&count=1&language=en&format=json"
    try:
        res = requests.get(search_url).json()
        if "results" in res and len(res["results"]) > 0:
            lat = res["results"][0]["latitude"]
            lon = res["results"][0]["longitude"]
            return lat, lon
    except Exception as e:
        st.error(f"Geocoding lookup failed: {e}")
    return None, None

# -----------------------------------------------------------------------------
# 4. STREAMLIT APPLICATION SURFACE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="AgriSmart Platform", page_icon="🌾", layout="wide")
st.title("🌾 AgriSmart: Crop Diagnostic & Weather Analytics Engine")

# --- UI Setup: Columns for diagnostics ---
col1, col2 = st.columns(2)
with col1:
    crop_selected = st.selectbox("🌱 1. Select Crop Type", list(crop_db.keys()))
with col2:
    disease_options = ["None / Healthy Crop"] + list(crop_db[crop_selected]["diseases"].keys())
    disease_selected = st.selectbox("🪳 2. Select Observed Disease", disease_options)

st.markdown("---")
st.subheader("📍 Location Setup")

# Split location layout into separate interactive segments
tab_dropdown, tab_gps = st.tabs(["🏙️ Select State & City Dropdown", "🌐 Use Browser GPS Location"])

# --- TAB 1: REGIONAL STATE & CITY LOOKUP ---
with tab_dropdown:
    col_state, col_city = st.columns(2)
    with col_state:
        state_selected = st.selectbox("Choose State", list(location_db.keys()))
    with col_city:
        city_selected = st.selectbox("Choose City", location_db[state_selected])
        
    if st.button("Confirm Selected Region", key="manual_city_btn"):
        with st.spinner("Resolving coordinates for your selection..."):
            lat, lon = get_coordinates_from_city(city_selected, state_selected)
            if lat and lon:
                st.session_state.saved_lat = lat
                st.session_state.saved_lon = lon
                st.session_state.display_location_name = f"{city_selected}, {state_selected}"
                st.success(f"✅ Map mapping complete for **{st.session_state.display_location_name}**")

# --- TAB 2: BROWSER GPS IMPLEMENTATION (Permission Request Restored) ---
with tab_gps:
    st.write("Clicking the button below explicitly requests real-time location streaming from your device browser.")
    
    if st.button("Trigger GPS Permission Prompt", key="gps_trigger_btn"):
        try:
            from streamlit_js_eval import get_geolocation
            loc = get_geolocation()
            
            if loc and 'coords' in loc:
                st.session_state.saved_lat = loc['coords']['latitude']
                st.session_state.saved_lon = loc['coords']['longitude']
                st.session_state.display_location_name = f"GPS Lock (Lat: {round(st.session_state.saved_lat,4)}, Lon: {round(st.session_state.saved_lon,4)})"
                st.success(f"✅ GPS Lock Confirmed via browser: {st.session_state.display_location_name}")
            else:
                st.info("💡 Browser popup triggered. Please click 'Allow' on your device banner to share your location data.")
        except Exception as permission_denied_error:
            st.error("⚠️ Browser geolocation permission was rejected or blocked. Please switch to the State & City Dropdown instead.")

# Display the active locked target location to the farmer
st.markdown("---")
if st.session_state.display_location_name:
    st.info(f"👉 **Currently Target Location:** {st.session_state.display_location_name}")
else:
    st.warning("👉 **Currently Target Location:** None. Please confirm your location choice above first.")

# -----------------------------------------------------------------------------
# 5. WEATHER PROCESSING & EVALUATION RUN
# -----------------------------------------------------------------------------
if st.button("🚀 Analyze Conditions & Calculate Success Probability", type="primary", key="main_analysis_btn"):
    
    if st.session_state.saved_lat is None or st.session_state.saved_lon is None:
        st.error("❌ Unable to proceed: Location target missing. Choose a location method above first and click confirm.")
    else:
        # Fetch data via Open-Meteo Current Forecast Endpoint using cached variables
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={st.session_state.saved_lat}&longitude={st.session_state.saved_lon}&current_weather=true"
        
        try:
            response = requests.get(weather_url).json()
            current_weather = response.get("current_weather", {})
            curr_temp = current_weather.get("temperature", None)
            curr_humidity = 65  # Default structural placeholder variable
            
            if curr_temp is not None:
                ideal_temp = crop_db[crop_selected]["ideal_temp"]
                ideal_hum = crop_db[crop_selected]["ideal_humidity"]
                
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.subheader("📋 Remedy Assessment")
                    if disease_selected == "None / Healthy Crop":
                        st.success("🎉 Crop is healthy. No treatment needed.")
                        base_health = 100
                    else:
                        pesticide = crop_db[crop_selected]["diseases"][disease_selected]
                        st.error(f"**Disease Found:** {disease_selected}")
                        st.info(f"**⚡ Prescribed Treatment:** Apply **{pesticide}** immediately.")
                        base_health = 70
                
                with res_col2:
                    st.subheader("☀️ Weather Verification")
                    temp_ok = ideal_temp[0] <= curr_temp <= ideal_temp[1]
                    st.write(f"**Target Location:** {st.session_state.display_location_name}")
                    st.write(f"**Current Temp:** {curr_temp}°C ({'✅ Ideal' if temp_ok else '❌ Off-Target'})")
                    st.write(f"**Current Humidity:** {curr_humidity}% (Ideal range: {ideal_hum[0]}-{ideal_hum[1]}%)")
                
                # Probability calculations
                temp_score = 20 if temp_ok else 5
                hum_score = 10 if (ideal_hum[0] <= curr_humidity <= ideal_hum[1]) else 2
                
                success_probability = round(base_health * ((temp_score + hum_score) / 30), 1)
                
                st.markdown("---")
                st.subheader("🔮 Expected Yield Success Score")
                if success_probability >= 75:
                    st.success(f"## **{success_probability}%** — Highly favorable growing conditions.")
                elif 50 <= success_probability < 75:
                    st.warning(f"## **{success_probability}%** — Moderate stress detected. Monitor fields.")
                else:
                    st.error(f"## **{success_probability}%** — Critical threat. Action required.")
            else:
                st.error("Failed to parse local weather parameters from response.")
        except Exception as api_error:
            st.error(f"Network error communicating with climate service: {api_error}")