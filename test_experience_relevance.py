
import os
import tempfile

from memory.experience_memory import ExperienceMemory


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "experiences.json")
        memory = ExperienceMemory(path=path)

        memory.record({
            "goal": "Research factual information about AI planning",
            "action": "search_knowledge",
            "success": True,
            "result": "Found reliable information about planning",
            "lesson": "Research before writing factual summaries",
        })

        memory.record({
            "goal": "Fix a Python file loading error",
            "action": "work",
            "success": False,
            "result": "The file path was incorrect",
            "error": "FileNotFoundError",
            "lesson": "Verify file paths before opening files",
        })

        tests = [
            (
                "Objetivo coincidente",
                "Research factual information about AI planning",
            ),
            (
                "Objetivo relacionado con otras palabras",
                "Prepare an evidence-based summary of AI planning",
            ),
            (
                "Objetivo no relacionado",
                "Prepare a lesson about classroom pronunciation",
            ),
        ]

        for label, query in tests:
            results = memory.search(query=query, limit=3)

            print(f"\n--- {label} ---")
            print("Consulta:", query)

            if not results:
                print("No se recuperaron experiencias.")
            else:
                for experience in results:
                    print(
                        "Objetivo recuperado:",
                        experience.get("goal"),
                    )

        # 1. Debe recuperar la experiencia coincidente.
        results = memory.search(
            "Research factual information about AI planning"
        )
        assert results
        assert results[0]["goal"] == "Research factual information about AI planning"

        # 2. Debe recuperar la experiencia relacionada.
        results = memory.search(
            "Prepare an evidence-based summary of AI planning"
        )
        assert results
        assert results[0]["goal"] == "Research factual information about AI planning"

        # 3. No debe recuperar experiencias irrelevantes.
        results = memory.search(
            "Prepare a lesson about classroom pronunciation"
        )
        assert results == []

        print("Todas las pruebas de relevancia fueron superadas.")


if __name__ == "__main__":
    main()
