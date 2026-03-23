from fastapi import FastAPI
from agents.agent import AIagent
from core.agentManager import aIagentManager
from core.config_loader import load_agent_config

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

    config = load_agent_config()
    agent = AIagent(
        name=config["name"],
        goal=config["goal"],
        initial_energy=config["initial_energy"],
        initial_status=config["initial_status"]
    )
    manager.add_agent(agent)

    return {"message":"Agent created from config"}

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

@app.get("/system/health")
def system_health():
    '''It tells if the system is operational'''
    return{
        "status":"running",
        "agent_loaded": agent is not None
    }

@app.get("/system/metrics")
def system_metrics ():
    '''Observability of agent metrics'''
    if not agent:
        return{"error":"Agent not initialized"}
    
    return{
        "agent_name":agent.name,
        "energy": agent.energy,
        "status":agent.status,
        "memory_entries":len(agent.memory),
        "remaining_plan_steps": len(agent.plan)
    }

@app.get("/system/logs")
def get_logs():
    '''Returns last 20 log entries, if not return error log'''
    try:
        with open("logs/agent.log","r") as file:
            logs = file.readlines()

        return {"logs":logs[-20:]}
    
    except FileNotFoundError:
        return {"error","Log file not found"}