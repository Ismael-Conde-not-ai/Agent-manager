
import unittest

from integrations.transport_factory import MCPTransportFactory
from integrations.transports.stdio_transport import StdioTransport
from integrations.transports.http_transport import StreamableHTTPTransport


class TestMCPTransportFactory(unittest.TestCase):

    def test_create_legacy_stdio_transport(self):
        config = {
            "name": "local_server",
            "command": "python",
            "args": ["server.py"],
            "cwd": "project"
        }

        transport = MCPTransportFactory.create(config)

        self.assertIsInstance(transport, StdioTransport)
        self.assertEqual(transport.server.command, "python")
        self.assertEqual(transport.server.args, ["server.py"])
        self.assertEqual(transport.server.cwd, "project")

    def test_create_nested_stdio_transport(self):
        config = {
            "name": "local_server",
            "transport": {
                "type": "stdio",
                "command": "python",
                "args": ["server.py"]
            }
        }

        transport = MCPTransportFactory.create(config)

        self.assertIsInstance(transport, StdioTransport)
        self.assertEqual(transport.server.command, "python")

    def test_create_http_transport(self):
        config = {
            "name": "http_server",
            "transport": {
                "type": "streamable-http",
                "url": "http://127.0.0.1:8080/mcp"
            }
        }

        transport = MCPTransportFactory.create(config)

        self.assertIsInstance(
            transport,
            StreamableHTTPTransport
        )
        self.assertEqual(
            transport.url,
            "http://127.0.0.1:8080/mcp"
        )

    def test_unsupported_transport(self):
        config = {
            "name": "invalid_server",
            "transport": {
                "type": "websocket"
            }
        }

        with self.assertRaisesRegex(ValueError, "Unsupported"):
            MCPTransportFactory.create(config)


if __name__ == "__main__":
    unittest.main()
