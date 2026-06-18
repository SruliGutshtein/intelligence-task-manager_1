from fastapi import FastAPI
import uvicorn
from database.db_connection import DBConnection
from logs import logger_setup
from routes import agent_routes, mission_routes, report_routes


logger_setup.setup_logging()


conn = DBConnection()
conn.create_database()
conn.create_tables()


app = FastAPI()

app.include_router(router=agent_routes.router, prefix="/agents", tags=["agents"])
app.include_router(router=mission_routes.router, prefix="/missions", tags=["missions"])
app.include_router(router=report_routes.router, prefix="/reports", tags=["reports"])



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)