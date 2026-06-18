from fastapi import APIRouter
import logging
from database.mission_db import MissionDB
from database.agent_db import AgentDB


logger = logging.getLogger(__name__)

router = APIRouter()

agent = AgentDB()
mission = MissionDB()


@router.get("/summary")
def general_report():
    logger.info("POST reports/summary called")
    
    logger.info(f"Start creating a new mission in SQL")
    missions = mission.get_all_missions()
    open_missions = [m for m in missions if m["status"] in ["NEW", "ASSIGNED", "IN_PROGRESS"]]
    failed_missions = [m for m in missions if m["status"] == "FAILED"]
    critical_missions = [m for m in missions if m["risk_level"] == "CRITICAL"]
    ret_val = {
    "active_agents_count": agent.count_active_agents(),
    "total_missions": mission.count_all_missions(),
    "open_missions": mission.count_open_missions(),
    "completed_missions": len(open_missions),
    "failed_missions": len(failed_missions),
    "critical_missions": len(critical_missions)
    }
    return ret_val

@router.get("/missions-by-status")
def missions_by_status_report():
    logger.info("POST reports/missions-by-status called")
    return {"new": mission.count_by_status("NEW"),
     "assign": mission.count_by_status("ASSIGNED"),
     "in_progress": mission.count_by_status("IN_PROGRESS"),
     "completed": mission.count_by_status("COMPLETED"),
     "failed": mission.count_by_status("FAILED"),
     "canceled": mission.count_by_status("CANCELLED")}

@router.get("/top-agent")
def get_top_agent():
    logger.info("POST reports/top-agent called")
    return mission.get_top_agent()