from flask import Flask, render_template, jsonify, abort, request
from services.mongo_service import get_all_satellites, get_satellite_by_name
from services.neo4j_service import get_graph_for_vis
from pymongo import MongoClient
import os, random
from etl.tle_latlon import tle_to_latlon

app = Flask(__name__, template_folder="./templates", static_folder="./static")

MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "space")

# URI avec authentification
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

# Connexion à MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]

@app.route("/")
def index():
    sats = get_all_satellites()
    # Pass list of dicts with at least 'name'
    return render_template("index.html", satellites=sats, title="Satellites")

@app.route("/satellite/<name>")
def satellite_view(name):
    sat = get_satellite_by_name(name)
    if not sat:
        abort(404, description="Satellite non trouvé")
    # Provide data to template
    return render_template("satellite.html", sat=sat["name"], data=sat, title=f"Satellite {sat['name']}")

@app.route("/graph")
def graph_view():
    graph_data = get_graph_for_vis()
    return render_template("graph.html", graph=graph_data, title="Graphe")

@app.route("/search")
def search():
    query = request.args.get("q", "")  # Récupère le texte de recherche
    if query:
        # Recherche par nom de satellite, insensible à la casse
        satellites = list(db.satellites.find(
            {"name": {"$regex": query, "$options": "i"}}, 
            {"_id": 0}  # On n'affiche pas l'ID Mongo
        ))
    else:
        satellites = []
    return render_template("search.html", satellites=satellites, query=query)

@app.route("/globe")
def globe_view():
    return render_template("globe.html", title="Globe 3D")

# Provide JSON endpoints useful for front-end or tests
@app.route("/api/satellites")
def api_satellites():
    satellites = list(db.satellites.find({}, {"_id": 0, "name": 1, "approx_alt_km": 1, "orbit_class": 1}))

    sats_clean = []
    for sat in satellites:
        alt_km = sat.get("approx_alt_km")
        # filtrage des valeurs invalides
        if alt_km is None or alt_km <= 0 or alt_km > 50000:
            continue

        sats_clean.append({
            "name": sat["name"],
            "latitude": random.uniform(-90, 90),   # temporaire
            "longitude": random.uniform(-180, 180),# temporaire
            "altitude": alt_km * 1000,             # km -> m
            "orbit_class": sat.get("orbit_class", "UNKNOWN")
        })
    return jsonify(sats_clean)

@app.route("/api/satellite/<name>")
def api_satellite(name):
    sat = get_satellite_by_name(name)
    if not sat:
        return jsonify({"error": "Satellite non trouvé"}), 404

    # Ajouter latitude, longitude et altitude pour correspondre à /api/satellites
    alt_km = sat.get("approx_alt_km")

    lat, lon, alt = tle_to_latlon(sat["line1"], sat["line2"])

    if alt_km is None or alt_km <= 0 or alt_km > 50000:
        altitude_m = None
    else:
        altitude_m = alt_km * 1000  # km -> m

    sat_with_position = {
        "name": sat["name"],
        "latitude": lat,   # temporaire
        "longitude": lon,# temporaire
        "altitude": alt,
        "orbit_class": sat.get("orbit_class", "UNKNOWN"),
        "line1": sat.get("line1"),
        "line2": sat.get("line2"),
        "catalog_number": sat.get("catalog_number"),
        "type": sat.get("type", "Inconnu")
    }

    return jsonify(sat_with_position)


@app.route("/api/graph")
def api_graph():
    return jsonify(get_graph_for_vis())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
