# project/db_create.py
# Database creation

import sqlite3
from _config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:
    c = connection.cursor()

    c. execute(""" CREATE TABLE tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status INTEGER NOT NULL)"""
              )
    c.execute("""INSERT INTO tasks (name, due_date, priority, status)
                    VALUES ("Finish this tutorial", "02/25/2020", 10, 1)""")
    c.execute("""INSERT INTO tasks (name, due_date, priority, status)
                    VALUES ("Finish REal Python Course 2", "03/15/2020", 10, 1)""")
