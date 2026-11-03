
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.server import app, manager
from integrations.config_loader import MCPConfigLoader


class TestAPILifespan(unittest.TestCase):

    def test_mcp_connections_closed_on_shutdown(self):
        with patch.object(
            MCPConfigLoader,
            "load_enabled_servers",
            return_value=[],
        ), patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock,
        ) as mock_close_all:

            with TestClient(app) as client:
                response = client.get("/")

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {"message": "AI Agent API is running"},
                )

            mock_close_all.assert_awaited_once()

    
    def test_enabled_mcp_servers_connect_on_startup(self):

        servers = [
            {
                "name": "server_a",
                "command": "python",
                "args": ["server.py"],
                "env": {},
                "cwd": None
            }
        ]

        with patch.object(
            MCPConfigLoader,
            "load_enabled_servers",
            return_value=servers
        ), patch.object(
            manager.mcp_manager,
            "connect_server",
            new_callable=AsyncMock
        ) as mock_connect, patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock
        ) as mock_close:

            with TestClient(app) as client:
                response = client.get("/")

                self.assertEqual(response.status_code, 200)

            mock_connect.assert_awaited_once_with(
                server_name="server_a",
                command="python",
                args=["server.py"],
                env={},
                cwd=None
            )

            mock_close.assert_awaited_once()

    def test_startup_failure_closes_connections(self):

        servers = [
            {
                "name": "server_a",
                "command": "python",
                "args": [],
                "env": {},
                "cwd": None
            }
        ]

        with patch.object(
            MCPConfigLoader,
            "load_enabled_servers",
            return_value=servers
        ), patch.object(
            manager.mcp_manager,
            "connect_server",
            new_callable=AsyncMock,
            side_effect=RuntimeError("MCP connection failed")
        ) as mock_connect, patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock
        ) as mock_close:

            with self.assertRaises(RuntimeError):  # noqa: SIM117
                with TestClient(app):
                    pass

            mock_connect.assert_awaited_once()
            mock_close.assert_awaited_once()



if __name__ == "__main__":
    unittest.main()
