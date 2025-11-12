import requests
from pymongo import MongoClient, errors
import os, dotenv

dotenv.load_dotenv()

# Connexion Mongo
uri = os.getenv("URI_MONGODB")
client = MongoClient(uri)
db = client["testdb"]
collection = db["velib"]

# Création d'un index unique sur stationcode (avant toute insertion)
collection.create_index("stationcode", unique=True)

# Récupération des données depuis l'API Vélib
response = requests.get(
    "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=100"
)
data = response.json()

# Vérifie qu'il y a bien une clé "results"
if "results" in data:
    documents = data["results"]

    if documents:
        try:
            # Insertion dans MongoDB
            collection.insert_many(documents, ordered=False)
            print(f"{len(documents)} stations Vélib insérées avec succès 🚴‍♂️")
        except errors.BulkWriteError as e:
            print("Certaines stations existent déjà, insertion partielle effectuée ✅")
    else:
        print("Aucune donnée à insérer.")
else:
    print("Structure de réponse inattendue :", data.keys())
