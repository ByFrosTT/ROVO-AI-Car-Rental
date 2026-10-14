# ROVO Full-Stack AI Car Rental — V3

ROVO V3 is a runnable Flask product prototype with a trained hybrid recommendation model, SQLite fleet database, location-aware recommendations, terrain/hill awareness, bookings, owner vehicle listings, image uploads, light/dark themes and responsive UI.

## What's new in V3
- Browser GPS coordinates are now sent to the backend (with permission).
- Pickup hubs have real approximate latitude/longitude values.
- Haversine distance is calculated from the user to each vehicle's available pickup hubs.
- AI understands phrases such as **near me**, **closest**, **close to my location** and ranks by real pickup distance.
- AI understands **hilly roads**, **ghats**, **mountains**, Lonavala/Mahabaleshwar/Matheran etc. and includes hill suitability in ranking.
- AI balances hill capability + efficiency rather than blindly choosing the highest-efficiency vehicle.
- AI recommendations are a horizontal scroll/slider, with working **View car** buttons.
- Car cards and details show the nearest pickup hub and distance when location is available.
- Header location has a pencil/edit control and supports precise or manual locations.
- AI has a **new chat/reset** control.
- Logout exists in the top bar and profile page.
- More Mumbai-region pickup hubs were added; every seeded vehicle gets 3 unique hubs.
- Owner-uploaded images are displayed when available.

## AI model
The local model is a TF-IDF + Ridge hybrid ranker. It is trained on 11k+ synthetic prompt/vehicle suitability examples and then combined with deterministic safety/business constraints and live features:
- price
- efficiency
- comfort
- highway suitability
- hill/terrain suitability
- distance to pickup
- seats
- luggage
- fuel
- transmission

This is intentionally a hybrid recommender: learned ranking handles natural-language similarity, while hard requirements and live distance stay deterministic and explainable.

## Run in VS Code (Windows)
1. Open this folder in VS Code.
2. Terminal → New Terminal.
3. Create environment: `python -m venv venv`
4. Activate: `venv\Scripts\activate`
5. Install: `pip install -r requirements.txt`
6. Start: `python app.py`
7. Open `http://127.0.0.1:5000`

Do not use Live Server for `index.html`; the site requires Flask APIs.

## Full smoke test
Keep Flask running, open a second VS Code terminal (activate the same venv), then run:

`python smoke_test.py`

It checks home, stats, GPS/hub resolution, distance-aware car results, hill+location AI ranking and conversational follow-up memory.

## Best manual AI test
1. Click the pencil beside the location and use precise location or choose **Chembur** manually.
2. Ask: `need a car for hilly roads and should be fuel efficient`
3. Ask: `somewhere close from my location`
4. Ask: `need something cheaper`
5. Use the horizontal recommendation slider and press **View car**.
6. Press ↻ in the AI header to start a new trip.

## Production services still required before a real commercial launch
OTP/account authentication, KYC/licence verification, payment gateway, production PostgreSQL, cloud object storage/CDN, map routing/geocoding provider, availability locking, insurance/deposit workflows, owner moderation, notifications, admin dashboard and deployment with HTTPS/secrets.
