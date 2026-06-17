from db_connection import DBConnection as dbc
from mission_db import MissionDB as mdb
import service


class AgentDB:
    def create_agent(self, data: dict) -> dict:
        """Accepts a dictionary and creates a new agent
        and returns the agent object"""
        
        sql = """INSERT INTO Intelligence_db (name, specialty, is_active, agent_rank)
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
                cursor.execute("SELECT * FROM Intelligence_db")
                agents = cursor.fetchall()
        return agents
        


    def get_agent_by_id(self, id) -> dict | None:
        """Returns one agent by ID, or None if not exist"""
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Intelligence_db WHERE id = %s", (id,))
                agent = cursor.fetchone()
        return agent

    def update_agent(self, id: int, data: dict) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        set_parts = [f"{key} = %s" for key in data.keys()]
        if "id" in set_parts:
            raise ValueError("Cannot change ID")
        set_clause = ", ".join(set_parts)
        values = tuple(data.values(), id)
        with dbc().get_connection() as conn:
            with conn.cursor() as cursor:
                sql = f"UPDATE agents SET {set_clause} WHERE id = %s"
                cursor.execute(sql, values)
                conn.commit()
                success = cursor.rowcount > 0
        return success

    def deactivate_agent(self, id: int) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        updated = self.update_member(id, {"is_active": False})
        return updated

    def increment_completed(self, id: int) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """SELECT COUNT(*) AS completed
                        FROM missions WHERE assigned_agent_id = %s
                        AND WHERE status = COMPLETED"""
                cursor.execute(sql, (id,))
                completed = cursor.fetchone()["completed"]
                updated = self.update_member(id, {"completed_missions": completed})
                return updated
                
    def increment_failed(self, id) -> bool:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        with dbc().get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """SELECT COUNT(*) AS failed
                        FROM missions WHERE assigned_agent_id = %s
                        AND WHERE status = FAILED"""
                cursor.execute(sql, (id,))
                failed = cursor.fetchone()["failed"]
                updated = self.update_member(id, {"failed_missions": failed})
                return updated

    def get_agent_performance(self, id: int) -> dict:
        agent = self.get_agent_by_id(id)
        if agent is None:
            raise KeyError(f"agent {id} not found")
        completed = mdb().count_by_status("COMPLETED")
        failed = mdb().count_by_status("FAILED")
        total = service.count_total_missions(id),
        ret_val = {
            "completed": completed,
            "failed": failed,
            "total": total,
            "success_rate": int(completed / total * 100)
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
