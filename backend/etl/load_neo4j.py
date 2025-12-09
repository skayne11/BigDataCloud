from neo4j import GraphDatabase
import os

NEO_URI = os.getenv("NEO_URI", "bolt://neo4j:7687")
NEO_USER = os.getenv("NEO_USER", "neo4j")
NEO_PWD = os.getenv("NEO_PWD", "password")

def get_driver():
    return GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PWD))

def reset_graph(driver):
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")

def load_satellites(driver, docs):
    """
    docs: list of dict with keys name, catalog_number, approx_alt_km, orbit_class, line1, line2
    We create:
      (s:Satellite {name, catalog_number, approx_alt_km})
      (o:Orbit {class: orbit_class})
      (s)-[:IN_ORBIT]->(o)
    """
    with driver.session() as s:
        for d in docs:
            s.run("""
                MERGE (sat:Satellite {name: $name})
                SET sat.catalog_number = $catalog_number,
                    sat.approx_alt_km = $approx_alt_km,
                    sat.orbit_class = $orbit_class,
                    sat.line1 = $line1,
                    sat.line2 = $line2
                """, {
                    "name": d.get("name"),
                    "catalog_number": d.get("catalog_number"),
                    "approx_alt_km": d.get("approx_alt_km"),
                    "orbit_class": d.get("orbit_class"),
                    "line1": d.get("line1"),
                    "line2": d.get("line2")
                })
            # Merge orbit node for class
            s.run("""
                MERGE (o:Orbit {class: $orbit_class})
                """, {"orbit_class": d.get("orbit_class")})
            # Create relation
            s.run("""
                MATCH (sat:Satellite {name: $name})
                MATCH (o:Orbit {class: $orbit_class})
                MERGE (sat)-[:IN_ORBIT]->(o)
                """, {"name": d.get("name"), "orbit_class": d.get("orbit_class")})

def build_graph_for_vis(driver, limit=500):
    """
    Returns a dict {nodes: [...], edges: [...]} suitable for vis.js
    nodes: {id: <int or str>, label: <string>, group: <string>}
    edges: {from: id, to: id}
    """
    with driver.session() as s:
        # get satellites and orbit nodes and relationships
        q = """
        MATCH (sat:Satellite)-[r:IN_ORBIT]->(o:Orbit)
        RETURN sat.name AS sname, sat.catalog_number AS cat, sat.approx_alt_km AS alt, o.class AS oclass
        LIMIT $limit
        """
        res = s.run(q, {"limit": limit})
        nodes = []
        edges = []
        node_ids = {}
        idx = 1
        # create nodes and edges
        for rec in res:
            sname = rec["sname"]
            oclass = rec["oclass"]
            alt = rec["alt"]
            # satellite node
            if sname not in node_ids:
                node_ids[sname] = idx
                nodes.append({"id": idx, "label": sname, "group": "satellite", "title": f"alt={alt}"})
                idx += 1
            # orbit node (use class as id label)
            orbit_label = f"Orbit:{oclass}"
            if orbit_label not in node_ids:
                node_ids[orbit_label] = idx
                nodes.append({"id": idx, "label": oclass, "group": "orbit"})
                idx += 1
            edges.append({"from": node_ids[sname], "to": node_ids[orbit_label]})
        return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    # quick manual test (requires env vars and running neo4j)
    driver = get_driver()
    reset_graph(driver)
    load_satellites(driver, [{"name":"TEST-1","catalog_number":99999,"approx_alt_km":550,"orbit_class":"LEO","line1":"","line2":""}])
    print(build_graph_for_vis(driver))
