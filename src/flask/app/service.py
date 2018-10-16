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
Customer Shop Demo

This is an example of a pet shop service written with Python Flask
It demonstraits how a RESTful service should be implemented.

Paths
-----
GET  /customers - Retrieves a list of pets from the database
GET  /customers{id} - Retrirves a Pet with a specific id
POST /customers - Creates a Pet in the datbase from the posted database
PUT  /customers/{id} - Updates a Pet in the database fom the posted database
DELETE /customers{id} - Removes a Pet from the database that matches the id
"""

import os
import sys
import logging

from flask import jsonify, request, url_for, make_response
from app.database import db_connect
from app.models import Customer, DataValidationError
from . import app
# from urlparse3 import urlparse3

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
CONNECTION = db_connect()

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
                   url=url_for('get_customer', _external=True)), HTTP_200_OK
# Customers starts here.

######################################################################
# ADD A NEW CUSTOMER
######################################################################


@app.route('/customers', methods=['POST'])
def create_customers():
    """Create a customer in the database."""
    app.logger.info('Creating a new customer')
    customer_info = request.get_json()
    print customer_info
    customer = Customer()
    customer.deserialize(customer_info)
    customer.save()
    message = customer.serialize()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_customer', cust_id=customer.id, _external=True)
    return response

######################################################################
# QUERY A CUSTOMER
######################################################################


@app.route('/customers', methods=['GET'])
def get_customer():
    """query and get the intersection of the queries.
    if there is no given query return all the list
    Args:
        **par: parameter of query
        empty equry

    return:
        1. the intersection of the parameters
        2. empty equry will return all the data
    """
    app.logger.info('Query a Customer with query')
    app.logger.info('Queries are: {}'.format(request.args.items().__str__()))

    if request.args:
        # Query customers.
        costumer_lists = [Customer.find_by_query(key, val) for key, val in request.args.items()]
        costumer_set_list = [set(costumer_list) for costumer_list in costumer_lists]
        costumer_set = set.intersection(*costumer_set_list)
        message = [costumer.serialize() for costumer in costumer_set]
        return_code = HTTP_200_OK
    else:
        # List all customers.
        results = Customer.all()
        message = [customer.serialize() for customer in results]
        return_code = HTTP_200_OK
    return jsonify(message), return_code

######################################################################
# RETRIEVE A Cusotmer
######################################################################
@app.route('/customers/<int:cust_id>', methods=['GET'])
def find_customer(cust_id):
    """ Retrieves a Customer with a specific id """
    app.logger.info('Finding a Customer with id [{}]'.format(cust_id))
    customer = Customer.find(cust_id)
    if customer:
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Customer with id: %s was not found' % str(cust_id)}
        return_code = HTTP_404_NOT_FOUND
    return jsonify(message), return_code

######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################


@app.route('/customers/<int:cust_id>', methods=['PUT'])
def update_customers(cust_id):
    """ Updates a Customer in the database fom the posted database """
    app.logger.info('Updating a Customer with id [{}]'.format(cust_id))
    customer = Customer.find(cust_id)
    if customer:
        customer_info = request.get_json()
        customer.deserialize(customer_info)
        customer.id = cust_id
        customer.save()
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Customer with id: %s was not found' % str(cust_id)}
        return_code = HTTP_404_NOT_FOUND
    return jsonify(message), return_code

######################################################################
# DISABLE AN CUSTOMER
######################################################################

@app.route('/customers/<int:cust_id>/disable', methods=['PUT'])
def disable_customer(cust_id):
    """ Diable a Customer's active attributes in the database """
    app.logger.info('Disabling a Customer with id [{}]'.format(cust_id))
    customer = Customer.find(cust_id)

    if customer:
        customer.active = "False"
        customer.save()
        message = customer.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Customer with id: %s was not found' % str(cust_id)}
        return_code = HTTP_404_NOT_FOUND
    return jsonify(message), return_code

######################################################################
# DELETE A EXISTING CUSTOMER
######################################################################


@app.route('/customers/<int:cust_id>', methods=['DELETE'])
def delete_customer(cust_id):
    """ Removes a Customer from the database that matches the id """
    app.logger.info('Deleting a Customer with id [{}]'.format(cust_id))
    customer = Customer.find(cust_id)
    if customer:
        customer.delete()
    return make_response('', HTTP_204_NO_CONTENT)

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
