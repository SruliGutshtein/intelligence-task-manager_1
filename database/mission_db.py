from database.db_connection import DBConnection as dbc
import database.agent_db

class MissionDB:
    def create_mission(self, data: dict) -> dict:
        """Accepts a dictionary and creates a new mission
        and returns the mission object"""
        
        sql = """INSERT INTO missions (title, description, location,
        difficulty, importance, risk_level)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        risk_level = calculate_risk_level(data["difficulty"], data["importance"])
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
        validate_assign_mission(m_id, a_id)
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """UPDATE missions SET assigned_agent_id=%s, status="ASSIGNED"
                WHERE id = %s"""
                cursor.execute(sql, (a_id, m_id))
                conn.commit()
                change = cursor.rowcount > 0
        return change
    
    def update_mission_status(self, id, status):
        mission = self.get_mission_by_id(id)
        if mission is None:
            raise KeyError(f"mission {id} not found")
        if status == "FAILED" or status == "COMPLETED":
            if mission["status"] != "IN_PROGRESS":
                raise ValueError("You cannot change the status \
                                 if it is not in IN_PROGRESS")
        if status == "IN_PROGRESS" and mission["status"] != "ASSIGNED":
            raise ValueError("You cannot start a mission if it is not 'ASSIGNED'")
        sql = """UPDATE missions SET status=%s WHERE assigned_agent_id = %s"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, (status, id))
                conn.commit()
                change = cursor.rowcount > 0
        return change
        
        
    def get_open_missions_by_agent(self, id):
        agent = database.agent_db().get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        sql = """SELECT * FROM missions WHERE assigned_agent_id = %s"""
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
                status_count = cursor.fetchone()
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
        sql = """SELECT * FROM agents
        ORDER BY completed_missions DESC LIMIT 1"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                top_agent = cursor.fetchone()
                if not top_agent:
                    return []
        return top_agent

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
    
def validate_assign_mission(m_id, a_id):
    """Enforces all mission assignment rules"""
    mission = MissionDB().get_mission_by_id(m_id)
    if mission is None:
        raise KeyError("Mission not found")
    agent = database.agent_db.AgentDB().get_agent_by_id(a_id)
    if agent is None:
        raise KeyError("Agent not found")
    if mission["status"] != "NEW":
        raise ValueError("Mission not available")
    if not agent["is_active"]:
        raise ValueError("Agent is not active")
    if count_open_mission_by_id(a_id) >= 3:
        raise ValueError("Agent has reached maximum missions")
    if mission["risk_level"] == "CRITICAL" \
        and agent["agent_rank"] != "Commander":
        raise ValueError("Only Commander can handle critical missions")
    
def calculate_risk_level(difficulty, importance) -> str:
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