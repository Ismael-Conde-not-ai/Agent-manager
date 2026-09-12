from api.api_client import geminiAI  #, geminiEmbed, ollamaAI, ollamaEmbed
from knowledge.knowledge_base import KnowledgeBase


class ResearchAgent:
    """
    A class to represent a research agent.
    """
    def __init__(self,name = "ResearchAgent"):

        self.name = name
        self.knowledge = KnowledgeBase()

    def research(self, query):
        """
        Perform research based on the given query using AI models.
        """
        context = self.knowledge.search(query)

        promt = f"""
        You are a research AI agent.

        Research question:
        {query}

        Relevant knowledge:
        {context[:2000]}

        Instructions:
        - Analyze the provided knowledge.
        - Extract the most relevant information.
        - Do not invent information.
        - Give a concise research result.

        Return:

        Research Result:
        <answer>

        Sources Used:
        <brief description>
        """

        response = geminiAI(promt).strip()

        return response