from main import app as application
from main import db

from app.models.flightinfo import * 
from app.models.user_booking_info import *
from app.models.flight_booking_records import *
from app.models.admin import * 

db.create_all()

if __name__ == '__main__':
	application.run(debug=True, host='0.0.0.0')