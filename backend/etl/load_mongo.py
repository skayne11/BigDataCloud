from pymongo import MongoClient
import os

# Récupération des credentials depuis les variables d'environnement
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
DB_NAME = os.getenv("MONGO_DB", "space")
COLLECTION = os.getenv("MONGO_COLLECTION", "satellites")

# Construction de l'URI avec auth
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

def get_client():
    return MongoClient(MONGO_URI)

def load_documents(docs, drop_first=True):
    client = get_client()
    db = client[DB_NAME]
    col = db[COLLECTION]
    if drop_first:
        col.delete_many({})
    if docs:
        col.insert_many(docs)
    return len(docs)

def list_all():
    client = get_client()
    db = client[DB_NAME]
    return list(db[COLLECTION].find({}, {"_id": 0}))

def find_by_name(name):
    client = get_client()
    db = client[DB_NAME]
    return db[COLLECTION].find_one({"name": name}, {"_id": 0})
