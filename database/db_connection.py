import mysql.connector


class DBConnection:
    def get_connection(self):
        return mysql.connector.connect(
            host = "localhost",
            port = 3306,
            user="root",
            password="1234",
            database="Intelligence_db"
        )
        
    def create_database(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS Intelligence_db")
                conn.commit()
                

    def create_tables(self):
        agents_table = """
        CREATE TABLE IF NOT EXISTS agents(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            specialty VARCHAR(50) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            completed_missions INT DEFAULT 0,
            failed_missions INT DEFAULT 0,
            agent_rank ENUM("Junior", "Senior", "Commander")
        )
        """
        missions_table = """
        CREATE TABLE IF NOT EXISTS missions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            location VARCHAR(100) NOT NULL,
            difficulty INT,
            importance INT,
            status VARCHAR(12) DEFAULT "NEW",
            risk_level VARCHAR(9) NOT NULL,
            assigned_agent_id INT DEFAULT NULL
        )
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(agents_table)
                cursor.execute(missions_table)
                conn.commit()
                
