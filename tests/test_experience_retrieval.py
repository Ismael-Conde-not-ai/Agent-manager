import os
import tempfile

from memory.experience_memory import ExperienceMemory


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = ExperienceMemory(path=os.path.join(temp_dir, "experiences.json"))
        memory.record({
            "goal": "Research RAG architecture",
            "action": "search_knowledge",
            "success": True,
            "result": "Found relevant RAG documents",
        })
        memory.record({
            "goal": "Research AI planning",
            "action": "search_knowledge",
            "success": True,
            "result": "Found planning documents",
        })
        for item in memory.search(query="RAG research", limit=3):
            print(item["goal"], item["success"])


if __name__ == "__main__":
    main()
