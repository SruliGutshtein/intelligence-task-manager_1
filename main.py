from database.agent_db import AgentDB
from database.mission_db import MissionDB
from database.db_connection import DBConnection

conn = DBConnection()
conn.create_tables()

agent = AgentDB()
mission = MissionDB()

