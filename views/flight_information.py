from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import login_required, current_user
from datetime import datetime

flight_module = Blueprint('flight_information', __name__)

from app.models.flightinfo import * 
from app.models.user_booking_info import *
from app.models.flight_booking_records import *


@flight_module.route('/flights/<admin>')
@flight_module.route('/flights')
def flights(admin = None):

	flights = FlightDetails.query.all()

	if admin == None:
		return render_template('flights.html', flights = flights)
	else:
		return render_template('flights.html', current_user = current_user, flights = flights)


@flight_module.route('/newFlight', methods = ['POST'])
@login_required
def Add_new_flight():

	flight_number = request.form['flight_number']
	source = request.form['source']
	destination = request.form['destination']
	flight_date = request.form['flight_date']
	departure = request.form['departure']
	arrival = request.form['arrival']
	total_seats = request.form['total_seats']
	created_at = datetime.now()
	updated_at = created_at

	new_flight = FlightDetails(flight_number = flight_number, source = source, destination = destination, flight_date = flight_date, 
								departure_time = departure, destination_arrival_time = arrival, 
								total_seats = total_seats, booked_seats = 0, created_at = created_at, updated_at = updated_at)

	db.session.add(new_flight)

	try:
		db.session.commit()
	except Exception, e:
		flash('There was an error in adding a flight. Please contact the site administrator')
	else:
		flash('New Flight Added Successfully')


	return redirect(url_for('flight_information.flights'))


@flight_module.route('/flight/<flight_no>')
def flight_data(flight_no):
	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()

	return render_template('flight_detail.html', current_user = current_user, flight_detail = flight_detail)


@flight_module.route('/delete_flight/<flight_no>', methods = ['GET' ,'DELETE'])
def delete_flight(flight_no):
	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()
	if not flight_detail:
		flash('There is no flight with flight no.' + str(flight_no))
		return redirect(url_for('flight_information.flights'))

	db.session.delete(flight_detail)

	try:
		db.session.commit()
	except Exception, e:
		flash('There was an error deleting the flight record. Please try again!')
		return redirect(url_for('flight_information.flights'))
	else:
		db.session.query(CustomerBooking).filter_by(flight_number = flight_no).delete()
		db.session.query(FlightBookingRecords).filter_by(flight_number = flight_no).delete()
		db.session.commit()
		flash('Flight Details Deleted for Flight Number:  ' + str(flight_no) + '. All bookings deleted!!')
		return redirect(url_for('flight_information.flights'))
	
	return redirect(url_for('flight_information.flights'))



@flight_module.route('/update_flight/<flight_no>', methods = ['POST'])
def update_flight(flight_no):
	
	updated_flight_date = request.form['updated_flight_date']
	updated_departure = request.form['updated_departure']
	updated_arrival = request.form['updated_arrival']
	updated_total_seats = int(request.form['updated_total_seats'])

	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()

	if not flight_detail:
		flash('Flight Does not Exist!')
		return redirect(url_for('flight_information.flights'))

	if updated_total_seats < flight_detail.booked_seats:
		flash('Total Seats Cannot be changed to less than already booked!!')
		return redirect(url_for('flight_information.flight_data', flight_no = flight_no))

	flight_detail.flight_date = updated_flight_date
	flight_detail.departure_time = updated_departure
	flight_detail.destination_arrival_time = updated_arrival
	flight_detail.total_seats = updated_total_seats
	flight_detail.updated_at = datetime.now()

	try:
		db.session.commit()
	except Exception, e:
		flash('There was an error updating the flight information. Please try again later!')
		return redirect(url_for('flight_information.flight_data', flight_no = flight_no))
	else:
		## Updating the Customer Booking information based on Modified Flight Details
		db.session.query(CustomerBooking).filter_by(flight_number = flight_no).update({CustomerBooking.flight_date:flight_detail.flight_date,
																						CustomerBooking.departure_time:flight_detail.departure_time })
		
		## Updating the Flight Booking records based on Modified Flight Details
		db.session.query(FlightBookingRecords).filter_by(flight_number = flight_no).update({FlightBookingRecords.total_seats: flight_detail.total_seats,
																							FlightBookingRecords.flight_date: flight_detail.flight_date,
																							FlightBookingRecords.departure_time: flight_detail.departure_time,
																							FlightBookingRecords.updated_on: datetime.now() })
		## Commit changes to the DB
		db.session.commit()

		flash('Updated the flight information for Flight No. ' + str(flight_no))
		return redirect(url_for('flight_information.flight_data', flight_no = flight_no))

	return redirect(url_for('flight_information.flight_data', flight_no = flight_no))


@flight_module.route('/<flight_no>/booking_records')
@login_required
def booking_records(flight_no):
	flight_booking_records = FlightBookingRecords.query.filter_by(flight_number = flight_no)
	return render_template('flight_booking_records.html', current_user = current_user, flight_booking_records = flight_booking_records)