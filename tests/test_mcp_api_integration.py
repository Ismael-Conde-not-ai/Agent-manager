import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.server import app, manager
from integrations.argument_validator import (
    MCPArgumentValidationError,
    MCPToolExecutionError,
)

SERVER_PATH = Path(__file__).with_name("mcp_test_server.py")


class TestMCPAPIIntegration(unittest.TestCase):

    def test_real_mcp_server_through_api(self):
        test_servers = [
            {
                "name": "local_test_server",
                "command": sys.executable,
                "args": [str(SERVER_PATH)],
                "enabled": True,
            }
        ]

        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=test_servers,
        ):
            with TestClient(app) as client:

                # 1. Verificar que el servidor MCP se conectó.
                response = client.get("/mcp/servers")
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    "local_test_server",
                    response.json()["connected_servers"],
                )

                # 2. Verificar el registro dinámico de herramientas.
                response = client.get("/mcp/tools")
                self.assertEqual(response.status_code, 200)

                tool_names = {
                    tool["name"]
                    for tool in response.json()["tools"]
                }

                self.assertIn(
                    "local_test_server.add_numbers",
                    tool_names,
                )
                self.assertIn(
                    "local_test_server.greet",
                    tool_names,
                )

                # 3. Ejecutar una herramienta MCP desde la API.
                response = client.post(
                    "/mcp/tools/local_test_server.add_numbers",
                    json={"a": 10, "b": 20},
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        "success": True,
                        "result": "30",
                        "source": "mcp",
                    },
                )

                # 4. Ejecutar la segunda herramienta.
                response = client.post(
                    "/mcp/tools/local_test_server.greet",
                    json={"name": "Ismael"},
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json()["result"],
                    "Hello, Ismael!",
                )

        # TestClient sale del contexto y ejecuta el apagado de FastAPI.
        self.assertEqual(
            manager.mcp_manager.clients,
            {},
        )

    def test_invalid_arguments_returns_400(self):
        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=[]
        ), patch.object(
            manager.tool_registry,
            "get_tool",
            return_value={"type": "mcp"}
        ), patch.object(
            manager.tool_execution_service,
            "execute",
            new_callable=AsyncMock,
            side_effect=MCPArgumentValidationError("Missing required argument: b")
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/mcp/tools/local_test_server.add_numbers",
                    json={"a": 10}
                )

        self.assertEqual(response.status_code, 400)

    def test_unknown_tool_returns_404(self):
        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=[]
        ), patch.object(
            manager.tool_registry,
            "get_tool",
            return_value=None
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/mcp/tools/unknown_tool",
                    json={"a": 10, "b": 20}
                )

        self.assertEqual(response.status_code, 404)

    def test_mcp_execution_error_returns_502(self):
        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=[]
        ), patch.object(
            manager.tool_registry,
            "get_tool",
            return_value={"type": "mcp"}
        ), patch.object(
            manager.tool_execution_service,
            "execute",
            new_callable=AsyncMock,
            side_effect=MCPToolExecutionError("MCP server unavailable")
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/mcp/tools/local_test_server.add_numbers",
                    json={"a": 10, "b": 20}
                )

        self.assertEqual(response.status_code, 502)

    def test_unexpected_error_returns_500(self):
        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=[]
        ), patch.object(
            manager.tool_registry,
            "get_tool",
            return_value={"type": "mcp"}
        ), patch.object(
            manager.tool_execution_service,
            "execute",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Unexpected internal error")
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/mcp/tools/local_test_server.add_numbers",
                    json={"a": 10, "b": 20}
                )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Internal server error.")

    def test_local_tool_returns_400(self):
        with patch(  # noqa: SIM117
            "api.server.MCPConfigLoader.load_enabled_servers",
            return_value=[]
        ), patch.object(
            manager.tool_registry,
            "get_tool",
            return_value={"type": "local"}
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/mcp/tools/local_tool",
                    json={}
                )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()