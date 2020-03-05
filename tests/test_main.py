import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = "test.db"

class MainTests(unittest.TestCase):
    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ########################
    #### helper methods ####
    ########################

    def login(self, name, password):
        return self.app.post('/', data=dict(
        name=name, password=password), follow_redirects=True)

    ###############
    #### tests ####
    ###############

    def test_404_error(self):
        response = self.app.get("/this-route-does-not-exist/")
        self.assertEquals(response.status_code, 404)

    def test_500_error(self):
        bad_user = User(
            name = "Janek1",
            email= "janek@wp.pl",
            password = "janek1"
        )
        db.session.add(bad_user)
        db.session.commit()
        self.assertRaises(ValueError, self.login, "Janek1", "janek1")
        try:
            response = self.login("Janek1", "janek1")
            self.assertEquals(response.status_code, 500)
        except ValueError:
            pass

if __name__ == "__main__":
    unittest.main()
