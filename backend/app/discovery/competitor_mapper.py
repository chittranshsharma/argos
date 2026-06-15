import json
import logging
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class CompetitorMapper:
    def discover_competitors(
        self,
        company_name: str,
        website: str = None
    ) -> list[dict]:
        """
        Use Groq to identify top 5 direct competitors.
        Returns list of {name, website, reason} dicts.
        """
        llm = get_groq_llm()
        prompt = f"""
You are a market research analyst.
Identify the top 5 direct competitors of {company_name}.
Website: {website or 'unknown'}

Return ONLY a valid JSON array, no explanation, no markdown:
[
  {{
    "name": "Competitor Name",
    "website": "https://competitor.com",
    "reason": "One sentence why they compete directly"
  }}
]
"""
        try:
            response = llm_invoke(llm, prompt)
            text = response.content if hasattr(response, 'content') else str(response)
            # Strip any markdown fences
            text = text.strip().replace('```json', '').replace('```', '').strip()
            competitors = json.loads(text)
            return competitors[:5]
        except Exception as e:
            logger.error(f"Competitor discovery failed: {e}")
            return []

    def store_competitor_relationships(
        self,
        company_name: str,
        company_id: str,
        competitors: list[dict]
    ) -> None:
        """
        Store COMPETES_WITH relationships in Neo4j.
        """
        from app.memory.graph_db import GraphDB
        graph = GraphDB()
        try:
            for competitor in competitors:
                # Store company node (assuming merge_entity is the method name based on my earlier fix, wait! The prompt says store_entity but I implemented merge_entity in graph_db.py earlier. I'll use merge_entity).
                graph.merge_entity(
                    name=company_name,
                    entity_type="Company",
                    description=f"Tracked company",
                    company_name=company_name
                )
                # Store competitor node
                graph.merge_entity(
                    name=competitor["name"],
                    entity_type="Company",
                    description=competitor.get("reason", "Competitor"),
                    company_name=company_name
                )
                # Store relationship
                graph.merge_relationship(
                    source=company_name,
                    relation="COMPETES_WITH",
                    target=competitor["name"],
                    company_name=company_name
                )
        finally:
            graph.close()