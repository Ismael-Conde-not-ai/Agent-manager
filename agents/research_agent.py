from api.api_client import geminiAI  #, geminiEmbed, ollamaAI, ollamaEmbed
from core.contracts import ErrorCategory
from core.exceptions import InternalAgentError
from knowledge.knowledge_base import KnowledgeBase


class ResearchAgent:
    """
    A class to represent a research agent.
    """
    def __init__(self, knowledge_base=None, name="ResearchAgent"):

        self.name = name
        self.knowledge = (
            knowledge_base
            if knowledge_base is not None
            else KnowledgeBase()
        )

    def research(self, query):
        """
        Perform research based on the given query using AI models.
        """
        try:
            context = self.knowledge.get_context(query, limit=3)
        except Exception as error:
            raise InternalAgentError(
                "Knowledge retrieval failed.",
                code="research_retrieval_failed",
                category=ErrorCategory.RESEARCH,
                details={"query_length": len(query)},
                cause=error,
            ) from error

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
        - If the knowledge is insufficient, say so.
        - Give a concise research result.

        Return:

        Research Result:
        <answer>

        Sources Used:
        <brief description>
        """

        try:
            response = geminiAI(promt).strip()
        except Exception as error:
            raise InternalAgentError(
                "Research model execution failed.",
                code="research_model_failed",
                category=ErrorCategory.RESEARCH,
                cause=error,
            ) from error

        return response