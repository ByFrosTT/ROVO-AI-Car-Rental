# ROVO — AI Car Rental Prototype

A Flask web application for browsing a demo car fleet, comparing rental options and finding vehicles through a conversational recommendation assistant. The interface includes location selection, nearby pickup hubs, booking records, owner listings and light/dark themes.

## Highlights

- Fleet browsing with price, category, fuel, seats and transmission filters.
- A local TF-IDF + Ridge recommendation model combined with explicit constraints.
- Pickup proximity calculated from coordinates and approximate hub locations.
- Conversational follow-ups, chat reset, vehicle details and image uploads.

## Quick start on Windows

Open the repository in VS Code and run these commands in PowerShell. Python 3.12 is a conservative choice for this project's scientific Python dependencies.

```powershell
cd ROVO_fullstack_ai
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:ROVO_SECRET = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:5000**. Keep the terminal running. These commands do not require virtual-environment activation. Use `python -m venv .venv` if Python 3.12 is already your default interpreter.

The SQLite database is initialized as needed. The recommendation model is loaded or trained during startup, so the first launch can take longer. The UI requires Flask; opening the HTML directly or using Live Server will not start the API.

## Try the assistant

Choose a pickup location, then try:

1. `Need a fuel efficient car for hilly roads`
2. `Something close to my location`
3. `Need something cheaper`

Use reset when starting a different trip. Browser GPS requires permission; manual location selection is also available.

## Smoke check

With Flask running, open another terminal from the application folder:

```powershell
.\.venv\Scripts\python.exe smoke_test.py
```

The included script exercises the home page, fleet statistics, location resolution and recommendation flow. Its presence is not a claim that it was run for this documentation update.

## Structure

| Path | Purpose |
|---|---|
| `ROVO_fullstack_ai/app.py` | Flask routes, bookings and listings |
| `ROVO_fullstack_ai/ai_engine.py` | Recommendation model and conversation handling |
| `ROVO_fullstack_ai/geo.py` | Pickup hubs and distance calculations |
| `ROVO_fullstack_ai/seed_data.py` | Demo fleet and database initialization |
| `ROVO_fullstack_ai/templates/` | HTML interface |
| `ROVO_fullstack_ai/static/` | Styles, JavaScript and car imagery |

## Demonstration scope

This is a college prototype, not a live rental service. The model learns from synthetic suitability examples; recommendations do not establish real availability or vehicle capability. Payment processing, verified identity, production authentication, booking locks and operational workflows require further implementation. External car images can be unavailable.

The current development server enables debug mode and binds to all interfaces. Run it only in a trusted local environment; production deployment needs an appropriate server, debug disabled and managed secrets. Use a unique ROVO_SECRET rather than the development fallback.

Generated database/model artifacts already present in older commits remain in history. Ignore rules prevent adding new local databases, uploads, caches and secrets; they do not erase tracked files or previous commits.
