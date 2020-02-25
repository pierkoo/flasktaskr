# project/test.py

import os
import unittest

from views import app, db
from _config import basedir
from models import User

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

    def test_user_setup(self):
        new_user = User("michael", "michael@mherman.org", "michaelherman")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "michael"

    def test_form_is_present(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please login to access your task list", response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_user_can_register(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register("Michael", "Michael@realpython.com", "python", "python")
        self.assertIn(b"Thanks for registering. Please login.", response.data)

    def test_user_can_login(self):
        self.register("Michael", "Michael@realpython.com", "python", "python")
        response = self.login("Michael", "python")
        self.assertIn(b"Welcome!", response.data)

    def test_invalid_form_data(self):
        self.register("Michael", "Michael@realpython.com", "python", "python")
        response = self.login('alert("alert box!");', "python")
        self.assertIn(b"Invalid username or password.", response.data)

    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register("Michael", "Michael@realpython.com", "python", "python")
        self.app.get('register/', follow_redirects=True)
        response = self.register("Michael", "Michael@realpython.com", "python", "python")
        self.assertIn(b"That username and/or email already exists", response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get("register/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please register to access the task list.", response.data)

    def test_logged_in_users_can_logout(self):
        self.register("Marek1", "marek@rp.com", "python", "python")
        self.login("Marek1", "python")
        response = self.logout()
        self.assertIn(b"Goodbye!", response.data)

    def test_not_logged_in_users_cannot_logout(self):
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
        self.create_user("Michael", 'mmm@mm.com', "python", "python")
        self.log_in("Michael", "python")
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()

        self.create_user("Romano", 'mmm@mm.com', "python", "python")
        self.log_in("Romano", "python")
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(b"Task was marked as complete.", response.data)



if __name__ == "__main__":
    unittest.main()

