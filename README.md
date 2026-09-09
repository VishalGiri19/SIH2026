#🌾 Agri Sentinel — Two-Tier Agricultural Diagnostic & Monitoring Platform


Agri Sentinel is an AI-powered agricultural monitoring and diagnostic system built
to serve both field-level farmers and regional agricultural administrators.

The ecosystem features an Expo Go Mobile App tailored specifically for farmers to
capture and analyze leaf images, alongside a Dual-POV Web Portal designed for
web-based farmer diagnostics and regional administrative command.


##1. SYSTEM OVERVIEW

* Farmer Mobile App (Expo Go): Built strictly for field-level mobile use.
  Features image scanning, risk detection, catalog-backed Do's & Don'ts, CPCB
  dosage calculations, and regional audio advisories.

* Dual-POV Web Portal: Offers a browser-based diagnostic scanner for farmers
  while serving administrators with expert triage tools, GIS outbreak hotspot
  radar maps, satellite NDVI layers, and emergency broadcasts.

* FastAPI Backend API: Central REST API powering vision model inference
  (A2H0H0R1/mobilenet_v2_1.0_224-plant-disease-new), land acreage math, optional
  Groq advisory rewriting, and multilingual translation.


##2. TECH STACK

* Backend Engine: Python 3.10+, FastAPI, Uvicorn, PyTorch / Transformers
* Mobile Frontend: React Native, Expo Go (expo-camera, expo-speech)
* Web Frontend: HTML5, CSS3, JavaScript (ES6), Leaflet.js
* ML Vision Model: A2H0H0R1/mobilenet_v2_1.0_224-plant-disease-new
  (38 classes across 14 crops)
* Agronomic Data: CPCB / ICAR deterministic treatment protocols

##3. STEPS TO START THE WEB APPLICATION & BACKEND API

Prerequisites:
- Install Python 3.10 or higher from python.org
- Ensure Git is installed

###Step 1: Clone & Navigate
  git clone https://github.com/your-username/sih-26.git
  cd sih-26

###Step 2: Create and Activate Virtual Environment
  - On Windows (PowerShell):
      python -m venv venv
      .\venv\Scripts\Activate.ps1
  - On Windows (Command Prompt):
      python -m venv venv
      venv\Scripts\activate.bat
  - On Linux or Mac:
      python3 -m venv venv
      source venv/bin/activate

###Step 3: Install Dependencies
  pip install -r backend/requirements.txt

###Step 4: Start the Backend Server
  python main.py
  (Alternative command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload)

###Step 5: Open the Web Application in Your Browser
  * Web Application: http://localhost:8000
  * Swagger API Docs: http://localhost:8000/docs
  * ReDoc API Docs: http://localhost:8000/redoc

##4. STEPS TO START THE EXPO MOBILE APP (FARMER POV)

Install Node.js LTS first if `node`/`npx` are not on your system PATH, then open a
new terminal:

###Step 1: Navigate & Install Dependencies
  cd mobile
  npm install

###Step 2: Configure Local Network API URL
  For a physical phone running Expo Go, set EXPO_PUBLIC_API_URL in mobile/.env to
  your computer's local network IP address (e.g., http://192.168.1.15:8000), NOT
  127.0.0.1.
  - Keep both your physical phone and computer on the SAME Wi-Fi network.
  - For an Android Emulator, set EXPO_PUBLIC_API_URL=http://10.0.2.2:8000 instead.

###Step 3: Launch Expo Server
  npx expo start

  * How to run: Open the Expo Go app on your physical smartphone and scan the
    QR code displayed in your terminal.

##5. HOW TO USE THE WEB PORTALS

Use the top navigation buttons on the web interface to toggle between both portals:

* Farmer Dashboard: Scan crop leaves using the AI scanner, check weather risks,
  view dynamic CPCB dosage guides based on land acreage, and listen to voice
  advisories.

* Expert Portal: View outbreak hotspot radar maps, inspect satellite NDVI
  layers, validate incoming farmer reports, and send emergency SMS/push broadcasts.


##6. RUN TESTS (OPTIONAL)

To verify backend API functionality and model endpoints:
  python -m pytest backend/tests/
