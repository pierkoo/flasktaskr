# project/db_create.py
# Database creation

from views import db
from models import Task
from datetime import date
# create the database and the db table
db.create_all()

#insert data
# db.session.add(Task("Finish this tutorial", date(2020, 2, 29), 10, 1))
# db.session.add(Task("Finish Real Python Course Part 2", date(2020, 3, 15), 10, 1))

# commit
db.session.commit()
