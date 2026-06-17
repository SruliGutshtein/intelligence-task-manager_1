def count_total_missions(id: int):
    missions = AgentDB().get_all_missions()
    missions_id = [mission for mission in missions if mission["assigned_agent_id"]==id]
    return len(missions_id)