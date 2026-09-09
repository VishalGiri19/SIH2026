# Agri Sentinel

Expo farmer app for crop image risk detection, catalog-backed dos and don'ts, optional Groq rewriting, and free translation.

## Run the API

```powershell
py -m pip install -r requirements.txt
$env:GROQ_API_KEY = "your-key" # optional
py -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Run the Expo app

Install Node.js LTS first if `node`/`npx` are not on PATH, then:

```powershell
cd mobile
npm install
npx expo start
```

For a physical phone, set `EXPO_PUBLIC_API_URL` to the computer's local network IP, not `127.0.0.1`.

The included `mobile/.env` uses the current Wi-Fi address. Keep the phone and computer on the same network. For an Android Emulator, use `EXPO_PUBLIC_API_URL=http://10.0.2.2:8000` instead.
