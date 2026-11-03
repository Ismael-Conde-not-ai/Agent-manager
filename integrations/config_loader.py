
import json
from pathlib import Path


class MCPConfigLoader:

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent
                / "config"
                / "mcp_servers.json"
            )

        self.config_path = Path(config_path)

    def load(self):
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"MCP configuration not found: {self.config_path}"
            )

        with self.config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise ValueError("MCP configuration must be an object")  # noqa: TRY004

        servers = config.get("servers")

        if not isinstance(servers, list):
            raise ValueError("'servers' must be a list")  # noqa: TRY004

        names = set()

        for server in servers:
            self._validate_server(server, names)

        return config

    def load_enabled_servers(self):
        config = self.load()

        return [
            server
            for server in config["servers"]
            if server.get("enabled", True)
        ]

    def _validate_server(self, server, names):
        if not isinstance(server, dict):
            raise ValueError("Each server configuration must be an object")  # noqa: TRY004

        name = server.get("name")
        command = server.get("command")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Each server must have a valid name")

        if name in names:
            raise ValueError(f"Duplicate MCP server name: {name}")

        names.add(name)

        if not isinstance(command, str) or not command.strip():
            raise ValueError(
                f"Server '{name}' must have a valid command"
            )

        args = server.get("args", [])

        if not isinstance(args, list) or not all(
            isinstance(arg, str) for arg in args
        ):
            raise ValueError(
                f"Server '{name}': args must be a list of strings"
            )

        env = server.get("env", {})

        if not isinstance(env, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in env.items()
        ):
            raise ValueError(
                f"Server '{name}': env must contain string values"
            )

        cwd = server.get("cwd")

        if cwd is not None and not isinstance(cwd, str):
            raise ValueError(
                f"Server '{name}': cwd must be a string or null"
            )

        enabled = server.get("enabled", True)

        if not isinstance(enabled, bool):
            raise ValueError(  # noqa: TRY004
                f"Server '{name}': enabled must be boolean"
            )
