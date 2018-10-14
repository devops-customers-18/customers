# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pet Shop Demo

This is an example of a pet shop service written with Python Flask
It demonstraits how a RESTful service should be implemented.

Paths
-----
GET  /pets - Retrieves a list of pets from the database
GET  /pets{id} - Retrirves a Pet with a specific id
POST /pets - Creates a Pet in the datbase from the posted database
PUT  /pets/{id} - Updates a Pet in the database fom the posted database
DELETE /pets{id} - Removes a Pet from the database that matches the id
"""

import os
import sys
import logging
from database import db_connect
from flask import Response, jsonify, request, json, url_for, make_response
from flask import render_template
from . import app
from models import Customer, DataValidationError
#from urlparse3 import urlparse3

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Postgres connection.
connection = db_connect()

# cursor.execute(query)
# one = cursor.fetch_one()
# all = cursor.fetch_all()
# cursor.commit()

######################################################################
# Error Handlers
######################################################################


@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)


@app.errorhandler(400)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    return jsonify(status=400, error='Bad Request', message=error.message), 400


@app.errorhandler(404)
def not_found(error):
    """ Handles Pets that cannot be found """
    return jsonify(status=404, error='Not Found', message=error.message), 404


@app.errorhandler(405)
def method_not_supported(error):
    """ Handles bad method calls """
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported.'
                   ' Check your HTTP method and try again.'), 405


@app.errorhandler(500)
def internal_server_error(error):
    """ Handles catostrophic errors """
    return jsonify(status=500, error='Internal Server Error', message=error.message), 500

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Customer Demo REST API Service',
                   version='1.0',
                   url=url_for('list_customer', _external=True)), HTTP_200_OK
# Customers starts here.


######################################################################
# ADD A NEW CUSTOMER
######################################################################
@app.route('/customers', methods=['POST'])
def create_pets():
    """Create a customer in the database."""
    app.logger.info('Creating a new customer')
    customer_info = request.get_json()
    print customer_info
    customer = Customer()
    customer.deserialize(customer_info)
    customer.save()
    message = customer.serialize()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_customer', id=customer.id, _external=True)
    return response

######################################################################
# LIST ALL CUSTOMER
######################################################################
@app.route('/customers', methods=['GET'])
def list_customer():
    """ Retrieves a list of pets from the database """
    app.logger.info('Listing pets')
    results = []
    category = request.args.get('category')
    if category:
        results = Customer.find_by_category(category)
    else:
        results = Customer.all()

    return jsonify([pet.serialize() for pet in results]), HTTP_200_OK

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """ Retrieves a Customer with a specific id """
    app.logger.info('Finding a Pet with id [{}]'.format(id))
    customer = Customer.find(id)
    if customer:
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Customer with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

#def get_customer(url):
#    """Retrieve a Customer with a set of query condition"""
#    parsed_url = urlparse3.parse_url(url)
#    query = parsed_url.query
#    for key, value in query.items():

######################################################################
# ADD A NEW PET
######################################################################
# @app.route('/customers', methods=['POST'])
# def create_pets():
#     """ Creates a Pet in the datbase from the posted database """
#     app.logger.info('Creating a new pet')
#     req = request.get_json()
#     response = {'message': 'good request'}
#     email = req['Email'] if 'Email' in req else 'NULL'
#     address = req['Address'] if 'Address' in req else 'NULL'
#     phone_num = req['Phone_Number'] if 'Phone_Number' in req else 'NULL'
#     title = req['Title'] if 'Title' in req else 'NULL'
#     try:
#         cursor = connection.cursor()
#         query = 'INSERT INTO users \
#                  (First_Name, Last_Name, Username, \
#                   Password, Email, Address, Phone_Number, \
#                   Title, Active) \
#                   VALUES (%s, %s, %s, %s, \
#                           %s, %s, %s, %s, %s);'
#         cursor.execute(query, (req['First_Name'],
#                                req['Last_Name'], req['Username'],
#                                req['Password'], email, address,
#                                phone_num, title, 'TRUE'))
#         connection.commit()
#         cursor.close()
#         return_code = HTTP_201_CREATED
#         print "success"
#     except Exception as e:
#         response['message'] = 'Missing Information'
#         return_code = HTTP_204_NO_CONTENT
#         print e
#     return jsonify(response), return_code

######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################


@app.route('/customers/<int:id>', methods=['PUT'])
def update_customers(id):
    """ Updates a Pet in the database fom the posted database """
    app.logger.info('Updating a Customer with id [{}]'.format(id))
    customer = Customer.find(id)
    if customer:
        customer_info = request.get_json()
        customer.deserialize(customer_info)
        customer.id = id
        customer.save()
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Customer with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# DISABLE AN CUSTOMER
######################################################################


@app.route('/customers/<int:id>/disable', methods=['PUT'])
def disable_pets(id):
    app.logger.info('Disabling a Customer with id [{}]'.format(id))
    customer = Customer.find(id)
    """ Diable a Customer in the database fom the posted database """
    if customer:
        customer.active = "False"
        customer.save()
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Customer with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# DELETE A EXISTING CUSTOMER
######################################################################
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """ Removes a Pet from the database that matches the id """
    app.logger.info('Deleting a Pet with id [{}]'.format(id))
    customer = Customer.find(id)
    if customer:
        customer.delete()
    return make_response('', HTTP_204_NO_CONTENT)


######################################################################
# Demo DATA
######################################################################
@app.route('/pets/demo', methods=['POST'])
def create_demo_data():
    """ Loads a few Pets into the database for demos """
    app.logger.info('Loading demo Pets')
    Pet(0, 'fido', 'dog').save()
    Pet(0, 'kitty', 'cat').save()
    return make_response(jsonify(message='Created demo customers'), HTTP_201_CREATED)

######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')