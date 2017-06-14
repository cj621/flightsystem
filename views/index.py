from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app.main import login_manager

index_module = Blueprint('index', __name__)

from app.models.admin import * 


login_manager.login_view = '/' #this works with @login_required decorator
login_manager.login_message = 'You need to log in with correct credentials!'


## mapping the python flask object with the object in the actual model
@login_manager.user_loader
def load_user(user_id):
	uid = Admin.query.get(user_id)
	return uid


@index_module.route('/')
def index():
	return render_template('index.html')



@index_module.route('/login', methods = ['POST'])
def admin_login():
	username = request.form['username']
	password = request.form['password']

	admin = Admin.query.filter_by(username = username).first()

	if not admin:
		flash('User Not Found! Please contact the Airlines\' Support Center')
		return redirect(url_for('index.index'))
	elif admin.password != password:
		flash('Invalid Credentials!')
		return redirect(url_for('index.index'))
	else:
		login_user(admin)
		return redirect(url_for('flight_information.flights', admin = current_user.username))



@index_module.route('/logout')
@login_required
def admin_logout():
	logout_user()
	flash('Successfully Logged Out!')
	return redirect(url_for('index.index'))