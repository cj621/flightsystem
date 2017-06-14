from flask import Blueprint, request, url_for, render_template, redirect, flash
from datetime import datetime
from random import randint

booking_module = Blueprint('booking_information', __name__)

from app.models.user_booking_info import *
from app.models.flightinfo import *
from app.models.flight_booking_records import * 


@booking_module.route('/flight/<flight_no>/availability')
def flight_availability(flight_no):
	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()

	if not flight_detail:
		flash('There is no flight with Flight Number: ' + str(flight_no))
		return redirect(url_for('flight_information.flights'))

	available_seats = flight_detail.total_seats - flight_detail.booked_seats
	if available_seats > 0:
		return render_template('flight_detail.html', available_seats = available_seats, flight_detail = flight_detail)
	else:
		flash('No seats available!!')
		return render_template('flight_detail.html')


@booking_module.route('/flight/<flight_no>/book')
def book_ticket(flight_no):
	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()
	if not flight_detail:
		flash('There is no such flight ('+ str(flight_no) +') in the system!')
		return redirect(url_for('flight_information.flights'))
	available_seats = flight_detail.total_seats - flight_detail.booked_seats	
	return render_template('book_ticket.html', flight_no = flight_no, available_seats = available_seats)


@booking_module.route('/confirm_booking/<flight_no>', methods = ['POST'])
def confirm_booking(flight_no):

	contact_email = request.form['email']
	required_seats = int(request.form['required_seats'])

	# For checking if the booking already exists for this user.
	booking_existence = CustomerBooking.query.filter_by(flight_number = flight_no, contact_email = contact_email).first()

	# For getting flight details
	flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()

	available_seats = flight_detail.total_seats - flight_detail.booked_seats

	if available_seats < required_seats:
		flash('Seats required by you are greater than the available seats!')
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))
	elif (booking_existence):
		flash('The booking already exists for this contact and flight number! Please check the booking details!')
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))
	else:

		flight_date = flight_detail.flight_date
		departure_time = flight_detail.departure_time
		booking_id = randint(67890, 99999)
		booking_status = "confirmed"
		booking_date = datetime.now()
		booking_update = booking_date

		new_customer_booking = CustomerBooking(flight_number = flight_no,
											contact_email = contact_email,
											flight_date = flight_date,
											departure_time = departure_time,
											seats_booked = required_seats,
											booking_id = booking_id,
											booking_status = booking_status,
											ticket_booked_on = booking_date,
											ticket_booking_updated_on = booking_update)

		db.session.add(new_customer_booking)

		try:
			db.session.commit()
		except Exception, e:
			flash('There was an error in booking the flight. Please contact the site administrator')
		else:
			flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()
			flight_detail.booked_seats += required_seats
			db.session.commit()

			#Checking if Booking records for this flight is available or not.
			flight_booking_record = FlightBookingRecords.query.filter_by(flight_number = flight_no).first()

			if not flight_booking_record:
				# Adding the booking record for flight booking
				booking_record = FlightBookingRecords(flight_number = flight_no,
													flight_date = flight_date,
													departure_time = departure_time,
													total_seats = flight_detail.total_seats,
													seats_booked = flight_detail.booked_seats,
													created_on = booking_date,
													updated_on = booking_update)
				db.session.add(booking_record)
				db.session.commit()
			else:
				flight_booking_record.seats_booked += required_seats
				flight_booking_record.updated_on = datetime.now()
				db.session.commit()

			flash('Booking Confirmed! ' + 'Booking ID is: ' + str(booking_id) + '. Please keep it for future reference.')


		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))


@booking_module.route('/flight/<flight_no>/book/<booking_id>', methods = ['GET', 'POST'])
def get_booking_information(flight_no, booking_id):

	if request.method == 'POST':
		booking_id = request.form['booking_id']

	booking_details = CustomerBooking.query.filter_by(flight_number = flight_no, booking_id = booking_id).first()
	if not booking_details:
		flash('The booking for Flight No. '+ str(flight_no) +' and Booking ID '+ str(booking_id) +' does not exist! OR the flight had been cancelled. Please check if ' + str(flight_no) + ' exists!')
		return render_template('booking_details.html', flight_no = flight_no)
	else:
		return render_template('booking_details.html', booking_details = booking_details)


