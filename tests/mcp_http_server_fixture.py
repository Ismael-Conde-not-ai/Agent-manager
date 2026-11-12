import asyncio
import socket
import sys
from contextlib import asynccontextmanager
from pathlib import Path


SERVER_PATH = Path(__file__).with_name("mcp_http_test_server.py")


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@asynccontextmanager
async def running_http_server():
    port = _free_port()
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(SERVER_PATH),
        "--port",
        str(port),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        for _ in range(100):
            if process.returncode is not None:
                error = await process.stderr.read()
                raise RuntimeError(
                    f"HTTP MCP test server exited: {error.decode(errors='replace')}"
                )

            try:
                reader, writer = await asyncio.open_connection(
                    "127.0.0.1",
                    port,
                )
                writer.close()
                await writer.wait_closed()
                break
            except OSError:
                await asyncio.sleep(0.05)
        else:
            raise RuntimeError("HTTP MCP test server did not start")

        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        if process.returncode is None:
            process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
