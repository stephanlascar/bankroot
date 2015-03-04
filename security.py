from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, UserMixin


bcrypt = Bcrypt()
login_manager = LoginManager()


class User(UserMixin):

    def __init__(self, _id):
        self.id = _id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)