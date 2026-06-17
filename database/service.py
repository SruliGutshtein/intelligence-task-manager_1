from database.agent_db import AgentDB
from database.mission_db import MissionDB


def count_total_missions(id: int):
    missions = MissionDB().get_all_missions()
    missions_id = [mission for mission in missions if mission["assigned_agent_id"]==id]
    return len(missions_id)

def validation_difficulty_and_importance(difficulty, importance):
    if difficulty < 0 or difficulty > 10:
        raise ValueError("difficulty most be between 0 and 10")
    if importance < 0 or importance > 10:
        raise ValueError("importance most be between 0 and 10")

def risk_level(difficulty, importance) -> str:
    result = difficulty * 2 + importance
    if 0 <= result <= 9:
        return "LOW"
    if 10 <= result <= 17:
        return "MEDIUM"
    if 18 <= result <= 24:
        return "HIGH"
    if result >= 25:
        return "CRITICAL"
    
def count_open_mission_by_id(id: int) :
    missions = MissionDB().get_all_missions()
    open_status = ["ASSIGNED", "IN_PROGRESS"]
    open_missions = [mission for mission in missions
             if mission["assigned_agent_id"]==id
             and mission["status"] in open_status]
    return len(open_missions)

def validate_assign_mission(m_id, a_id):
    """Enforces all mission assignment rules"""
    agent = AgentDB().get_agent_by_id(a_id)
    if agent is None:
        raise KeyError(f"agent {a_id} not found")
    if not agent["is_active"]:
        raise KeyError(f"agent {a_id} is not active")
    mission = MissionDB().get_mission_by_id(m_id)
    if mission["risk_level"] == "CRITICAL" \
        and agent["agent_rank"] != "Commander":
        raise ValueError("A critical mission can only be assigned to a commander")
    if count_open_mission_by_id(a_id) >= 3:
        raise ValueError("An agent cannot have more than 3 open tasks at the same time")
    if mission["status"] != "NEW":
        raise ValueError("Only a task with a NEW status can be assigned")
    