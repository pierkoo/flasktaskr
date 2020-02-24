# project/db_migrate.py

from views import db
from _config import DATABASE_PATH

import sqlite3
from datetime import datetime

with sqlite3.connect(DATABASE_PATH) as connection:

    c = connection.cursor()
    # change the name of tasks table
    c.execute("""ALTER TABLE tasks RENAME TO old_tasks""")
    # create a new tasks table with updated schema
    db.create_all()
    # retrieve data from old tasks table
    c.execute("""SELECT name,due_date, priority, status
                 FROM old_tasks ORDER BY task_id ASC""")
    # save all rows as a list of tuples with user+id = 1
    data = [(row[0], row[1], row[2], row[3],
             datetime.now(), 1) for row in c.fetchall()]
    # insert data to tasks table
    c.executemany("""INSERT INTO tasks ( name, due_date, priority, status,
                     posted_date, user_id) VALUES (?, ?, ?, ?, ?, ?)""", data)
    # delete old tasks table
    c.execute("DROP TABLE old_tasks")
