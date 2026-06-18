from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from database.mission_db import MissionDB



logger = logging.getLogger(__name__)

router = APIRouter()

mission = MissionDB()

class NewMission(BaseModel):
    title: str = Field(max_length=50)
    description: str
    location: str = Field(max_length=100)
    difficulty: int = Field(ge=1, le=10)
    importance: int = Field(ge=1, le=10)
        

@router.post("", status_code=201)
def create_mission(body: NewMission):
    logger.info("POST /missions called")
    try:
        logger.info(f"Start creating a new mission in SQL")
        new_mission = mission.create_mission(body.model_dump())
        if not new_mission:
            raise HTTPException(status_code=500, 
            detail="An unexpected error occurred while creating a new mission")
        logger.info(f"mission created successfully: id={new_mission["id"]}")
        return new_mission
    except:
        logger.warning(f"""(500) An unexpected error occurred
                       while creating a new mission""")
        raise

@router.get("")
def get_all_missions():
    logger.info("GET /mission called")
    try:
        logger.info(f"Start get all mission from SQL")
        missions = mission.get_all_missions()
        logger.info(f"get all mission from SQL completed successfully.")
        return missions
    except:
        logger.warning(f"(500) An unexpected error occurred \
                       while creating a new mission")
        raise


@router.get("/{id}")
def get_mission_by_id(id: int):
    try:
        logger.info(f"GET /missions/{id} called")
        logger.info(f"Start get mission by id from SQL")
        mission_id = mission.get_mission_by_id(id)
        if mission_id == None:
            logger.error(f"mission not found: {id}")
            raise HTTPException(status_code=404, detail=f"mission not found: {id}")
        logger.info(f"Get mission by id from SQL completed successfully, id={id}.")
        return mission_id
    except HTTPException as e:
        raise
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while get mission by id {id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")

@router.put("/{id}/assign/{agent_id}")
def assign_mission(id: int, agent_id: int):
    try:
        logger.info(f"PUT /missions/{id}/assign/{agent_id} called")
        logger.info(f"Start assign_mission {id} to {agent_id} from SQL")
        assign = mission.assign_mission(id, agent_id)
        if assign:
            logger.info(f"assign_mission completed successfully, \
                        id={id} agent_id={agent_id}. ")
        return {"assign": "success"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while assign_mission{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")
        
        

@router.put("/{id}/start")
def start_mission(id: int):
    try:
        logger.info(f"PUT /{id}/start called")
        logger.info(f"Start update start mission {id} in SQL")
        started = mission.update_mission_status(id, "IN_PROGRESS")
        if started:
            logger.info(f"start mission successfully id={id}.")
            return {"success": f"mission {id} start successfully"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while start_mission{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")

@router.put("/{id}/complete")
def completed_mission(id: int):
    try:
        logger.info(f"PUT /{id}/complete called")
        logger.info(f"Start update complete mission {id} in SQL")
        completed = mission.update_mission_status(id, "COMPLETED")
        if completed:
            logger.info(f"complete mission successfully id={id}.")
            return {"success": f"mission {id} complete successfully"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while completed_mission{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")

@router.put("/{id}/fail")
def failed_mission(id: int):
    try:
        logger.info(f"PUT /{id}/fail called")
        logger.info(f"Start fail mission {id} in SQL")
        fail = mission.update_mission_status(id, "FAILED")
        if fail:
            logger.info(f"fail mission successfully id={id}.")
            return {"success": f"mission {id} fail successfully"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while failed_mission{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")

@router.put("/{id}/cancel")
def canceled_mission(id: int):
    try:
        logger.info(f"PUT /{id}/cancel called")
        logger.info(f"Start cancel mission {id} in SQL")
        cancel = mission.update_mission_status(id, "CANCELLED")
        if cancel:
            logger.info(f"cancel mission successfully id={id}.")
            return {"success": f"mission {id} canceled successfully"}
    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"(500) An unexpected error occurred while cancel_mission{id}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again later.")
