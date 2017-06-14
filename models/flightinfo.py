from app.main import db
from datetime import datetime

class FlightDetails(db.Model):
	__tablename__ = 'flight_details'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	flight_number = db.Column(db.String(100), primary_key = True)
	source = db.Column(db.String(200), nullable = False)
	destination = db.Column(db.String(200), nullable = False)
	flight_date = db.Column(db.Date, primary_key = True)
	departure_time = db.Column(db.Time(timezone = False), nullable = False) #departure from the source
	destination_arrival_time = db.Column(db.Time(timezone = False), nullable = False) #arrival at the destination
	total_seats = db.Column(db.Integer, nullable = False)
	booked_seats = db.Column(db.Integer, default = 0)
	created_at = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)
	updated_at = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)