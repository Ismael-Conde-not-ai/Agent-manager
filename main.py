from agents.agent import AIagent
from core.manager import Manager

from agents.research_agent import ResearchAgent

research_agent = ResearchAgent()

result = research_agent.research(
    "How do AI agents use planning?"
)

print(result)