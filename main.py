from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')

from config import *
app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)


#DB object
db = SQLAlchemy(app)


#Migrations
migrate = Migrate(app, db)


#LoginManager
login_manager = LoginManager(app)


#Blueprints
from views.index import index_module
app.register_blueprint(index_module)

from views.flight_information import flight_module
app.register_blueprint(flight_module)

from views.booking_information import booking_module
app.register_blueprint(booking_module)