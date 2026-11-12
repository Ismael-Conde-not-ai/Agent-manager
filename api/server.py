from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from agents.agent import AIagent
from core.config_loader import load_agent_config
from core.composition import create_application
from integrations.argument_validator import (
    MCPArgumentValidationError,
    MCPToolExecutionError,
)
from integrations.config_loader import MCPConfigLoader
from core.exceptions import AgentError, PlanningError, ValidationError
from core.logger import logger
application = create_application()
manager = application.manager
orchestrator = application.orchestrator

agent = None

research_agent = application.research_agent
planner_agent = application.planner_agent
executor_agent = application.executor_agent
evaluator_agent = application.evaluator_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Connects configured MCP servers on startup
    and closes all connections on shutdown.
    """

    try:
        config_loader = MCPConfigLoader()

        await manager.mcp_manager.connect_configured_servers(
            config_loader
        )

        yield

    finally:
        await manager.mcp_manager.close_all()


app = FastAPI(lifespan=lifespan)


def _error_status(error: AgentError) -> int:
    if isinstance(error, ValidationError):
        return 422
    if error.category.value == "planning":
        return 422
    if error.category.value in {
        "execution",
        "tool",
        "mcp_communication",
        "evaluation",
        "research",
    }:
        return 502
    return 500


@app.exception_handler(AgentError)
async def handle_agent_error(request: Request, error: AgentError):
    logger.error(
        "[API] path=%s category=%s code=%s message=%s",
        request.url.path,
        error.category.value,
        error.code,
        str(error),
        exc_info=error,
    )
    message = (
        str(error)
        if error.category.value != "internal"
        else "Internal server error."
    )
    return JSONResponse(
        status_code=_error_status(error),
        content={
            "error": {
                "code": error.code,
                "category": error.category.value,
                "message": message,
            }
        },
    )

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
        initial_status=config["initial_status"],
        knowledge_base=application.knowledge_base,
        memory_manager=application.memory_manager,
        tool_registry=application.tool_registry,
        tool_execution_service=application.tool_execution_service,
        planner_agent=application.planner_agent,
        executor_agent=application.executor_agent,
        orchestrator=application.orchestrator,
    )
    
    manager.add_agent(agent)

    return {"message":"Agent created from config"}

@app.post("/agent/step")
async def run_agent_step():

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not created")
    
    await agent.autonomous_step()

    return{
        "energy":agent.energy,
        "status":agent.status,
        "plan_remaining":agent.plan
    }

@app.get("/agent/status")
def agent_status():

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not created")
    
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
        raise HTTPException(
            status_code=404,
            detail="Agent not initialized",
        )
    
    return{
        "agent_name":agent.name,
        "energy": agent.energy,
        "status":agent.status,
        "memory_entries":len(agent.long_term_memory),
        "remaining_plan_steps": len(agent.plan) if agent.plan else 0
    }

@app.get("/system/logs")
def get_logs():
    '''Returns last 20 log entries, if not return error log'''
    try:
        with open("logs/agent.log","r") as file:
            logs = file.readlines()

        return {"logs":logs[-20:]}
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Log file not found",
        ) from None

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
    if plan is None:
        raise PlanningError(
            "Generated plan could not be parsed.",
            code="invalid_plan",
        )

    return{
        "agent": planner_agent.name,
        "goal": goal,
        "plan": (
            [step.model_dump() for step in plan]
            if plan is not None
            else None
        )
    }

@app.post("/workflow/full")
async def full_workflow(goal: str):
    '''Conducts research, creates a plan, and executes it.'''
    if not agent:
        raise HTTPException(status_code=409, detail="No main agent created")
    result = await orchestrator.run(goal, agent)
    if not result.success:
        status_code = 502
        if result.error is not None:
            status_code = _error_status(
                AgentError(
                    result.error.message,
                    code=result.error.code,
                    category=result.error.category,
                )
            )
        return JSONResponse(
            status_code=status_code,
            content=result.to_legacy_dict(),
        )
    return result.to_legacy_dict()

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
        raise HTTPException(status_code=409, detail="No main agent created")
    
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