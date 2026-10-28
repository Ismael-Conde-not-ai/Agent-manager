from memory.experience_memory import ExperienceMemory

memory = ExperienceMemory(
    path="data/test_experience_memory.json"
)

# Limpiar los datos de prueba de ejecuciones anteriores.
if memory.path:
    memory.experiences = []
    memory.save()


memory.record({
    "goal": "Research RAG architecture",
    "action": "search_knowledge",
    "success": True,
    "result": "Found relevant RAG documents"
})

memory.record({
    "goal": "Research RAG architecture",
    "action": "search_knowledge",
    "success": False,
    "result": "Knowledge search returned no useful results",
    "error": "No relevant documents"
})

memory.record({
    "goal": "Create a calendar event",
    "action": "calendar_create",
    "success": True,
    "result": "Calendar event created"
})

memory.record({
    "goal": "Research AI planning",
    "action": "search_knowledge",
    "success": True,
    "result": "Found planning documents"
})


print("\n=== SEARCH: RAG ===")

for item in memory.search(
    query="RAG research",
    limit=3
):
    print(item["goal"], item["success"])


print("\n=== SUCCESSFUL SEARCHES ===")

for item in memory.search(
    query="research",
    success=True
):
    print(item["goal"], item["success"])


print("\n=== FAILED KNOWLEDGE SEARCHES ===")

for item in memory.search(
    action="search_knowledge",
    success=False
):
    print(item["goal"], item["result"])

results = memory.search(
    query="RAG research",
    limit=3
)

scores = [
    sum(
        1
        for term in {"rag", "research"}
        if term in " ".join([
            str(item.get("goal", "")),
            str(item.get("action", "")),
            str(item.get("result", "")),
            str(item.get("error", "")),
            str(item.get("lesson", ""))
        ]).lower()
    )
    for item in results
]

print("Matching terms:", scores)