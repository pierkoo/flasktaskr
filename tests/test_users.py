# project/test.py

import os
import unittest

from project import app, db
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

    def get_in(self, name):
        self.register(name, "marek@rp.com", "python", "python")
        self.login(name, "python")

    def get_in_admin(self):
        new_user = User(
            name="Superadmin",
            email="admin@admin.ad",
            password="almighty",
            role="admin"
        )
        db.session.add(new_user)
        db.session.commit()
        self.login("Superadmin", "almighty")

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

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_user_can_register(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register("Michael", "Michael@realpython.com", "python", "python")
        self.assertIn(b"Thanks for registering. Please login.", response.data)

    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register("Michael", "Michael@realpython.com", "python", "python")
        self.app.get('register/', follow_redirects=True)
        response = self.register("Michael", "Michael@realpython.com", "python", "python")
        self.assertIn(b"That username and/or email already exists", response.data)

    def test_user_can_login(self):
        self.register("Michael", "Michael@realpython.com", "python", "python")
        response = self.login("Michael", "python")
        self.assertIn(b"Welcome!", response.data)

    def test_only_logged_in_users_can_logout(self):
        self.register("Marek1", "marek@rp.com", "python", "python")
        self.login("Marek1", "python")
        response = self.logout()
        self.assertIn(b"Goodbye!", response.data)
        response = self.logout()
        self.assertNotIn(b"Goodbye!", response.data)

    def test_only_logged_user_can_acces_task_page(self):
        response = self.app.get("/tasks", follow_redirects=True)
        self.assertIn(b"You need to login first.", response.data)
        self.register("Marek1", "marek@rp.com", "python", "python")
        self.login("Marek1", "python")
        response = self.app.get("/tasks", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add a new task:", response.data)

    def test_user_repr(self):
        new_user = User(
                "pppppp",
                "ppp@ppp.pp",
                "ppplolololo"
            )
        self.assertIn("<User pppppp>", repr(new_user))

    def test_task_template_displays_logged_in_user(self):
        self.get_in("Marek1")
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertIn(b"Marek1", response.data)

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.get_in("Marek1")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()

        self.get_in("Marek2")
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertNotIn(b"complete/1/", response.data)
        self.assertNotIn(b"delete/1/", response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.get_in("Marek1")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()

        self.get_in("Marek1")
        self.create_task()
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertIn(b"complete/1/", response.data)
        self.assertIn(b"delete/1/", response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.get_in("Marek1")
        self.app.get("tasks/", follow_redirects=True)
        self.create_task()
        self.logout()

        self.get_in_admin()
        self.create_task()
        response = self.app.get("tasks/", follow_redirects=True)
        self.assertIn(b"complete/1/", response.data)
        self.assertIn(b"delete/1/", response.data)
        self.assertIn(b"complete/2/", response.data)
        self.assertIn(b"delete/2/", response.data)


if __name__ == "__main__":
    unittest.main()

