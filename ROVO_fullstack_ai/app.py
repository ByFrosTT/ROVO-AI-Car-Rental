from flask import Flask, render_template, request, jsonify, session, send_from_directory
from pathlib import Path
import sqlite3, os, json, uuid
from werkzeug.utils import secure_filename
from seed_data import ensure_database
from ai_engine import RovoAI
from geo import resolve_user_location, search_hubs, nearest_hubs, nearest_pickup

BASE = Path(__file__).resolve().parent
DB = BASE / "rovo.db"
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("ROVO_SECRET", "rovo-dev-secret-change-me")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

ensure_database(DB)
ai = RovoAI(DB, BASE / "models" / "rovo_recommender.joblib")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def parse_user_location(payload=None):
    payload = payload or {}
    lat = payload.get("lat")
    lng = payload.get("lng")
    label = payload.get("label")
    try:
        if lat is not None and lng is not None:
            return resolve_user_location(float(lat), float(lng), label)
    except (TypeError, ValueError):
        pass
    return resolve_user_location(label=label) if label else None

def decorate_car(row, user_location=None):
    d = dict(row)
    d["locations"] = json.loads(d.pop("locations_json"))
    d["images"] = json.loads(d.pop("images_json", "[]") or "[]")
    near = nearest_pickup(d["locations"], user_location)
    if near:
        d["nearest_pickup"] = near["name"]
        d["distance_km"] = near["distance_km"]
    else:
        d["nearest_pickup"] = d.get("location")
        d["distance_km"] = None
    return d

@app.route("/")
def index():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return render_template("index.html")

@app.get("/api/cars")
def cars():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    fuel = request.args.get("fuel", "")
    transmission = request.args.get("transmission", "")
    location = request.args.get("location", "").strip()
    seats = request.args.get("seats", type=int)
    max_price = request.args.get("max_price", type=int, default=999999)
    limit = min(request.args.get("limit", type=int, default=80), 250)
    nearby = request.args.get("nearby", "0") == "1"
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    label = request.args.get("user_location", "")
    user_location = resolve_user_location(lat, lng, label) if lat is not None and lng is not None else (resolve_user_location(label=label) if label else None)

    clauses = ["approved=1", "available=1", "price<=?"]
    args = [max_price]
    if q:
        clauses.append("(brand||' '||model||' '||category||' '||fuel||' '||transmission LIKE ?)")
        args.append(f"%{q}%")
    if category:
        clauses.append("category=?"); args.append(category)
    if fuel:
        clauses.append("fuel=?"); args.append(fuel)
    if transmission:
        clauses.append("transmission=?"); args.append(transmission)
    if seats:
        clauses.append("seats>=?"); args.append(seats)

    con = db()
    raw = list(con.execute(f"SELECT * FROM cars WHERE {' AND '.join(clauses)}", args))
    con.close()
    rows = [decorate_car(r, user_location) for r in raw]
    if location:
        rows = [r for r in rows if any(location.lower() in loc.lower() for loc in r["locations"])]
    if nearby and user_location and user_location.get("lat") is not None:
        rows.sort(key=lambda r: (999 if r["distance_km"] is None else r["distance_km"], -r["rating"], r["price"]))
    else:
        rows.sort(key=lambda r: (-r["rating"], r["price"]))
    return jsonify(rows[:limit])

@app.get("/api/cars/<int:car_id>")
def car_detail(car_id):
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    label = request.args.get("user_location", "")
    user_location = resolve_user_location(lat, lng, label) if lat is not None and lng is not None else (resolve_user_location(label=label) if label else None)
    con = db(); r = con.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone(); con.close()
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify(decorate_car(r, user_location))

@app.post("/api/location/resolve")
def location_resolve():
    data = request.get_json(force=True)
    loc = resolve_user_location(data.get("lat"), data.get("lng"), data.get("label"))
    if loc.get("lat") is not None:
        loc["nearby_hubs"] = nearest_hubs(loc["lat"], loc["lng"], 5)
    else:
        loc["nearby_hubs"] = []
    return jsonify(loc)

