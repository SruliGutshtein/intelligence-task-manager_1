# Intelligence-Task-Manager

## Agent and task management system connected to a MySQL database

<br> <br>


## Folder structure
```
intelligence-task-manager/
├── database/
│   ├── db_connection.py
│   ├── agent_db.py
│   └── mission_db.py
├── README.md
├── requirements.txt
└── .gitignore
```

<br>


## Database structure
```
Intelligence_db
├── agents Table
├── missions Table
```

<br>

## Tables structure

### Agents Table

| field | type | Notes |
| :--- | :--- | :--- |
| `id` | INT, AUTO_INCREMENT, PK | Unique identifier |
| `name` | VARCHAR | Agent name |
| `specialty` | VARCHAR	| Field of specialization |
| `is_active` | BOOLEAN	| DEFAULT  TRUE |
| `completed_missions` | INT | DEFAULT 0 |
| `failed_missions`	| INT | DEFAULT 0 |
| `agent_rank` | ENUM / VARCHAR	| Junior / Senior / Commander only |


<br>

### Agents Table

| field | type | Notes |
| :--- | :--- | :--- |
| `id` | INT, AUTO_INCREMENT, PK | Unique identifier |
| `title` | VARCHAR	| Mission title |
| `description`	| TEXT | Detailed description |
| `location` | VARCHAR | location |
| `difficulty` | INT | 1–10 only |
| `importance` | INT | 1–10 only |
| `status` | VARCHAR | DEFAULT NEW |
| `risk_level` | VARCHAR | Automatically calculated — not coming from the user |
| `assigned_agent_id` | INT	| NULL until association |

<br><br>


## Explanation of DB Classes
<br>

#### DBCOnnection Class 

| method | role |
| :--- | :--- |
| `get_connection()` | Returns an active connection to MySQL |
| `create_database()` | Creates Intelligence_db if it does not exist |
| `create_tables()` | Creates both tables if they do not exist |

<br>

#### AgentDB Class 
Responsible for all SQL operations against the agents table

(Wherever it is not explicitly stated what to return, a success or failure message is returned)

| method | role |
| :--- | :--- |
| `create_agent(data)` | Creates a new agent and returns the agent object |
| `get_all_agents()` | Returns a list of all agents |
| `get_agent_by_id(id)` | Returns one agent by ID, or None |
| `update_agent(id, data)` | UPDATE for the entire row (cannot change id) |
| `deactivate_agent(id)` | Sets agent inactive status |
| `increment_completed(id)` | Updates the number of tasks completed |
| `increment_failed(id)` | Updates the number of failed tasks |
| `get_agent_performance(id)` | Returns a dictionary with these keys completed, failed, total, success_rate |
| `count_active_agents()` | Returns the number of active agents |

<br>

#### MissionDB Class 

| method | role |
| :--- | :--- |
| `create_mission(data)` | Creates a new task and returns the entire object |
| `get_all_missions()` | Returns all tasks |
| `get_mission_by_id(id)` | Returns one task by ID, or None |
| `assign_mission(m_id, a_id)` | Assigning a task to an agent
| `update_mission_status(id, status)` | Used for any status change |
| `get_open_missions_by_agent(id)` | Returns agent ASSIGNED/IN_PROGRESS tasks |
| `count_all_missions()` | Total tasks |
| `count_by_status(status)` | Counting by a certain status
| `count_open_missions()` | Open task counter |
| `count_critical_missions()` | CRITICAL task counter |
| `get_top_agent()` | The agent with the highest completed_missions |

<br>

## System rules

* `1` rank must be Junior / Senior / Commander — any other value throws an error.
* `2` difficulty and importance must be between 1 and 10 — otherwise an error.
* `3` risk_level is calculated automatically when creating a task — the user does not submit it.
* `4` An agent with is_active=False cannot accept tasks.
* `5` An agent cannot have more than 3 open tasks (ASSIGNED / IN_PROGRESS) at the same time.
* `6` If risk_level=CRITICAL — only an agent with the Commander rank can accept the task.
* `7` Only a task with the status NEW can be assigned. After assignment: status=ASSIGNED.
* `8` Only a task with the status ASSIGNED can be started. After: status=IN_PROGRESS.
* `9` Only a task with the status IN_PROGRESS can be finished and changed to failed or completed.
* `10` Only a task with the status NEW or ASSIGNED can be canceled — otherwise an error.

<br><br>

## Running instructions

### Running MySQL with Docker
```
docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 \
  -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0
```

## Running Python 

* create a virtual environment
```
# on windows 
python3 -m venv .venv
./.venv/Scripts/activate
```
```
# on mac
python3 -m venv .venv
source .venv/bin/activate
```

* install requirements
```
pip install -r requirements.txt
```

* run `python main.py` to activate the project 
```
cd <where the project is>/intelligence-task-manager
python main.py
```