@booking_module.route('/delete_booking/<flight_no>/<booking_id>', methods = ['GET' ,'DELETE'])
def delete_ticket(flight_no, booking_id):
	cust_booking_details = CustomerBooking.query.filter_by(flight_number = flight_no, booking_id = booking_id).first()
	if not cust_booking_details:
		flash('There is no booking for this flight no. ' + str(flight_no) + ' and booking ID ' + str(booking_id))
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))

	db.session.delete(cust_booking_details)

	try:
		db.session.commit()
	except Exception, e:
		flash('There was an error deleting the record. Please try again!')
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))
	else:
		## Update the booked_seats in flight information
		flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()
		if not flight_detail:
			flash('There is no flight with Flight Number : ' + str(flight_no))
			return redirect(url_for('flight_information.flights'))
		flight_detail.booked_seats -= cust_booking_details.seats_booked

		##Update the seats_booked in Flight Booking Records
		db.session.query(FlightBookingRecords).filter_by(flight_number = 
						flight_no).update({FlightBookingRecords.seats_booked: (FlightBookingRecords.seats_booked - cust_booking_details.seats_booked)})

		## Commit the changes to the DB
		db.session.commit()
		

		flash('Booking Details Deleted for booking ID ' + str(booking_id))
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))
	
	return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))


@booking_module.route('/update_booking/<flight_no>/<booking_id>', methods = ['POST'])
def update_ticket(flight_no, booking_id):
	cust_booking_details = CustomerBooking.query.filter_by(flight_number = flight_no, booking_id = booking_id).first()
	
	if not cust_booking_details:
		flash('There is no booking for this flight no. ' + str(flight_no) + ' and booking ID ' + str(booking_id))
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))
	flash('Update the booking information for booking ID: ' + str(booking_id))
	return render_template('update_ticket.html', cust_booking_details = cust_booking_details)


@booking_module.route('/update_processing/<flight_no>/<booking_id>', methods = ['POST'])
def update_processing(flight_no, booking_id):

	updated_email = request.form['updated_email']
	released_seats = int(request.form['released_seats'])

	cust_booking_details = CustomerBooking.query.filter_by(flight_number = flight_no, booking_id = booking_id).first()
	
	if not cust_booking_details:
		flash('There is no booking for this flight no. ' + str(flight_no) + ' and booking ID ' + str(booking_id))
		return redirect(url_for('booking_information.book_ticket', flight_no = flight_no))

	if released_seats > cust_booking_details.seats_booked:
		flash('You are trying to release more seats than you have booked. Please try again with a valid number!')
		return render_template('update_ticket.html', cust_booking_details = cust_booking_details)

	if released_seats == cust_booking_details.seats_booked:
		flash('You released all the booked seats. ')
		return redirect(url_for('booking_information.delete_ticket', flight_no = flight_no, booking_id = booking_id))

	## Updating booked seats and contact email in the customer booking information
	cust_booking_details.seats_booked -= released_seats
	cust_booking_details.contact_email = updated_email
	cust_booking_details.ticket_booking_updated_on = datetime.now()


	try:
		db.session.commit()
	except Exception, e:
		flash('There was an error updating the booking information. Please try again later!')
		return render_template('update_ticket.html', cust_booking_details = cust_booking_details)
	else:

		## Updating the booked seats in Flight Information
		flight_detail = FlightDetails.query.filter_by(flight_number = flight_no).first()
		if not flight_detail:
			flash('This flight with flight number: ' + str(flight_no) + ' does not exist. Please check your booking status for more information.')
			return redirect(url_for('flight_information.flights'))
		flight_detail.booked_seats -= released_seats	

		# updating the booked seats in Flight Booking Records
		db.session.query(FlightBookingRecords).filter_by(flight_number = 
						flight_no).update({FlightBookingRecords.seats_booked: (FlightBookingRecords.seats_booked - released_seats)})

		## Commit the changes to the DB
		db.session.commit()


		## Sending the response to the front end	
		flash(str(released_seats) + ' seats released. ' 'Updated the booking information')
		return redirect(url_for('booking_information.get_booking_information', flight_no = flight_no, booking_id = booking_id))
