from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

from agents.agent import AIagent
from agents.evaluator_agent import EvaluatorAgent
from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from core.config_loader import load_agent_config
from core.manager import Manager
from core.orchestrator import Orchestrator
from integrations.argument_validator import (
    MCPArgumentValidationError,
    MCPToolExecutionError,
)
from integrations.config_loader import MCPConfigLoader
from memory.memory_context_builder import MemoryContextBuilder

manager = Manager()
orchestrator = Orchestrator(manager)

agent = None

research_agent = ResearchAgent()
planner_agent = PlannerAgent( memory_manager=manager.memory_manager)  # Pass the memory manager to the planner agent
executor_agent = ExecutorAgent(tool_execution_service=manager.tool_execution_service)  # Pass the tool execution service to the executor agent
evaluator_agent = EvaluatorAgent()

manager.add_agent(research_agent)  # Add the research agent to the manager
manager.add_agent(planner_agent)  # Add the planner agent to the manager
manager.add_agent(executor_agent) # Add the executor agent to the manager
manager.add_agent(evaluator_agent) # Add the evaluator agent to the manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Loads MCP configuration, connects enabled servers,
    and closes all connections on application shutdown.
    """

    try:
        config_loader = MCPConfigLoader()
        servers = config_loader.load_enabled_servers()

        for server in servers:
            await manager.mcp_manager.connect_server(
                server_name=server["name"],
                command=server["command"],
                args=server.get("args", []),
                env=server.get("env"),
                cwd=server.get("cwd")
            )

        yield

    finally:
        await manager.mcp_manager.close_all()


app = FastAPI(lifespan=lifespan)

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
    agent.memory_manager = manager.memory_manager  # Assign the shared memory manager to the agent
    agent.memory_context_builder = MemoryContextBuilder(agent.memory_manager)  # Initialize the memory context builder for the agent
    
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
        "memory":agent.short_term_memory
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
        "memory_entries":len(agent.long_term_memory),
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
        return {"error":"Log file not found"}

@app.post("/research")
def research(query: str):
    '''Research agent performs research on a given query'''
    result = research_agent.research(query)

    return{
        "agent": research_agent.name,
        "query": query,
        "result": result
    }

@app.post("/plan")
def create_plan(goal: str):
    '''Planner agent creates a plan based on a given goal'''
    plan_text = planner_agent.create_plan(goal)
    plan = planner_agent.parse_plan(plan_text)

    return{
        "agent": planner_agent.name,
        "goal": goal,
        "plan": plan
    }

@app.post("/workflow/full")
async def full_workflow(goal: str):
    '''Conducts research, creates a plan, and executes it.'''
    if not agent:
        return {"error": "No main agent created"}
    try:
        result = await orchestrator.run(goal, agent)
        return result
    except ValueError as e:
        return {"error": str(e)}

@app.get("/agents")
def list_agents():
    '''Returns a list of all agents managed by the system'''
    return{
        "agents":manager.list_agents()
    }

@app.get("/orchestrator/status")
def orchestrator_status():
    '''Returns the status of the orchestrator and its agents'''
    return{
        "status":"ready",
        "agents":manager.list_agents()
    }

@app.get("/knowledge/search")
def knowledge_search(query: str):
    '''Searches the knowledge base for relevant information based on a query'''
    if not agent:
        return {"error": "No main agent created"}
    
    results = agent.knowledge.search(query, limit=3)
    return {
        "query": query,
        "results": results
    }

# ==========================================
# MCP ENDPOINTS
# ==========================================

@app.get("/mcp/servers")
async def list_mcp_servers():
    """Returns all currently connected MCP servers."""

    servers = await manager.mcp_manager.list_servers()

    return {
        "connected_servers": servers,
        "total": len(servers)
    }


@app.get("/mcp/tools")
def list_mcp_tools():
    """Returns all dynamically registered MCP tools."""

    tools = []

    for tool_name in manager.tool_registry.list_tools():
        tool = manager.tool_registry.get_tool(tool_name)

        if tool and tool.get("type") == "mcp":
            tools.append({
                "name": tool_name,
                "server_name": tool.get("server_name"),
                "tool_name": tool.get("tool_name"),
                "description": tool.get("description", ""),
                "input_schema": tool.get("input_schema", {})
            })

    return {
        "tools": tools,
        "total": len(tools)
    }


@app.post("/mcp/tools/{tool_name}")
async def execute_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any]
):
    tool = manager.tool_registry.get_tool(tool_name)

    if tool is None:
        raise HTTPException(
            status_code=404,
            detail=f"MCP tool '{tool_name}' not found."
        )

    if tool.get("type") != "mcp":
        raise HTTPException(
            status_code=400,
            detail=f"'{tool_name}' is not an MCP tool."
        )

    try:
        result = await manager.tool_execution_service.execute(
            tool_name=tool_name,
            arguments=arguments
        )
        return result

    except MCPArgumentValidationError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except MCPToolExecutionError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        ) from error