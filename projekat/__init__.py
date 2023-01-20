from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager

import os
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Zare/Desktop/neki novi folder/DRS-Projekat/instance/projekat.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "prijava"
login_manager.login_message = "Prijavite se da biste videli ovu stranicu."
login_manager.login_message_category = "info"

from projekat import routes
