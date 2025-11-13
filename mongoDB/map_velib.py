import folium
from pymongo import MongoClient
import dotenv, os
from geopy.geocoders import Nominatim
from geopy.distance import distance

dotenv.load_dotenv()

# Connexion Mongo
client = MongoClient(os.getenv("URI_MONGODB"))
db = client["testdb"]
collection = db["velib"]

# Demande d'adresse à l'utilisateur
adresse = input("Entrez une adresse à Paris : ")

# Géocodage de l'adresse
geolocator = Nominatim(user_agent="velib_map_app")
location = geolocator.geocode(adresse)

if location is None:
    print("Adresse introuvable.")
    exit()

user_lat, user_lon = location.latitude, location.longitude
rayon_m = 500  # distance en mètres autour de l'adresse

# Récupération des stations
stations = list(collection.find())

# Création de la carte centrée sur l'adresse
map_paris = folium.Map(location=[user_lat, user_lon], zoom_start=15)

# Ajout d'un marqueur pour l'adresse de l'utilisateur
folium.Marker(
    [user_lat, user_lon],
    popup="📍 " + adresse,
    icon=folium.Icon(color="red")
).add_to(map_paris)

# Ajout des stations proches
for s in stations:
    try:
        lat = s["coordonnees_geo"]["lat"]
        lon = s["coordonnees_geo"]["lon"]

        # Calcul de la distance par rapport à l'adresse
        dist = distance((user_lat, user_lon), (lat, lon)).meters
        if dist > rayon_m:
            continue  # ignore les stations trop loin

        name = s.get("name", "Station inconnue")
        bikes = s.get("numbikesavailable", 0)
        docks = s.get("numdocksavailable", 0)

        popup_text = f"<b>{name}</b><br>🚲 {bikes} vélos disponibles<br>🅿️ {docks} bornes libres<br>Distance : {int(dist)} m"
        folium.Marker([lat, lon], popup=popup_text, icon=folium.Icon(color="blue")).add_to(map_paris)
    except Exception:
        continue

# Sauvegarde dans un fichier HTML
map_paris.save("velib_map.html")
print("✅ Carte générée : ouvre 'velib_map.html' dans ton navigateur 🌍")
