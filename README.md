# 🌾 TerraSync — AI-Powered Crop Disease & Pest Early Warning System

**Smart India Hackathon 2026 | Problem Statement SIH26131**
**Theme:** Agriculture, FoodTech & Rural Development
**Organization:** Government of Maharashtra

---

## 📋 Problem Statement

Farmers across Maharashtra face significant crop losses due to late detection of plant diseases and pest infestations. Existing solutions are either purely reactive (diagnosis only after visible damage) or require expert agronomists who aren't always accessible in rural areas. There is a need for an **AI-powered, proactive early-warning system** that combines visual diagnosis with environmental risk factors to alert farmers *before* outbreaks escalate.

## 💡 Our Solution

**TerraSync** fuses three signals into a single, explainable risk score for every field:

1. **📸 Image-based diagnosis** — a CNN classifies leaf photos across 38 disease/pest categories (built on the PlantVillage dataset)
2. **🌦️ Live weather data** — humidity, temperature, rainfall, and leaf wetness, since most fungal and pest outbreaks are weather-driven
3. **📊 Field history** — each field's own past disease/pest counts, since outbreaks recur where spores and pest populations already exist

This fusion approach means a farmer can get an early warning **even before symptoms are visible**, using weather + history alone — and once a photo is uploaded, the system combines all three signals into one final, confidence-scored alert.

---

## ✅ Current Feature Status

| Feature | Status |
|---|---|
| Leaf image disease/pest classification | ✅ Working |
| Geospatial hotspot mapping | ✅ Working |
| Weather + field-history risk fusion model | ✅ Built & validated (standalone) |
| Fusion API integration into app/web UI | 🔄 In progress |
| Rule-based pest risk scoring (trap counts + weather thresholds) | 🔄 In progress |
| Expert validation portal | 🔄 In progress |
| Multilingual farmer advisories | 🔜 Planned |

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   Farmer Photo   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐        ┌──────────────────┐
                    │  Image Classifier │       │   Weather API     │
                    │   (classifier.py) │       │ (weather_fusion.py)│
                    └────────┬────────┘        └─────────┬─────────┘
                             │                             │
                             │        ┌──────────────────┐│
                             └───────▶│   Field History   │◀┘
                                      │  (database.py)     │
                                      └─────────┬─────────┘
                                                │
                                      ┌─────────▼─────────┐
                                      │   Fusion Engine     │
                                      │  (risk_fusion.py)   │
                                      └─────────┬─────────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                 ▼
                     ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
                     │ Hotspot Map     │ │ Risk Alerts   │ │ Expert Review   │
                     │ (geospatial.py, │ │ (advisory.py) │ │ (expert.py)     │
                     │  hotspot.py)    │ │               │ │                 │
                     └────────────────┘ └──────────────┘ └────────────────┘
```

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI
- **ML/AI:** TensorFlow/Keras (CNN image classifier), scikit-learn (weather + history fusion model)
- **Database:** SQLite (dev) / Supabase-Postgres (planned production)
- **Frontend:** HTML/CSS/JS (`index.html`), web app
- **Geospatial:** hotspot + mapping logic (`geospatial.py`, `hotspot.py`)
- **Testing:** pytest (`test_ai/`, `test_api/`, `test_fusion/`)

---

## 📁 Repository Structure

```
├── app.py                  # Main API entrypoint
├── classifier.py           # Image-based disease/pest classifier
├── config.py               # App configuration
├── database.py             # DB models & queries
├── weather_fusion.py       # Weather signal processing
├── risk_fusion.py          # Combines image + weather + history into final risk score
├── hotspot.py              # Hotspot detection logic
├── geospatial.py           # Geospatial/mapping utilities
├── advisory.py             # Farmer-facing advisory generation
├── expert.py               # Expert validation workflows
├── farmer.py               # Farmer profile/data handling
├── index.html              # Web app frontend
├── requirements.txt        # Python dependencies
├── test_ai/                # ML model tests
├── test_api/                # API endpoint tests
└── test_fusion/            # Fusion logic tests
```

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/Shailender-CSE/SIH2026.git
cd SIH2026
git checkout sih-round-2

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The API will be available locally; open `index.html` to access the web app.

---

## 👥 Team

Six-member team building TerraSync for SIH26131, GEHU Bhimtal.

---

## 🗺️ Roadmap

- [ ] Wire the fusion model into live app/web UI
- [ ] Complete rule-based pest risk scoring (trap counts + weather thresholds)
- [ ] Launch expert validation portal for flagged/uncertain predictions
- [ ] Add multilingual farmer advisories
- [ ] Deploy fusion API + image model to production hosting

---

## 📄 License

This project was built for Smart India Hackathon 2026 under the Government of Maharashtra's Agriculture, FoodTech & Rural Development theme.
