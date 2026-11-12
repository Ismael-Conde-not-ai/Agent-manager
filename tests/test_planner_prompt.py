from unittest.mock import patch

from agents.planner_agent import PlannerAgent
from memory.memory_manager import MemoryManager


def main():
    planner = PlannerAgent(memory_manager=MemoryManager())
    with patch(
        "agents.planner_agent.geminiAI",
        return_value='[{"step": 1, "action": "work", "description": "Apply findings"}]',
    ):
        planner.create_plan("How do AI agents use planning?")


if __name__ == "__main__":
    main()
