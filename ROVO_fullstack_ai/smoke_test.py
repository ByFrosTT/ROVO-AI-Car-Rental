"""Run this while `python app.py` is running to test key ROVO APIs."""
import json, urllib.request, urllib.parse, http.cookiejar

BASE = "http://127.0.0.1:5000"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def get(path):
    with opener.open(BASE + path, timeout=10) as r:
        return r.status, json.loads(r.read().decode())

def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), headers={"Content-Type":"application/json"})
    with opener.open(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode())

print("ROVO smoke test")
print("1) Home:", opener.open(BASE + "/", timeout=10).status)
print("2) Stats:", get("/api/stats"))
status, loc = post("/api/location/resolve", {"lat":19.0522,"lng":72.9005})
print("3) Location resolve:", status, loc.get("label"), loc.get("nearby_hubs", [])[:2])
qs = urllib.parse.urlencode({"limit":3,"lat":19.0522,"lng":72.9005})
status, cars = get("/api/cars?" + qs)
print("4) Cars:", status, [(c["brand"]+" "+c["model"], c.get("distance_km")) for c in cars])
status, ai = post("/api/ai/chat", {"message":"fuel-efficient car for hilly roads close to me", "user_location":{"label":"Chembur","lat":19.0522,"lng":72.9005}})
print("5) AI terrain + location:", status, ai.get("answer"))
print("   recommendations:", [(c["brand"]+" "+c["model"], c.get("distance_km"), c.get("hill_fit")) for c in ai.get("cars", [])[:3]])
status, ai2 = post("/api/ai/chat", {"message":"need something cheaper", "user_location":{"label":"Chembur","lat":19.0522,"lng":72.9005}})
print("6) AI follow-up memory:", status, ai2.get("answer"))
print("PASS if all statuses above are 200 and recommendations change sensibly.")
