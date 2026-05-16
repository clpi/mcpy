import pytest
from hello_server.server import create_server, knowledge_graph

@pytest.fixture(autouse=True)
def clear_knowledge_graph():
    """Clear the knowledge graph before each test to ensure isolation."""
    knowledge_graph["entities"].clear()
    knowledge_graph["relationships"].clear()
    yield

@pytest.fixture
def server():
    """Yield a configured server."""
    return create_server()

@pytest.mark.asyncio
async def test_add_entity_success(server):
    """Test adding a new entity to the knowledge graph."""
    entity_id = "test-1"
    label = "TestEntity"
    properties = {"key": "value"}

    # FastMCP server.call_tool returns a tuple.
    # Example from exploration:
    # ([TextContent(type='text', text="Entity '1' (Person) added.", annotations=None, meta=None)], {'result': "Entity '1' (Person) added."})
    # or sometimes we just check the knowledge graph directly depending on the testing approach

    # We will test the inner logic using server.call_tool
    result = await server.call_tool("add_entity", {"id": entity_id, "label": label, "properties": properties})

    # Check if we get a tuple and extract the actual return value
    # Since we explored it returns ([TextContent(...)], {'result': '...'})
    # But to be robust, let's just check the knowledge_graph

    assert entity_id in knowledge_graph["entities"]
    assert knowledge_graph["entities"][entity_id]["label"] == label
    assert knowledge_graph["entities"][entity_id]["properties"] == properties

    # Also verify the return message is formatted properly
    # Also verify the return message is formatted properly
    _, result_dict = result
    assert result_dict["result"] == f"Entity '{entity_id}' ({label}) added."

@pytest.mark.asyncio
async def test_add_entity_already_exists(server):
    """Test adding an entity that already exists."""
    entity_id = "test-2"
    label = "TestEntity"
    properties = {"key": "value"}

    # Add it once
    await server.call_tool("add_entity", {"id": entity_id, "label": label, "properties": properties})

    # Add it again
    result = await server.call_tool("add_entity", {"id": entity_id, "label": "AnotherLabel", "properties": {}})

    # Verify the knowledge graph wasn't modified by the second call
    assert knowledge_graph["entities"][entity_id]["label"] == label
    assert knowledge_graph["entities"][entity_id]["properties"] == properties

    # Verify the error message
    _, result_dict = result
    assert result_dict["result"] == f"Entity with id '{entity_id}' already exists."
