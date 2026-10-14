from math import radians, sin, cos, sqrt, atan2

# Approximate centre coordinates for supported pickup hubs.
# These are intentionally hub-level rather than street addresses.
HUBS = {
    "Thane": (19.2183, 72.9781),
    "Vile Parle": (19.1006, 72.8438),
    "Bandra": (19.0607, 72.8362),
    "Andheri": (19.1136, 72.8697),
    "Powai": (19.1176, 72.9060),
    "Chembur": (19.0522, 72.9005),
    "Lower Parel": (18.9988, 72.8258),
    "Navi Mumbai": (19.0330, 73.0297),
    "Borivali": (19.2307, 72.8567),
    "Dadar": (19.0178, 72.8478),
    "Worli": (19.0170, 72.8170),
    "Goregaon": (19.1663, 72.8526),
    "Mulund": (19.1726, 72.9565),
    "BKC": (19.0678, 72.8677),
    "Kurla": (19.0726, 72.8845),
    "Airoli": (19.1590, 72.9986),
    "Vashi": (19.0771, 72.9986),
    "Kharghar": (19.0473, 73.0699),
    "Wadala": (19.0174, 72.8562),
    "Sion": (19.0434, 72.8617),
    "Ghatkopar": (19.0867, 72.9081),
    "Malad": (19.1874, 72.8484),
    "Kandivali": (19.2045, 72.8520),
}

ALIASES = {
    "bkc": "BKC",
    "bandra kurla complex": "BKC",
    "vileparle": "Vile Parle",
    "vile parle east": "Vile Parle",
    "vile parle west": "Vile Parle",
    "navi mumbai": "Navi Mumbai",
    "lowerparel": "Lower Parel",
}

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2-lat1)
    dl = radians(lon2-lon1)
    a = sin(dp/2)**2 + cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*r*atan2(sqrt(a), sqrt(1-a))

def normalize_hub(name):
    if not name:
        return None
    raw = " ".join(str(name).strip().split())
    low = raw.lower()
    if low in ALIASES:
        return ALIASES[low]
    for hub in HUBS:
        if hub.lower() == low:
            return hub
    return None

def search_hubs(query, limit=8):
    q = (query or "").strip().lower()
    if not q:
        return [{"name": n, "lat": v[0], "lng": v[1]} for n, v in list(HUBS.items())[:limit]]
    matches = []
    for name, (lat, lng) in HUBS.items():
        score = 0
        nl = name.lower()
        if nl == q:
            score = 100
        elif nl.startswith(q):
            score = 80
        elif q in nl:
            score = 60
        elif any(part in nl for part in q.split()):
            score = 30
        if score:
            matches.append((score, name, lat, lng))
    matches.sort(reverse=True)
    return [{"name": n, "lat": lat, "lng": lng} for _, n, lat, lng in matches[:limit]]

def nearest_hubs(lat, lng, limit=5):
    out = []
    for name, (hlat, hlng) in HUBS.items():
        out.append({"name": name, "lat": hlat, "lng": hlng, "distance_km": round(haversine_km(lat, lng, hlat, hlng), 1)})
    out.sort(key=lambda x: x["distance_km"])
    return out[:limit]

def resolve_user_location(lat=None, lng=None, label=None):
    if lat is not None and lng is not None:
        nearest = nearest_hubs(float(lat), float(lng), 1)[0]
        return {
            "label": nearest["name"],
            "lat": float(lat),
            "lng": float(lng),
            "nearest_hub": nearest["name"],
            "distance_to_hub_km": nearest["distance_km"],
        }
    hub = normalize_hub(label)
    if hub:
        hlat, hlng = HUBS[hub]
        return {"label": hub, "lat": hlat, "lng": hlng, "nearest_hub": hub, "distance_to_hub_km": 0.0}
    return {"label": label or "Mumbai", "lat": None, "lng": None, "nearest_hub": None, "distance_to_hub_km": None}

def nearest_pickup(locations, user_location):
    if not user_location or user_location.get("lat") is None or user_location.get("lng") is None:
        return None
    lat, lng = float(user_location["lat"]), float(user_location["lng"])
    best = None
    for loc in locations:
        hub = normalize_hub(loc)
        if not hub:
            continue
        hlat, hlng = HUBS[hub]
        d = haversine_km(lat, lng, hlat, hlng)
        if best is None or d < best[1]:
            best = (hub, d)
    if not best:
        return None
    return {"name": best[0], "distance_km": round(best[1], 1)}
