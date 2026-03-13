from fastapi import FastAPI
from agents.agent import AIagent
from core.agentManager import aIagentManager

app = FastAPI()

manager = aIagentManager()
agent = None

@app.get("/")
def read_root():
    return {"message": "AI Agent API is running"}

@app.get("/status")
def get_status():
    return {"status":"Agent system ready"}

@app.post("/agent/create")
def create_agent():

    global agent

    agent = AIagent(
        name="Alpha",
        goal="Work efficiently while maintaining energy"
    )
    manager.add_agent(agent)

    return {"message":"Agent created"}

@app.post("/agent/step")
def run_agent_step():

    if not agent:
        return{"error":"Agent not created"}
    
    agent.autonomousStep()

    return{
        "energy":agent.energy,
        "status":agent.status,
        "plan_remaining":agent.plan
    }

@app.get("/agent/status")
def agent_status():

    if not agent:
        return {"error":"Agent not created"}
    
    return {
        "name":agent.name,
        "goal":agent.goal,
        "energy":agent.energy,
        "status":agent.status,
        "memory":agent.memory
    }