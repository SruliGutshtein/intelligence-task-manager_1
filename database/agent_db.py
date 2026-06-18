from database.db_connection import DBConnection as dbc
from database.mission_db import MissionDB



class AgentDB:
    def create_agent(self, data: dict) -> dict:
        """Accepts a dictionary and creates a new agent
        and returns the agent object"""
        
        sql = """INSERT INTO agents (name, specialty, agent_rank)
            VALUES (%s, %s, %s)"""
        values = (data["name"], data["specialty"], data["agent_rank"])
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, values)
                conn.commit()
                new_id = cursor.lastrowid
        return self.get_agent_by_id(new_id)
        

    def get_all_agents(self) -> list:
        """Returns a list of all agents"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM agents")
                agents = cursor.fetchall()
        return agents
        


    def get_agent_by_id(self, id) -> dict | None:
        """Returns one agent by ID, or None if not exist"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM agents WHERE id = %s", (id,))
                agent = cursor.fetchone()
        return agent

    def update_agent(self, id: int, data: dict) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        set_parts = [f"{key} = %s" for key in data.keys()]
        set_clause = ", ".join(set_parts)
        values = tuple(data.values() + (id,))
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                sql = f"UPDATE agents SET {set_clause} WHERE id = %s"
                cursor.execute(sql, values)
                conn.commit()
                success = cursor.rowcount > 0
        return success

    def deactivate_agent(self, id: int) -> bool:
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "UPDATE agents SET is_active=FALSE WHERE id = %s"
                cursor.execute(sql, (id,))
                conn.commit()
                success = cursor.rowcount > 0
        return success

    def increment_completed(self, id: int) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """SELECT COUNT(*) AS completed
                        FROM missions WHERE assigned_agent_id = %s
                        AND status = 'COMPLETED'"""
                cursor.execute(sql, (id,))
                completed = cursor.fetchone()["completed"]
                updated = self.update_agent(id, {"completed_missions": completed})
                return updated
                
    def increment_failed(self, id) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """SELECT COUNT(*) AS failed
                        FROM missions WHERE assigned_agent_id = %s
                        AND status = 'FAILED'"""
                cursor.execute(sql, (id,))
                failed = cursor.fetchone()["failed"]
                updated = self.update_agent(id, {"failed_missions": failed})
                return updated

    def get_agent_performance(self, id: int) -> dict:
        agent = self.get_agent_by_id(id)
        completed = agent["completed_missions"]
        failed = agent["failed_missions"]
        total = count_total_missions(id)
        total_closed = completed + failed
        ret_val = {
            "completed": completed,
            "failed": failed,
            "total": total,
            "success_rate": int(completed / total_closed * 100 
                                if total_closed != 0 else 0)
        }
        return ret_val
    
    def count_active_agents(self) -> int:
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """SELECT COUNT(*) AS active_agents
                        FROM agents WHERE is_active = TRUE
                    """
                cursor.execute(sql)
                active_agents = cursor.fetchone()["active_agents"]
        return active_agents

def count_total_missions(id: int):
    missions = MissionDB().get_all_missions()
    missions_id = [mission for mission in missions if mission["assigned_agent_id"]==id]
    return len(missions_id)