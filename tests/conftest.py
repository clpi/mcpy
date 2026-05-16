import sys
from unittest.mock import MagicMock

# Mock mcp.server.fastmcp
mcp_mock = MagicMock()
fastmcp_module_mock = MagicMock()

class MockFastMCP:
    def __init__(self, *args, **kwargs):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    def list_tools(self):
        return list(self.tools.values())

class MockContext:
    def __init__(self, session_id=None):
        self.session_id = session_id

fastmcp_module_mock.FastMCP = MockFastMCP
fastmcp_module_mock.Context = MockContext
sys.modules["mcp"] = mcp_mock
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = fastmcp_module_mock

# Mock smithery.decorators
smithery_module_mock = MagicMock()
smithery_decorators_module_mock = MagicMock()

# In server.py: from smithery.decorators import smithery
# Then @smithery.server()
smithery_obj = MagicMock()
smithery_obj.server.return_value = lambda x: x
smithery_decorators_module_mock.smithery = smithery_obj

sys.modules["smithery"] = smithery_module_mock
sys.modules["smithery.decorators"] = smithery_decorators_module_mock
