from app.main import db
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
	__tablename__ = 'admin'
	id = db.Column(db.Integer, primary_key=True, autoincrement = True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(50), unique=True, nullable=False)