from mcp.server.fastmcp import FastMCP
from smithery.decorators import smithery

# In-memory storage for the knowledge graph
knowledge_graph = {
    "entities": {},
    "relationships": [],
    "adjacency_list": {}
}

@smithery.server()
def create_server():
    """Create and configure the MCP server."""
    print("Creating server...")
    server = FastMCP("Knowledge Graph")
    print("Server created.")

    @server.tool()
    def add_entity(id: str, label: str, properties: dict) -> str:
        """Add an entity to the knowledge graph."""
        if id in knowledge_graph["entities"]:
            return f"Entity with id '{id}' already exists."
        knowledge_graph["entities"][id] = {"label": label, "properties": properties}
        if id not in knowledge_graph["adjacency_list"]:
            knowledge_graph["adjacency_list"][id] = []
        return f"Entity '{id}' ({label}) added."

    @server.tool()
    def add_relationship(source_id: str, target_id: str, label: str, properties: dict) -> str:
        """Add a relationship between two entities."""
        if source_id not in knowledge_graph["entities"]:
            return f"Source entity '{source_id}' not found."
        if target_id not in knowledge_graph["entities"]:
            return f"Target entity '{target_id}' not found."

        relationship = {
            "source": source_id,
            "target": target_id,
            "label": label,
            "properties": properties
        }
        knowledge_graph["relationships"].append(relationship)

        # Ensure adjacency list entries exist
        if source_id not in knowledge_graph["adjacency_list"]:
            knowledge_graph["adjacency_list"][source_id] = []
        if target_id not in knowledge_graph["adjacency_list"]:
            knowledge_graph["adjacency_list"][target_id] = []

        knowledge_graph["adjacency_list"][source_id].append(relationship)
        if source_id != target_id:
            knowledge_graph["adjacency_list"][target_id].append(relationship)
        return f"Relationship '{label}' from '{source_id}' to '{target_id}' added."

    @server.tool()
    def query(query_text: str) -> str:
        """Query the knowledge graph."""
        if query_text == "list all entities":
            return str(list(knowledge_graph["entities"].keys()))

        parts = query_text.split()
        if query_text.startswith("list relationships of"):
            entity_id = parts[-1]
            if entity_id not in knowledge_graph["entities"]:
                return f"Entity '{entity_id}' not found."

            relations = knowledge_graph["adjacency_list"].get(entity_id, [])
            return str(relations)

        return "Unknown query. Try 'list all entities' or 'list relationships of <entity_id>'."

    return server