from db_connection import DBConnection as dbc
import service
from agent_db import AgentDB as adb

class MissionDB:
    def create_mission(self, data: dict) -> dict:
        """Accepts a dictionary and creates a new mission
        and returns the mission object"""
        
        sql = """INSERT INTO Intelligence_db (title, description, location,
        difficulty, importance, risk_level)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        service.validation_difficulty_and_importance(
            data["difficulty"], data["importance"])
        risk_level = service.risk_level(data["difficulty"], data["importance"])
        values = (data["title"], data["description"], data["location"],
                  data["difficulty"], data["importance"], risk_level)
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, values)
                conn.commit()
                new_id = cursor.lastrowid
        return self.get_mission_by_id(new_id)
    
    def get_all_missions(self):
        """Returns a list of all missions"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM missions")
                missions = cursor.fetchall()
        return missions
    
    def get_mission_by_id(self, id) -> dict | None:
        """Returns one mission by ID, or None if not exist"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM missions WHERE id = %s", (id,))
                mission = cursor.fetchone()
        return mission
    
    def assign_mission(self, m_id, a_id) -> bool:
        service.validate_assign_mission(m_id, a_id)
        self.update_mission_status(id, "ASSIGNED")
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """UPDATE missions SET assigned_agent_id=%s 
                WHERE id = %s"""
                cursor.execute(sql, (a_id, m_id))
                conn.commit()
                change = cursor.rowcount > 0
        return change
    
    def update_mission_status(self, id, status):
        mission = self.get_mission_by_id(id)
        if mission is None:
            raise KeyError(f"mission {id} not found")
        if status == "failed" or status == "completed":
            if mission["status"] != "IN_PROGRESS":
                raise ValueError("""You cannot change the status
                                 if it is not in IN_PROGRESS""")
        
    def get_open_missions_by_agent(self, id):
        agent = adb().get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        sql = """SELECT * FROM missions WHERE id = %s"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                missions = cursor.fetchall()
        open_status = ["ASSIGNED", "IN_PROGRESS"]
        open_missions = [mission for mission in missions
             if mission["status"] in open_status]
        return open_missions
    
    def count_all_missions(self) -> int:
        missions = self.get_all_missions()
        return len(missions)
    
    def count_by_status(self, status) -> int:
        sql = """SELECT count(*) AS status_count
        FROM missions WHERE status = %s"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, (status,))
                status_count = cursor.fetchall()
        return status_count["status_count"]
    
    def count_open_missions(self) -> int:
        missions = self.get_all_missions()
        open_status = ["ASSIGNED", "IN_PROGRESS"]
        open_missions = [mission for mission in missions
             if mission["status"] in open_status]
        return len(open_missions)
        
    def count_critical_missions(self) -> int:
        criticals = self.count_by_status("CRITICAL")
        return len(criticals)
    
    def get_top_agent(self):
        sql = """SELECT assigned_agent_id, COUNT(*) AS completed
        FROM missions WHERE status = 'COMPLETED'
        GROUP BY assigned_agent_id"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                top_agent = cursor.fetchall()
                if not top_agent:
                    return []
                if len(top_agent) > 1:
                    ids = [id["assigned_agent_id"] for id in top_agent]
                    agents_id = [adb.get_agent_by_id(id) for id in ids]
                    return agents_id
                return top_agent[0]
        