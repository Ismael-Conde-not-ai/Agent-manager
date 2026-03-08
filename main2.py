from agent import AIagent
from agentManager import aIagentManager

agent1 = AIagent(name="Alpha",goal="Work efficiently while maintaining energy")

manager = aIagentManager()
manager.add_agent(agent1)
manager.runSimulation(10)