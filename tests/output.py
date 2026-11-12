import sys


def configure_utf8_output():
    """Keep demo output lossless on Windows CP1252 consoles."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
