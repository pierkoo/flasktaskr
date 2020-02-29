# project/db_create.py
# Database creation

from datetime import date

from project import db
from project.models import Task, User
# create the database and the db table
db.create_all()

#insert data
# db.session.add(User("admin", "ad@min.com", "admin", "admin"))

# db.session.add(
#     Task("Finish this tutorial", date(2020, 2, 29), 10, date(2020, 2, 29), 1, 1 ))

# db.session.add(
#     Task("Finish Real Python Course Part 2", date(2020, 3, 15), 10, date(2020, 2, 29), 1, 1))

# commit
db.session.commit()
