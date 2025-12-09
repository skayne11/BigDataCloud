from etl.load_neo4j import get_driver, build_graph_for_vis

def get_graph_for_vis(limit=500):
    driver = get_driver()
    try:
        graph = build_graph_for_vis(driver, limit=limit)
        return graph
    finally:
        driver.close()
