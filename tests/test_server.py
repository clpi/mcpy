import pytest
from hello_server.server import create_server
from mcp.server.fastmcp import Context


@pytest.fixture
def server():
    return create_server()

@pytest.fixture
def default_context():
    return Context("default-session")

def test_query_unknown(server, default_context):
    # Test unrecognized query
    result = server.tools["query"]("random string", ctx=default_context)
    assert result == "Unknown query. Try 'list all entities' or 'list relationships of <entity_id>'."

def test_query_list_all_entities(server, default_context):
    # Setup: add some entities
    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"}, ctx=default_context)
    server.tools["add_entity"](id="2", label="Person", properties={"name": "Bob"}, ctx=default_context)

    # Test list all entities
    result = server.tools["query"]("list all entities", ctx=default_context)
    assert "1" in result
    assert "2" in result

def test_query_list_relationships(server, default_context):
    # Setup: add entities and a relationship
    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"}, ctx=default_context)
    server.tools["add_entity"](id="2", label="Person", properties={"name": "Bob"}, ctx=default_context)
    server.tools["add_relationship"](source_id="1", target_id="2", label="knows", properties={}, ctx=default_context)

    # Test list relationships
    result = server.tools["query"]("list relationships of 1", ctx=default_context)
    assert "knows" in result
    assert "1" in result
    assert "2" in result

def test_query_list_relationships_not_found(server, default_context):
    # Test list relationships for non-existent entity
    result = server.tools["query"]("list relationships of non_existent", ctx=default_context)
    assert result == "Entity 'non_existent' not found."


def test_session_scoped_graph_isolation(server):
    ctx_a = Context("session-a")
    ctx_b = Context("session-b")

    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"}, ctx=ctx_a)

    result_a = server.tools["query"]("list all entities", ctx=ctx_a)
    result_b = server.tools["query"]("list all entities", ctx=ctx_b)

    assert "1" in result_a
    assert result_b == "[]"
