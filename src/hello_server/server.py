from threading import RLock

from mcp.server.fastmcp import Context, FastMCP
from smithery.decorators import smithery

@smithery.server()
def create_server():
    """Create and configure the MCP server."""
    session_graphs = {}
    graph_lock = RLock()

    def _session_key(ctx: Context | None) -> str:
        return str(getattr(ctx, "session_id", "__default__"))

    def _get_knowledge_graph(ctx: Context | None) -> dict:
        session_key = _session_key(ctx)
        with graph_lock:
            if session_key not in session_graphs:
                session_graphs[session_key] = {
                    "entities": {},
                    "relationships": [],
                    "adjacency_list": {}
                }
            return session_graphs[session_key]

    print("Creating server...")
    server = FastMCP("Knowledge Graph")
    print("Server created.")

    @server.tool()
    def add_entity(id: str, label: str, properties: dict, ctx: Context | None = None) -> str:
        """Add an entity to the knowledge graph."""
        knowledge_graph = _get_knowledge_graph(ctx)
        with graph_lock:
            if id in knowledge_graph["entities"]:
                return f"Entity with id '{id}' already exists."
            knowledge_graph["entities"][id] = {"label": label, "properties": properties}
            if id not in knowledge_graph["adjacency_list"]:
                knowledge_graph["adjacency_list"][id] = []
        return f"Entity '{id}' ({label}) added."

    @server.tool()
    def add_relationship(source_id: str, target_id: str, label: str, properties: dict, ctx: Context | None = None) -> str:
        """Add a relationship between two entities."""
        knowledge_graph = _get_knowledge_graph(ctx)
        with graph_lock:
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
    def query(query_text: str, ctx: Context | None = None) -> str:
        """Query the knowledge graph."""
        knowledge_graph = _get_knowledge_graph(ctx)
        with graph_lock:
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
