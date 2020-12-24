from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_manager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dailyapp.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # function name of the route, like url_for function
login_manager.login_message_category = 'info'  # this is to style the prompt for user to login before viewing /account page (info is a bootstrap class)

# Only import from dailyapp starting here (because they require db or app)
from dailyapp import routes