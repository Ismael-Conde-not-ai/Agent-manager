#from agents.agent import AIagent
#from core.manager import Manager

#from agents.research_agent import ResearchAgent
from agents.planner_agent import PlannerAgent
"""
research_agent = ResearchAgent()

result = research_agent.research(
    "How do AI agents use planning?"
)

print(result)
"""
planner = PlannerAgent()

goal = "How do AI agents use planning?"

research = """
AI agents can use planning to organize actions,
select tools, and achieve a specific goal.
"""

plan_text = planner.create_plan(goal, research)

print("\nRAW PLAN\n")
print(plan_text)

plan = planner.parse_plan(plan_text)

print("\nPARSED PLAN:\n")
for step in plan:
    print(
        f"Step {step['step']}: "
        f"{step['action']} - "
        f"{step['description']}"
    )