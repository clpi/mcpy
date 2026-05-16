import pytest
from hello_server.server import create_server, knowledge_graph

@pytest.fixture(autouse=True)
def clear_knowledge_graph():
    knowledge_graph["entities"].clear()
    knowledge_graph["relationships"].clear()
    knowledge_graph["adjacency_list"].clear()
    yield

@pytest.fixture
def server():
    return create_server()

def test_add_entity_success(server):
    entity_id = "test-1"
    label = "TestEntity"
    properties = {"key": "value"}

    result = server.tools["add_entity"](id=entity_id, label=label, properties=properties)

    assert entity_id in knowledge_graph["entities"]
    assert knowledge_graph["entities"][entity_id]["label"] == label
    assert knowledge_graph["entities"][entity_id]["properties"] == properties
    assert result == f"Entity '{entity_id}' ({label}) added."

def test_add_entity_already_exists(server):
    entity_id = "test-2"
    label = "TestEntity"
    properties = {"key": "value"}

    server.tools["add_entity"](id=entity_id, label=label, properties=properties)
    result = server.tools["add_entity"](id=entity_id, label="AnotherLabel", properties={})

    assert knowledge_graph["entities"][entity_id]["label"] == label
    assert knowledge_graph["entities"][entity_id]["properties"] == properties
    assert result == f"Entity with id '{entity_id}' already exists."

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
