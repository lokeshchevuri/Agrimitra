const BACKEND_URL = "http://localhost:8000";

let activeCoordinates = null;
let metadataCache = null;

/**
 * Bootstraps the application data caches, loads initial inputs, and registers user actions.
 */
async function initApplication() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/meta`);
        metadataCache = await response.json();
        
        populateDropdown("cropSelect", Object.keys(metadataCache.crops));
        populateDropdown("stateSelect", Object.keys(metadataCache.locations));
        
        document.getElementById("cropSelect").addEventListener("change", handleCropChange);
        document.getElementById("stateSelect").addEventListener("change", handleStateChange);
        document.getElementById("citySelect").addEventListener("change", resetLocationStatus);
        
        // Manual actions decoupling instant connection fetches on boot loading
        document.getElementById("fetchLocationBtn").addEventListener("click", handleCityFetchManual);
        document.getElementById("gpsBtn").addEventListener("click", triggerNativeGPSPermission);
        document.getElementById("submitBtn").addEventListener("click", runYieldAnalysis);
        
        handleCropChange();
        handleStateChange();
    } catch (err) {
        console.error("Initialization failure:", err);
    }
}

/**
 * Injects array elements safely into target option selectors.
 */
function populateDropdown(elementId, options) {
    const element = document.getElementById(elementId);
    element.innerHTML = options.map(opt => `<option value="${opt}">${opt}</option>`).join("");
}

/**
 * Resets selections and forces user to perform coordinate resolution tracking explicitly.
 */
function resetLocationStatus() {
    activeCoordinates = null;
    document.getElementById("locationStatus").innerText = "Current Position Vector State: Unset (Click 'Fetch Location')";
}

/**
 * Handles dependency variations across sub-menus dynamically.
 */
function handleCropChange() {
    if (!metadataCache) return;
    const currentCrop = document.getElementById("cropSelect").value;
    const dynamicDiseases = ["None / Healthy Crop", ...metadataCache.crops[currentCrop]];
    populateDropdown("diseaseSelect", dynamicDiseases);
}

/**
 * Handles cascading geographic state modifications smoothly.
 */
function handleStateChange() {
    if (!metadataCache) return;
    const currentState = document.getElementById("stateSelect").value;
    populateDropdown("citySelect", metadataCache.locations[currentState]);
    resetLocationStatus();
}

/**
 * Manually executes geocode tracking sequences cleanly on explicit click commands.
 */
async function handleCityFetchManual() {
    const currentCity = document.getElementById("citySelect").value;
    const currentState = document.getElementById("stateSelect").value;
    const statusText = document.getElementById("locationStatus");

    statusText.innerText = `Resolving map coordinates for ${currentCity}...`;

    try {
        const res = await fetch(`${BACKEND_URL}/api/geocode?city=${encodeURIComponent(currentCity)}&state=${encodeURIComponent(currentState)}`);
        
        if (res.ok) {
            const coords = await res.json();
            activeCoordinates = { lat: coords.lat, lon: coords.lon };
            statusText.innerText = `Active Target Location Locked: Dropdown City (${activeCoordinates.lat.toFixed(4)}, ${activeCoordinates.lon.toFixed(4)}, ${currentCity})`;
        } else {
            statusText.innerText = `⚠️ Location lookup failed for ${currentCity}.`;
            activeCoordinates = null;
        }
    } catch (error) {
        statusText.innerText = "⚠️ Network timeout connecting to backend engine geolocation mapper.";
        activeCoordinates = null;
    }
}

/**
 * Polls physical hardware APIs for absolute spatial global coordinates securely.
 */
function triggerNativeGPSPermission() {
    const statusText = document.getElementById("locationStatus");
    statusText.innerText = "Requesting browser hardware permissions...";

    if (!navigator.geolocation) {
        statusText.innerText = "Error: Geolocation hardware missing.";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            activeCoordinates = { lat: position.coords.latitude, lon: position.coords.longitude };
            statusText.innerText = `Active Target Location Locked: Hardware GPS (${activeCoordinates.lat.toFixed(4)}, ${activeCoordinates.lon.toFixed(4)})`;
        },
        (error) => {
            statusText.innerText = `GPS Rejected. Please pick a dropdown city option and click 'Fetch Location'.`;
            activeCoordinates = null;
        },
        { enableHighAccuracy: true, timeout: 7000 }
    );
}

/**
 * Contacts analytic calculation endpoints to output aggregated performance success models.
 */
async function runYieldAnalysis() {
    const resultsCard = document.getElementById("resultsCard");
    const resultsGrid = document.getElementById("resultsGrid");
    
    if (!activeCoordinates) {
        alert("Please select a location and click 'Fetch Location' to synchronize coordinates first.");
        return;
    }

    const crop = document.getElementById("cropSelect").value;
    const disease = document.getElementById("diseaseSelect").value;
    
    try {
        const queryUrl = `${BACKEND_URL}/api/analyze?crop=${encodeURIComponent(crop)}&disease=${encodeURIComponent(disease)}&lat=${activeCoordinates.lat}&lon=${activeCoordinates.lon}`;
        const dataFetch = await fetch(queryUrl);
        const report = await dataFetch.json();
        
        resultsCard.style.display = "block";
        let visualAlertClass = "success-box";
        if (report.success_probability < 75 && report.success_probability >= 50) visualAlertClass = "warning-box";
        if (report.success_probability < 50) visualAlertClass = "error-box";
        
        resultsGrid.innerHTML = `
            <div class="card">
                <h4>📋 Treatment Protocol Summary</h4>
                <p>Threat Status Vector: <b>${report.disease_remedy.disease}</b></p>
                <div class="info-badge">Prescribed Pesticide Remedy: ${report.disease_remedy.prescribed_pesticide}</div>
            </div>
            <div class="card">
                <h4>☀️ Environmental Metrics Validation (Side-by-Side View)</h4>
                <div class="weather-flex-layout">
                    <div class="weather-panel-column">
                        <strong style="color: #48bb78;">Current Recorded</strong>
                        <p>Temp: <b>${report.weather_metrics.current_temp}°C</b> (${report.weather_metrics.temp_status})</p>
                        <p>Humidity: <b>${report.weather_metrics.current_humidity}%</b> (${report.weather_metrics.humidity_status})</p>
                    </div>
                    <div class="weather-panel-column">
                        <strong style="color: #a0aec0;">Ideal Target Crop Bounds</strong>
                        <p>Range: <b>${report.weather_metrics.ideal_temp_range[0]} - ${report.weather_metrics.ideal_temp_range[1]}°C</b></p>
                        <p>Range: <b>${report.weather_metrics.ideal_humidity_range[0]} - ${report.weather_metrics.ideal_humidity_range[1]}%</b></p>
                    </div>
                </div>
            </div>
            <div class="card" style="grid-column: span 2; text-align: center;">
                <h3>🔮 Aggregated Crop Success Probability Assessment</h3>
                <div class="${visualAlertClass}" style="font-size: 32px; font-weight: 800; padding: 20px;">
                    ${report.success_probability}%
                </div>
            </div>
        `;
        resultsCard.scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
        alert("Analysis processing engine execution cycle failed.");
    }
}

window.addEventListener("DOMContentLoaded", initApplication);