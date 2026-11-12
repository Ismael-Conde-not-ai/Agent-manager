import tempfile
from pathlib import Path

from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = MemoryManager(
            persistent=PersistentMemory(path=str(Path(temp_dir) / "memory.json"))
        )
        memory.remember_persistently("last_goal", "Build a modular AI agent")
        print(memory.recall_persistently("last_goal"))


if __name__ == "__main__":
    main()
