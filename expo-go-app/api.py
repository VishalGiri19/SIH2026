import json
import os
import re
from io import BytesIO
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

load_dotenv()

with open("icar_data.json", encoding="utf-8") as file:
    CATALOG: dict[str, dict[str, Any]] = json.load(file)
    MODEL_CROPS = {"Apple", "Blueberry", "Cherry", "Corn (maize)", "Grape", "Orange", "Peach", "Pepper, bell", "Potato", "Raspberry", "Soybean", "Squash", "Strawberry", "Tomato"}
    MODEL_CROPS_BY_KEY = {crop.lower(): crop for crop in MODEL_CROPS}

app = FastAPI(title="Agri Sentinel API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FUSION_API_URL = "https://cough-daylight-argue.ngrok-free.dev/predict"


class WeatherRiskRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop: str
    image_confidence: float = Field(0, ge=0, le=1)
    prev_disease_count_30d: int = Field(0, ge=0)
    prev_pest_count_30d: int = Field(0, ge=0)
    days_since_last_disease: int = Field(365, ge=0)
    days_since_last_pest: int = Field(365, ge=0)


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def find_guidance(label: str) -> dict[str, Any] | None:
    label_text = normalize(label)
    for item in CATALOG.values():
        candidate = normalize(item["disease_name"])
        if label_text == candidate:
            return item
    return None


def model_result(image: Image.Image, crop: str) -> dict[str, Any]:
    from image_model import analyze_crop_image

    raw = json.loads(analyze_crop_image(image, crop))
    if raw.get("status") == "unsupported_crop":
        raise HTTPException(status_code=422, detail=f"The current model does not support {crop} images yet. A model trained on {crop} disease images is required.")
    if raw.get("status") != "success":
        raise HTTPException(status_code=422, detail=raw.get("message", "The model could not analyze this image."))
    return raw["prediction"]


def make_prompt(guidance: dict[str, Any], language: str) -> str:
    return f"""Rewrite this agricultural guidance for a small farmer in {language}. Keep it practical, short, and clear. Do not invent advice, change dosage, or remove safety warnings. Return only valid JSON with arrays named dos_list and donts_list. Disease: {guidance['disease_name']}. Do: {guidance['dos_list']}. Do not: {guidance['donts_list']}."""


async def groq_guidance(guidance: dict[str, Any], language: str) -> dict[str, Any] | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You simplify verified farm guidance. Never create new pesticide recommendations."},
            {"role": "user", "content": make_prompt(guidance, language)},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            rewritten = json.loads(content)
            if isinstance(rewritten.get("dos_list"), list) and isinstance(rewritten.get("donts_list"), list):
                return {"dos_list": rewritten["dos_list"], "donts_list": rewritten["donts_list"], "generated_by": "groq"}
    except (httpx.HTTPError, KeyError, json.JSONDecodeError):
        return None
    return None


async def translate_text(text: str, language: str) -> str:
    if language == "en":
        return text
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(os.getenv("TRANSLATION_API_URL", "https://api.mymemory.translated.net/get"), params={"q": text, "langpair": f"en|{language}"})
            response.raise_for_status()
            translated = response.json().get("responseData", {}).get("translatedText")
            return translated or text
    except (httpx.HTTPError, ValueError):
        return text


async def translate_guidance(guidance: dict[str, Any], language: str) -> dict[str, Any]:
    if language == "en":
        return guidance
    translated = dict(guidance)
    translated["disease_name"] = await translate_text(guidance["disease_name"], language)
    translated["crop"] = await translate_text(guidance["crop"], language)
    translated["dos_list"] = [await translate_text(item, language) for item in guidance["dos_list"]]
    translated["donts_list"] = [await translate_text(item, language) for item in guidance["donts_list"]]
    if guidance.get("organic_alternative"):
        translated["organic_alternative"] = await translate_text(guidance["organic_alternative"], language)
    return translated


async def get_weather_features(latitude: float, longitude: float) -> dict[str, float]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "daily": "precipitation_sum,relative_humidity_2m_mean",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        response.raise_for_status()
        weather = response.json()

    daily = weather.get("daily", {})
    rainfall = daily.get("precipitation_sum", [])
    humidity_history = daily.get("relative_humidity_2m_mean", [])
    humidity = weather["current"]["relative_humidity_2m"]
    rainfall_7d = sum(value or 0 for value in rainfall[:7])
    humid_hours = sum(24 for value in humidity_history[:7] if value is not None and value >= 80)
    return {
        "temperature_c": weather["current"]["temperature_2m"],
        "humidity_pct": humidity,
        "rainfall_mm_7d": rainfall_7d,
        "wind_kmph": weather["current"]["wind_speed_10m"],
        "leaf_wetness_hours": humid_hours,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/weather-risk")
async def weather_risk(request: WeatherRiskRequest) -> dict[str, Any]:
    crop = MODEL_CROPS_BY_KEY.get(request.crop.strip().lower())
    if not crop:
        raise HTTPException(status_code=400, detail="Select a crop supported by the weather model.")
    try:
        weather = await get_weather_features(request.latitude, request.longitude)
        features = {
            **weather,
            "crop": crop,
            "prev_disease_count_30d": request.prev_disease_count_30d,
            "prev_pest_count_30d": request.prev_pest_count_30d,
            "days_since_last_disease": request.days_since_last_disease,
            "days_since_last_pest": request.days_since_last_pest,
            f"crop_{crop.replace(' ', '_').replace(',', '')}": 1,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(FUSION_API_URL, json={"features": features, "image_confidence": request.image_confidence}, headers={"ngrok-skip-browser-warning": "true"})
            response.raise_for_status()
            return {"weather": weather, "model": response.json(), "features_used": features}
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail=f"Weather risk service unavailable: {error}") from error


@app.post("/analyze")
async def analyze(image: UploadFile = File(...), language: str = Form("en"), crop: str = Form(...)) -> dict[str, Any]:
    crop = MODEL_CROPS_BY_KEY.get(crop.strip().lower(), "")
    if not crop:
        raise HTTPException(status_code=400, detail="Select a crop from the dropdown before checking the image.")
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload an image file.")
    try:
        contents = await image.read()
        prediction = model_result(Image.open(BytesIO(contents)).convert("RGB"), crop)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Could not read image: {error}") from error

    catalog_item = find_guidance(prediction["label"])
    if not catalog_item:
        healthy = "healthy" in prediction["label"].lower()
        return {
            "catalog_match": False,
            "prediction_label": prediction["label"],
            "selected_crop": crop,
            "disease_name": prediction["label"],
            "crop": "Detected by image model",
            "confidence_percentage": prediction["confidence_percentage"],
            "dos_list": ["Continue regular field scouting and monitor new growth."] if healthy else ["Contact your local agriculture officer for a confirmed diagnosis."],
            "donts_list": ["No disease treatment is needed based on this result."] if healthy else ["Do not apply chemicals based on this prediction alone."],
            "generated_by": "model-only",
        }

    result: dict[str, Any] = {**catalog_item, "catalog_match": True, "prediction_label": prediction["label"], "selected_crop": crop, "confidence_percentage": prediction["confidence_percentage"], "generated_by": "catalog"}
    rewritten = await groq_guidance(result, language)
    if rewritten:
        result.update(rewritten)
    elif language != "en":
        result = await translate_guidance(result, language)
        result["generated_by"] = "catalog + free translation"
    return result
