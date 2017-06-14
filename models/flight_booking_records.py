from app.main import db
from datetime import datetime

class FlightBookingRecords(db.Model):
	__tablename__ = 'flight_booking_records'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	flight_number = db.Column(db.String(100), primary_key = True)
	flight_date = db.Column(db.Date, primary_key = True)
	departure_time = db.Column(db.Time(timezone = False), nullable = False) #departure from the source
	total_seats = db.Column(db.Integer, nullable = False)
	seats_booked = db.Column(db.Integer, default = 0)
	created_on = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)
	updated_on = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)