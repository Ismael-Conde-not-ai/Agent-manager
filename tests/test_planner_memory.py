import tempfile
from pathlib import Path
from unittest.mock import patch

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
            "goal": "How do AI agents use planning?",
            "action": "search_knowledge",
            "success": True,
            "result": "Found information about planning and decision-making.",
            "lesson": "Research relevant information before creating a plan.",
        })
        planner_agent = PlannerAgent(memory_manager=memory)
        with patch("agents.planner_agent.geminiAI", return_value="[]"):
            planner_agent.create_plan("How do AI agents use planning?")


if __name__ == "__main__":
    main()
