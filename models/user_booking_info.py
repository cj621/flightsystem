from app.main import db
from datetime import datetime

class CustomerBooking(db.Model):
	__tablename__ = 'customer_booking'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	flight_number = db.Column(db.String(100), primary_key = True)
	contact_email = db.Column(db.String(100), nullable = False)
	flight_date = db.Column(db.Date, primary_key = True)
	departure_time = db.Column(db.Time(timezone = False), nullable = False) #departure from the source
	seats_booked = db.Column(db.Integer, default = 0, nullable = False)
	booking_id = db.Column(db.Integer, default = -1, primary_key = True)
	booking_status = db.Column(db.String(100), default = "pending")
	ticket_booked_on = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)
	ticket_booking_updated_on = db.Column(db.DateTime(timezone=False), default=datetime.now(), nullable=False)