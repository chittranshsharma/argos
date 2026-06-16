"""
Argos — Neo4j Graph Database Operations
Stores entities and relationships for the knowledge graph.
Uses lazy initialization for the connection driver.
"""

import logging
from neo4j import GraphDatabase

from app.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)


class GraphDB:
    """Neo4j operations for storing and querying the knowledge graph."""

    def __init__(self):
        self._driver = None
        self._connection_attempted = False

    def _get_driver(self):
        """Lazy initialize the Neo4j driver."""
        if not self._connection_attempted:
            self._connection_attempted = True
            if NEO4J_URI and NEO4J_PASSWORD:
                try:
                    self._driver = GraphDatabase.driver(
                        NEO4J_URI,
                        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                    )
                    # Verify connectivity
                    self._driver.verify_connectivity()
                    logger.info("Connected to Neo4j")
                except Exception as e:
                    logger.warning(f"Neo4j connection failed (non-fatal): {e}")
                    self._driver = None
            else:
                logger.info("Neo4j not configured — graph features disabled")
        return self._driver

    def close(self):
        """Close the Neo4j driver."""
        driver = self._get_driver()
        if driver:
            driver.close()

    def merge_entity(self, name: str, entity_type: str,
                     description: str, company_name: str) -> None:
        """
        Create or update an entity node in Neo4j.
        Labels: Company, Person, Technology, Product, Competitor
        """
        driver = self._get_driver()
        if not driver or not name:
            return

        # Sanitize label
        valid_labels = {"Company", "Person", "Technology", "Product", "Competitor"}
        label = entity_type if entity_type in valid_labels else "Entity"

        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n.description = $description,
            n.company_context = $company_name,
            n.updated_at = datetime()
        RETURN n
        """

        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                session.run(query, name=name, description=description,
                           company_name=company_name)
        except Exception as e:
            logger.error(f"Neo4j merge entity error: {e}")

    def merge_relationship(self, source: str, relation: str,
                           target: str, company_name: str) -> None:
        """
        Create or update a relationship between two entities.
        If entities don't exist, they're created as generic Entity nodes.
        """
        driver = self._get_driver()
        if not driver or not source or not target:
            return

        # Sanitize relation name (Neo4j requires uppercase, no spaces)
        rel_type = relation.upper().replace(" ", "_").replace("-", "_")
        if not rel_type.isidentifier():
            rel_type = "RELATED_TO"

        query = f"""
        MERGE (a {{name: $source}})
        MERGE (b {{name: $target}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r.company_context = $company_name,
            r.updated_at = datetime()
        RETURN a, r, b
        """

        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                session.run(query, source=source, target=target,
                           company_name=company_name)
        except Exception as e:
            logger.error(f"Neo4j merge relationship error: {e}")

    def boost_relationship_weight(self, company_name: str, rel_type: str, increment: float = 0.3) -> None:
        """
        Boost the weight of existing relationships of a specific type for a company.
        Used by the SignalCorrelator to adjust graph confidence without creating new facts.
        """
        driver = self._get_driver()
        if not driver:
            return

        rel_type = rel_type.upper().replace(" ", "_").replace("-", "_")
        
        query = f"""
        MATCH (a)-[r:{rel_type}]->(b)
        WHERE r.company_context = $company_name
        SET r.weight = coalesce(r.weight, 1.0) + $increment,
            r.updated_at = datetime()
        RETURN count(r) as updated_count
        """
        
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, company_name=company_name, increment=increment)
                record = result.single()
                if record and record["updated_count"] > 0:
                    logger.info(f"Boosted weight for {record['updated_count']} {rel_type} edges for {company_name}")
        except Exception as e:
            logger.error(f"Neo4j boost relationship error: {e}")

    def get_company_graph(self, company_name: str) -> dict:
        """
        Get all nodes and relationships associated with a company
        for visualization in the frontend.
        Returns {nodes: [...], links: [...]}.
        """
        driver = self._get_driver()
        if not driver:
            return {"nodes": [], "links": []}

        query = """
        MATCH (n)
        WHERE n.company_context = $company_name
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE m.company_context = $company_name
        RETURN collect(DISTINCT {
            id: elementId(n),
            name: n.name,
            type: labels(n)[0],
            description: n.description
        }) AS nodes,
        collect(DISTINCT {
            source: n.name,
            target: m.name,
            relation: type(r),
            weight: coalesce(r.weight, 1.0)
        }) AS links
        """

        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, company_name=company_name)
                record = result.single()
                if record:
                    nodes = [n for n in record["nodes"] if n.get("name")]
                    links = [l for l in record["links"] if l.get("source") and l.get("target")]
                    return {"nodes": nodes, "links": links}
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")

        return {"nodes": [], "links": []}