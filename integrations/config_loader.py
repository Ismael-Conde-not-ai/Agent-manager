
import json
from pathlib import Path


class MCPConfigLoader:

    SUPPORTED_TRANSPORTS = {"stdio", "streamable-http"}

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
            raise ValueError("MCP configuration must be an object")

        servers = config.get("servers")

        if not isinstance(servers, list):
            raise ValueError("'servers' must be a list")

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
            raise ValueError(
                "Each server configuration must be an object"
            )

        name = server.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Each server must have a valid name")

        if name in names:
            raise ValueError(f"Duplicate MCP server name: {name}")

        names.add(name)

        enabled = server.get("enabled", True)

        if not isinstance(enabled, bool):
            raise ValueError(
                f"Server '{name}': enabled must be boolean"
            )

        transport = server.get("transport")

        # Backward compatibility:
        # If transport is omitted, use the old STDIO configuration.
        if transport is None:
            self._validate_stdio(server, name)
            return

        if not isinstance(transport, dict):
            raise ValueError(
                f"Server '{name}': transport must be an object"
            )

        transport_type = transport.get("type")

        if (
            not isinstance(transport_type, str)
            or transport_type not in self.SUPPORTED_TRANSPORTS
            ):
            raise ValueError(
                f"Server '{name}': unsupported transport type "
                f"'{transport_type}'"
            )

        if transport_type == "stdio":
            self._validate_stdio(transport, name)

        elif transport_type == "streamable-http":
            self._validate_http(transport, name)

    def _validate_stdio(self, config, name):
        command = config.get("command")

        if not isinstance(command, str) or not command.strip():
            raise ValueError(
                f"Server '{name}' must have a valid command"
            )

        args = config.get("args", [])

        if not isinstance(args, list) or not all(
            isinstance(arg, str) for arg in args
        ):
            raise ValueError(
                f"Server '{name}': args must be a list of strings"
            )

        env = config.get("env", {})

        if not isinstance(env, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in env.items()
        ):
            raise ValueError(
                f"Server '{name}': env must contain string values"
            )

        cwd = config.get("cwd")

        if cwd is not None and not isinstance(cwd, str):
            raise ValueError(
                f"Server '{name}': cwd must be a string or null"
            )

    def _validate_http(self, config, name):
        url = config.get("url")

        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                f"Server '{name}': HTTP transport requires a valid URL"
            )

        if not url.startswith(("http://", "https://")):
            raise ValueError(
                f"Server '{name}': URL must use HTTP or HTTPS"
            )
