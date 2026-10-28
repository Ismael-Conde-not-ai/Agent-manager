
from tools.search_knowledge import search_knowledge


class FakeAgent:
    def get_relevant_context(self):
        return [
            {"text": "RAG retrieves relevant documents."},
            {"text": "The agent uses context to make decisions."}
        ]


result = search_knowledge(FakeAgent())

print(result)

assert "RAG retrieves relevant documents." in result
assert "The agent uses context to make decisions." in result
assert "'text':" not in result

print("All tests passed.")
