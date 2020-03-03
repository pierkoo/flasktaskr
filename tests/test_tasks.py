# project/test_tasks.py

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User, Task
import datetime

TEST_DB = "test.db"

class AllTest(unittest.TestCase):

    # helper methods
    def register(self, name, email, password, confirm):
        return self.app.post(
            "register/",
            data=dict(name=name, email=email, password=password,
                confirm=confirm),
            follow_redirects=True
        )

    def login(self, name, password):
        return self.app.post('/', data=dict(
        name=name, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get("logout/", follow_redirects=True)


    def get_in_admin(self):
        new_user = User(
            name="Superadmin",
            email="admin@admin.ad",
            password=bcrypt.generate_password_hash("almighty"),
            role="admin"
        )
        db.session.add(new_user)
        db.session.commit()
        self.login("Superadmin", "almighty")

    def get_in(self):
        self.register("Marek1", "marek@rp.com", "python", "python")
        self.login("Marek1", "python")

    def create_task(self):
        return self.app.post("add/", data=dict(
            name="Test task",
            due_date="10/08/2020",
            priority="1",
            posted_date="09/10/2020",
            status="1"
            ), follow_redirects=True)

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    #each test should start with "test"


    def test_invalid_form_data(self):
    #    self.register("Michael", "Michael@realpython.com", "python", "python")
        response = self.login('alert("alert box!");', "python")
        self.assertIn(b"Invalid username or password.", response.data)

    def test_user_can_add_tasks(self):
        self.get_in()
        self.app.get("tasks/", follow_redirects=True)
        response = self.create_task()
        self.assertIn(b"New entry was successfully added. Thanks.", response.data)

    def test_user_cannot_add_task_when_error(self):
        self.get_in()
        self.app.get("tasks/", follow_redirects=True)
        response = self.app.post("add/", data=dict(
            name="Test task",
            due_date="",
            priority="1",
            posted_date="09/10/2020",
            status="1"
            ), follow_redirects=True)
        self.assertIn(b"This field is required.", response.data)

    def test_can_delete_tasks(self):
        self.get_in()
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b"The task was deleted.", response.data)

    def test_can_complete_tasks(self):
        self.get_in()
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b"Task was marked as complete.", response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.register("Michael", 'mmm@mm.com', "python", "python")
        self.login("Michael", "python")
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.register("Romano", 'rrr@mm.com', "python", "python")
        self.login("Romano", "python")
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(b"Task was marked as complete.", response.data)
        self.assertIn(b"You can only update tasks that belong to you", response.data)
    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.register("Michael", 'mmm@mm.com', "python", "python")
        self.login("Michael", "python")
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.register("Romano", 'rrr@mm.com', "python", "python")
        self.login("Romano", "python")
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(b"The task was deleted.", response.data)
        self.assertIn(b"You can only delete tasks that belong to you", response.data)
    def test_admins_can_complete_tasks_that_are_not_created_by_them(self):
        self.get_in()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.get_in_admin()
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b"Task was marked as complete.", response.data)

    def test_admins_can_delete_tasks_that_are_not_created_by_them(self):
        self.get_in()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.get_in_admin()
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b"The task was deleted.", response.data)


    def test_task_repr(self):
        new_task = Task(
            "test task",
            "22/22/2022",
            "1",
            datetime.datetime.utcnow(),
            "1",
           "1"
        )
        self.assertIn("name test task", repr(new_task))


if __name__ == "__main__":
    unittest.main()

