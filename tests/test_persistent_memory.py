import tempfile
from pathlib import Path

from memory.persistent_memory import PersistentMemory


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = PersistentMemory(path=str(Path(temp_dir) / "memory.json"))
        memory.remember("last_goal", "Research AI agent planning")
        memory.remember("last_tool", "search_knowledge")
        print(memory.get_all())
        print(memory.recall("last_goal"))
        print(memory.forget("last_tool"))


if __name__ == "__main__":
    main()
