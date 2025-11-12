from flask import Flask, render_template, request
from pymongo import MongoClient
from geopy.geocoders import Nominatim
from geopy.distance import distance
import folium
import dotenv, os

dotenv.load_dotenv()

app = Flask(__name__)

# Connexion Mongo
client = MongoClient(os.getenv("URI_MONGODB"))
db = client[os.getenv("DB_NAME")]
collection = db["velib"]

# Fonction pour calculer statistiques
def get_stats(stations):
    total_stations = len(stations)
    total_ebikes = sum(s.get("ebike", 0) for s in stations)
    total_mech = sum(s.get("mechanical", 0) for s in stations)
    return {
        "stations": total_stations,
        "ebikes": total_ebikes,
        "mechanical": total_mech
    }

@app.route("/", methods=["GET", "POST"])
def index():
    map_html = None
    stats = {}
    stations_proches = []

    # Par défaut : afficher toutes les stations
    stations = list(collection.find())

    if request.method == "POST":
        adresse = request.form.get("adresse")
        rayon = float(request.form.get("rayon", 500))  # en mètres
        
        if adresse:
            # Géocodage
            geolocator = Nominatim(user_agent="velib_flask_app")
            location = geolocator.geocode(adresse)
            if location:
                user_lat, user_lon = location.latitude, location.longitude
                
                # Carte centrée sur l'adresse
                map_paris = folium.Map(location=[user_lat, user_lon], zoom_start=15)
                folium.Marker([user_lat, user_lon], popup="📍 " + adresse, icon=folium.Icon(color="red")).add_to(map_paris)
                
                # Filtrer stations proches
                stations_proches = []
                for s in stations:
                    try:
                        lat = s["coordonnees_geo"]["lat"]
                        lon = s["coordonnees_geo"]["lon"]
                        dist = distance((user_lat, user_lon), (lat, lon)).meters
                        if dist > rayon:
                            continue

                        popup_text = f"<b>{s.get('name')}</b><br>🚲 {s.get('numbikesavailable',0)} vélos disponibles<br>🅿️ {s.get('numdocksavailable',0)} bornes libres<br>Distance: {int(dist)} m"
                        folium.Marker([lat, lon], popup=popup_text, icon=folium.Icon(color="blue")).add_to(map_paris)
                        stations_proches.append(s)
                    except Exception:
                        continue
                
                stats = get_stats(stations_proches)
                map_html = map_paris._repr_html_()
    
    # Si pas de POST ou pas d'adresse, afficher toutes les stations
    if not map_html:
        # Carte centrée sur Paris
        map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
        for s in stations:
            try:
                lat = s["coordonnees_geo"]["lat"]
                lon = s["coordonnees_geo"]["lon"]
                popup_text = f"<b>{s.get('name')}</b><br>🚲 {s.get('numbikesavailable',0)} vélos disponibles<br>🅿️ {s.get('numdocksavailable',0)} bornes libres"
                folium.Marker([lat, lon], popup=popup_text, icon=folium.Icon(color="blue")).add_to(map_paris)
            except Exception:
                continue
        stats = get_stats(stations)
        map_html = map_paris._repr_html_()

    return render_template("index.html", map_html=map_html, stats=stats)

if __name__ == "__main__":
    app.run(debug=True)
