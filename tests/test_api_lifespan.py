
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.server import app, manager
from integrations.config_loader import MCPConfigLoader


class TestAPILifespan(unittest.TestCase):

    def test_mcp_connections_closed_on_shutdown(self):
        with patch.object(
            manager.mcp_manager,
            "connect_configured_servers",
            new_callable=AsyncMock,
        ) as mock_connect, patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock,
        ) as mock_close:

            with TestClient(app) as client:
                response = client.get("/")

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {"message": "AI Agent API is running"},
                )

            mock_connect.assert_awaited_once()
            self.assertIsInstance(
                mock_connect.await_args.args[0],
                MCPConfigLoader,
            )
            mock_close.assert_awaited_once()

    def test_mcp_servers_connect_on_startup(self):
        with patch.object(
            manager.mcp_manager,
            "connect_configured_servers",
            new_callable=AsyncMock,
        ) as mock_connect, patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock,
        ) as mock_close:

            with TestClient(app) as client:
                response = client.get("/")

                self.assertEqual(response.status_code, 200)

            mock_connect.assert_awaited_once()
            mock_close.assert_awaited_once()

    def test_startup_failure_closes_connections(self):
        with patch.object(
            manager.mcp_manager,
            "connect_configured_servers",
            new_callable=AsyncMock,
            side_effect=RuntimeError("MCP connection failed"),
        ) as mock_connect, patch.object(
            manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock,
        ) as mock_close:

            with self.assertRaisesRegex(  # noqa: SIM117
                RuntimeError,
                "MCP connection failed",
            ):
                with TestClient(app):
                    pass

            mock_connect.assert_awaited_once()
            mock_close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
