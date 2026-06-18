import os
import sys
sys.path.append(os.getcwd())
from app.memory.graph_db import GraphDB

def check_graph():
    graph = GraphDB()
    driver = graph._get_driver()
    if not driver:
        print("No Neo4j driver.")
        return
        
    with driver.session() as session:
        # Check specific edges
        for rel in ["ACQUIRED", "INVESTED_IN", "WORKS_AT", "COMPETES_WITH", "PARTNERS_WITH"]:
            res = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) as c")
            count = res.single()["c"]
            print(f"{rel}: {count}")
            
        # Check generic edges from old analyze_signals
        for rel in ["USES", "HIRED", "ACQUIRED_BY", "PARTNERED", "RELATED_TO"]:
            res = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) as c")
            count = res.single()["c"]
            print(f"{rel}: {count}")
            
    graph.close()

if __name__ == "__main__":
    check_graph()
