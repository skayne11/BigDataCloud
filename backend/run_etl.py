from etl.fetch_tle import fetch_tle
from etl.parse_tle import parse_tle_text
from etl.load_mongo import load_documents
from etl.load_neo4j import get_driver, reset_graph, load_satellites
import os, sys

def run(group="active"):
    print("[ETL] Fetching TLE...")
    raw = fetch_tle(group)
    print("[ETL] Parsing TLE...")
    docs = parse_tle_text(raw)
    print(f"[ETL] Parsed {len(docs)} objects.")
    # load mongo
    print("[ETL] Loading into MongoDB...")
    n = load_documents(docs, drop_first=True)
    print(f"[ETL] Inserted {n} documents into MongoDB.")
    # load into neo4j
    print("[ETL] Loading into Neo4j...")
    driver = get_driver()
    reset_graph(driver)
    load_satellites(driver, docs)
    print("[ETL] Neo4j load completed.")
    driver.close()

if __name__ == "__main__":
    grp = "active"
    if len(sys.argv) > 1:
        grp = sys.argv[1]
    run(grp)
