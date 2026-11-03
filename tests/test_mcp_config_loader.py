
import json
import tempfile
import unittest
from pathlib import Path

from integrations.config_loader import MCPConfigLoader


class TestMCPConfigLoader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "mcp.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_config(self, config):
        with self.config_path.open("w", encoding="utf-8") as file:
            json.dump(config, file)

    def test_load_empty_configuration(self):
        self.write_config({"servers": []})

        loader = MCPConfigLoader(self.config_path)

        self.assertEqual(loader.load()["servers"], [])

    def test_load_enabled_servers(self):
        self.write_config({
            "servers": [
                {
                    "name": "server_a",
                    "enabled": True,
                    "command": "python",
                    "args": [],
                    "env": {},
                    "cwd": None
                },
                {
                    "name": "server_b",
                    "enabled": False,
                    "command": "node"
                }
            ]
        })

        loader = MCPConfigLoader(self.config_path)

        servers = loader.load_enabled_servers()

        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]["name"], "server_a")

    def test_missing_configuration(self):
        loader = MCPConfigLoader(self.config_path)

        with self.assertRaises(FileNotFoundError):
            loader.load()

    def test_duplicate_server_names(self):
        self.write_config({
            "servers": [
                {"name": "server_a", "command": "python"},
                {"name": "server_a", "command": "node"}
            ]
        })

        loader = MCPConfigLoader(self.config_path)

        with self.assertRaisesRegex(ValueError, "Duplicate"):
            loader.load()

    def test_invalid_args(self):
        self.write_config({
            "servers": [
                {
                    "name": "server_a",
                    "command": "python",
                    "args": "invalid"
                }
            ]
        })

        loader = MCPConfigLoader(self.config_path)

        with self.assertRaisesRegex(ValueError, "args"):
            loader.load()

    def test_invalid_enabled_value(self):
        self.write_config({
            "servers": [
                {
                    "name": "server_a",
                    "command": "python",
                    "enabled": "yes"
                }
            ]
        })

        loader = MCPConfigLoader(self.config_path)

        with self.assertRaisesRegex(ValueError, "enabled"):
            loader.load()


if __name__ == "__main__":
    unittest.main()
