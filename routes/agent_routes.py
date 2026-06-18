from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import logging
from database.agent_db import AgentDB


logger = logging.getLogger(__name__)

router = APIRouter()

agent = AgentDB()

class NewAgent(BaseModel):
    name: str=Field(max_length=50)
    specialty: str=Field(max_length=50) 
    agent_rank: Literal["Junior", "Senior", "Commander"]

class UpdateAgent(BaseModel):
    name: str | None =Field(max_length=50, default=None)
    specialty: str | None =Field(max_length=50, default=None)
    agent_rank: None |Literal["Junior", "Senior", "Commander"] = None

@router.post("", status_code=201)
def create_agent(body: NewAgent):
    logger.info("POST /agents called")
    try:
        logger.info(f"Start creating a new agent in SQL")
        new_agent = agent.create_agent(body.model_dump())
        if not new_agent:
            raise HTTPException(status_code=500, 
            detail="An unexpected error occurred while creating a new agent")
        logger.info(f"Agent created successfully: id={new_agent["id"]}")
        return new_agent
    except:
        logger.warning(f"""(500) An unexpected error occurred
                       while creating a new agent""")
        raise

@router.get("")
def get_all_agents() -> list:
    logger.info("GET /agents called")
    try:
        logger.info(f"Start get all agents from SQL")
        agents = agent.get_all_agents()
        logger.info(f"get all agents from SQL completed successfully.")
        return agents
    except:
        logger.warning(f"(500) An unexpected error occurred \
                       while creating a new agent")
        raise

@router.get("/{id}")
def get_agent_by_id(id: int):
    try:
        logger.info(f"GET /agents/{id} called")
        logger.info(f"Start get agent by id from SQL")
        agent_id = agent.get_agent_by_id(id)
        if agent_id == None:
            logger.error(f"Agent not found: {id}")
            raise HTTPException(status_code=404, detail=f"Agent not found: {id}")
        logger.info(f"Get agent by id from SQL completed successfully, id={id}.")
        return agent_id
    except HTTPException as e:
        raise
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while get Agent by id {id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")
        
@router.put("/{id}")
def update_agent_by_id(id: int, body: UpdateAgent):
    try:
        logger.info("PUT /agents/{id} called")
        agent_id = agent.get_agent_by_id(id)
        if agent_id is None:
            raise KeyError(f"Agent not found: {id}")
        data = body.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=400,
                detail=("The update body cannot be empty",))
        logger.info(f"Start updating agent {id} in SQL")
        updated = agent.update_agent(id, data)
        if updated:
            logger.info(f"update agent {id} successfully")
            return {"updated": f"agent {id}"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while update Agent by id {id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")


@router.put("/{id}/deactivate")
def deactivate_agent(id: int):
    try:
        logger.info("PUT /agents/{id}/deactivate called")
        agent_id = agent.get_agent_by_id(id)
        if agent_id is None:
            raise KeyError(f"Agent not found: {id}")
        if not agent_id["is_active"]:
            logger.error(f"Agent is already deactivate: {id}")
            raise ValueError(f"Agent is already deactivate: {id}")
        logger.info(f"Start deactivate agent {id} in SQL")
        deactivate = agent.deactivate_agent(id)
        if deactivate:
            logger.info(f"deactivate agent {id} successfully")
            return {"deactivate": f"agent {id}"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while deactivate Agent{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")


@router.get("/{id}/performance")
def get_agent_performance(id: int):
    try:
        logger.info("PUT /agents/{id}/performance called")
        agent_id = agent.get_agent_by_id(id)
        if agent_id is None:
            raise KeyError(f"Agent not found: {id}")
        performance = agent.get_agent_performance(id)
        return performance
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while get_agent_performance, id={id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")