@app.get("/api/location/search")
def location_search():
    return jsonify(search_hubs(request.args.get("q", ""), 10))

@app.post("/api/ai/chat")
def ai_chat():
    data = request.get_json(force=True)
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message required"}), 400
    sid = session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    current_car = data.get("current_car_id")
    user_location = parse_user_location(data.get("user_location") or {})
    response = ai.chat(sid, msg, current_car_id=current_car, user_location=user_location)
    return jsonify(response)

@app.post("/api/ai/reset")
def ai_reset():
    sid = session.get("sid")
    if sid:
        ai.reset(sid)
    return jsonify({"ok": True})

@app.post("/api/logout")
def logout():
    sid = session.get("sid")
    if sid:
        ai.reset(sid)
    session.clear()
    return jsonify({"ok": True})

@app.post("/api/bookings")
def create_booking():
    d = request.get_json(force=True)
    required = ["car_id", "driver_name", "licence", "start_date", "duration_days", "pickup_location"]
    if any(not d.get(k) for k in required):
        return jsonify({"error": "Missing booking fields"}), 400
    con = db()
    car = con.execute("SELECT * FROM cars WHERE id=?", (d["car_id"],)).fetchone()
    if not car:
        con.close(); return jsonify({"error": "Car not found"}), 404
    days = max(1, int(d["duration_days"]))
    base = car["price"] * days; platform = 199; taxes = round(base * .18); total = base + platform + taxes
    code = "ROVO" + uuid.uuid4().hex[:8].upper()
    con.execute("""INSERT INTO bookings(code,car_id,driver_name,licence,start_date,duration_days,pickup_location,total,status)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (code, d["car_id"], d["driver_name"], d["licence"], d["start_date"], days, d["pickup_location"], total, "Upcoming"))
    con.commit(); con.close()
    return jsonify({"ok": True, "code": code, "total": total})

@app.get("/api/bookings")
def list_bookings():
    con = db()
    rows = [dict(r) for r in con.execute("""SELECT b.*, c.brand,c.model,c.fuel,c.transmission
                                         FROM bookings b JOIN cars c ON c.id=b.car_id
                                         ORDER BY b.id DESC""")]
    con.close()
    return jsonify(rows)

@app.post("/api/host/list-car")
def list_car():
    form = request.form
    needed = ["brand", "model", "year", "category", "fuel", "transmission", "seats", "price", "location"]
    if any(not form.get(k) for k in needed):
        return jsonify({"error": "Complete all required fields"}), 400
    image_names = []
    for f in request.files.getlist("photos")[:8]:
        if not f.filename:
            continue
        name = f"{uuid.uuid4().hex[:10]}_{secure_filename(f.filename)}"
        f.save(UPLOADS / name); image_names.append(name)
    con = db()
    cur = con.execute("""INSERT INTO cars
      (brand,model,category,seats,price,fuel,transmission,efficiency,comfort,highway,rating,trips,year,color,location,locations_json,bags,available,approved,owner_listing,images_json)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (form["brand"], form["model"], form["category"], int(form["seats"]), int(form["price"]), form["fuel"], form["transmission"],
       8, 8, 8, 4.5, 0, int(form["year"]), "Owner listing", form["location"], json.dumps([form["location"]]), 3, 1, 1, 1, json.dumps(image_names)))
    con.commit(); car_id = cur.lastrowid; con.close()
    return jsonify({"ok": True, "car_id": car_id, "message": "Vehicle submitted and added to the marketplace prototype."})

@app.get("/uploads/<path:name>")
def upload(name):
    return send_from_directory(UPLOADS, name)

@app.get("/api/stats")
def stats():
    con = db()
    car_count = con.execute("SELECT COUNT(*) FROM cars WHERE approved=1").fetchone()[0]
    host_count = con.execute("SELECT COUNT(*) FROM cars WHERE owner_listing=1").fetchone()[0]
    con.close()
    return jsonify({"cars": car_count, "host_listings": host_count, "model": ai.model_info, "location_aware": True, "terrain_aware": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
