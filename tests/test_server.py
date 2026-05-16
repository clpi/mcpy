import pytest
from hello_server.server import create_server


class DummyContext:
    def __init__(self, session_id):
        self.session_id = session_id


@pytest.fixture
def server():
    return create_server()

def test_query_unknown(server):
    # Test unrecognized query
    result = server.tools["query"]("random string")
    assert result == "Unknown query. Try 'list all entities' or 'list relationships of <entity_id>'."

def test_query_list_all_entities(server):
    # Setup: add some entities
    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"})
    server.tools["add_entity"](id="2", label="Person", properties={"name": "Bob"})

    # Test list all entities
    result = server.tools["query"]("list all entities")
    assert "1" in result
    assert "2" in result

def test_query_list_relationships(server):
    # Setup: add entities and a relationship
    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"})
    server.tools["add_entity"](id="2", label="Person", properties={"name": "Bob"})
    server.tools["add_relationship"](source_id="1", target_id="2", label="knows", properties={})

    # Test list relationships
    result = server.tools["query"]("list relationships of 1")
    assert "knows" in result
    assert "1" in result
    assert "2" in result

def test_query_list_relationships_not_found(server):
    # Test list relationships for non-existent entity
    result = server.tools["query"]("list relationships of non_existent")
    assert result == "Entity 'non_existent' not found."


def test_session_scoped_graph_isolation(server):
    ctx_a = DummyContext("session-a")
    ctx_b = DummyContext("session-b")

    server.tools["add_entity"](id="1", label="Person", properties={"name": "Alice"}, ctx=ctx_a)

    result_a = server.tools["query"]("list all entities", ctx=ctx_a)
    result_b = server.tools["query"]("list all entities", ctx=ctx_b)

    assert "1" in result_a
    assert result_b == "[]"
