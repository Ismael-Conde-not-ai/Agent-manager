import tempfile
from pathlib import Path

from agents.planner_agent import PlannerAgent
from core.manager import Manager
from memory.experience_memory import ExperienceMemory
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = MemoryManager(
            persistent=PersistentMemory(path=str(Path(temp_dir) / "persistent.json")),
            experience=ExperienceMemory(path=str(Path(temp_dir) / "experiences.json")),
        )
        memory.record_experience({
            "goal": "Research AI agent planning",
            "action": "search_knowledge",
            "success": True,
            "result": "Relevant documents found",
        })
        print(memory.search_experiences("planning", limit=5))

    manager = Manager()
    planner_agent = PlannerAgent(memory_manager=manager.memory_manager)
    print("¿Comparten memoria?", planner_agent.memory_manager is manager.memory_manager)


if __name__ == "__main__":
    main()
