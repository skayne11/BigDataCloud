from pymongo import MongoClient
from neo4j import GraphDatabase
import dotenv, os

# Charger les variables d'environnement (.env)
dotenv.load_dotenv()

# --- Connexion MongoDB ---
mongo_uri = os.getenv("URI_CLOUD")
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client["velib"]
mongo_col = mongo_db["Paris"]

# --- Connexion Neo4j ---
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password123"
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


def create_constraints(tx):
    """
    Crée des contraintes pour éviter les doublons
    """
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Station) REQUIRE s.stationcode IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Arrondissement) REQUIRE a.name IS UNIQUE")


def insert_station(tx, station):
    """
    Crée un nœud Station relié à son Arrondissement
    """
    tx.run("""
        MERGE (a:Arrondissement {name: $arr})
        MERGE (s:Station {stationcode: $code})
        SET s.name = $name,
            s.bikes = $bikes,
            s.docks = $docks,
            s.lat = $lat,
            s.lon = $lon
        MERGE (s)-[:LOCATED_IN]->(a)
        """,
        arr=station.get("nom_arrondissement_communes", "Inconnu"),
        code=station.get("stationcode"),
        name=station.get("name"),
        bikes=station.get("numbikesavailable", 0),
        docks=station.get("numdocksavailable", 0),
        lat=station.get("coordonnees_geo", {}).get("lat"),
        lon=station.get("coordonnees_geo", {}).get("lon")
    )


def sync_mongo_to_neo4j():
    """
    Récupère les stations depuis Mongo et les pousse dans Neo4j
    """
    with driver.session() as session:
        session.execute_write(create_constraints)

        stations = list(mongo_col.find())
        print(f"{len(stations)} stations à synchroniser...")

        for s in stations:
            session.execute_write(insert_station, s)

        print("Synchronisation MongoDB → Neo4j terminée !")


if __name__ == "__main__":
    sync_mongo_to_neo4j()
    driver.close()
