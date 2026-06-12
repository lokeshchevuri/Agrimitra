# AgriMitra 🌾

AgriMitra is a smart agricultural companion application designed to empower farmers with data-driven insights. By analyzing real-time climate data against crop requirements, AgriMitra helps farmers understand the success rate of common crops, identify prevalent crop diseases, and find effective cures.

---

## 🚀 Features

- **Crop & Disease Intelligence**: Access a comprehensive database of common crops, their widespread diseases, and proven cures/treatments.
- **Climate Analysis**: Fetches current local weather data and compares it against the **ideal climate thresholds** required for specific crops.
- **Crop Success Rate**: Uses an algorithm to calculate and display a predictive success percentage for crops based on real-time environmental factors.
- **Dual Location Selection**:
  1. **GPS Mode**: Automatically fetches high-accuracy real-time geographic coordinates.
  2. **Manual Mode**: A built-in curated list of major states and their important agricultural cities for quick selection.

---

## 🛠️ Project Structure

Based on your repository, here is how the core files interact:
* `app.js` / `index.html` - The frontend user interface for selecting locations and viewing success rates.
* `app.py` - The backend Python service handling climate data calculations and crop algorithms.
* `crops.json` - Database containing crop thresholds, diseases, and cure data.
* `places.json` - Pre-configured list of supported states and major cities.
* `requirements.txt` - Python dependencies needed to run the backend application.

---

## 📦 Installation & Setup

### Prerequisites
Make sure you have both **Node.js** (for frontend/fullstack JS execution) and **Python 3.x** installed.

### 1. Clone the Repository
```bash
git clone [https://github.com/lokeshchevuri/Agrimitra.git]
(https://github.com/lokeshchevuri/Agrimitra.git)
cd Agrimitra
2. Set Up the Python BackendInstall the required dependencies listed in requirements.txt:Bashpip install -r requirements.txt
3. Run the ApplicationLaunch your backend application:
Bash
python app.py
📊 How it Works (Core Logic)Location Input: The farmer grants GPS permission or selects their region from the dropdown menu.Weather Fetching: The app sends the coordinates to a weather API to retrieve live parameters (Temperature, Humidity, Rainfall).
Success Rate Calculation:
The app compares live metrics against the boundaries stored in crops.json
Actionable Insights:
 The system outputs a percentage score along with custom preventative measures for common crop diseases.
🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to check the issues page if you want to help expand the crops.json database or improve the climate matching algorithm.
---

