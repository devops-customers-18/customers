"""
This module contains the Pet Collection Resource
"""
from flask import request, abort
from flask_restful import Resource
from flask_api import status
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Customer, DataValidationError
from . import CustomerResource


class CustomerCollection(Resource):
    """ Handles all interactions with collections of Customers """

    def get(self):
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
        username = request.args.get('username')
        address = request.args.get('address')

        if username:
            # Query customers by name
            app.logger.info('Filtering by username:%s', username)
            results = Customer.find_by_name(username)

            message = [customer.serialize() for customer in results]
            return_code = status.HTTP_200_OK
        elif address:
            # Query customers by name
            app.logger.info('Filtering by username:%s', username)
            results = Customer.find_by_address(address)

            message = [customer.serialize() for customer in results]
            return_code = status.HTTP_200_OK

        elif request.args:
            # Query customers by query
            #key = request.args.keys()
            app.logger.info('Filtering by query:%s', request.args.keys())
            results = Customer.find_by(kwargs=request.args)
            #results = Customer.find_by_query({key:request.args.get(key)})
            message = [customer.serialize() for customer in results]
            return_code = status.HTTP_200_OK
        else:
                # List all customers.
            results = Customer.all()
            message = [customer.serialize() for customer in results]
            return_code = status.HTTP_200_OK
        return message, return_code

    def post(self):
        """Create a customer in the database"""
        app.logger.info('Creating a new customer')

        content_type = request.headers.get('Content-Type')

        data = {}

        if content_type == 'application/x-www-form-urlencoded':
            app.logger.info('Processing FORM data')
            data = {
                'username': request.form['name'],
                'password': request.form['category'],
                'first_name': request.form['available'],
                'last_name': request.form['available'],
                'address': request.form['address'],
                'phone_number': request.form['phone_number'],
                'active': request.form['active'],
                'email': request.form['active'],
            }
        elif content_type == 'application/json':
            app.logger.info('Processing JSON data')
            data = request.get_json()
        else:
            message = 'Unsupported Content-Type: {}'.format(content_type)
            app.logger.info(message)
            abort(status.HTTP_400_BAD_REQUEST, message)

        customer = Customer()
        try:
            customer.deserialize(data)
        except DataValidationError as error:
            raise BadRequest(str(error))
        customer.save()
        app.logger.info('Customer with new id [%s] saved!', customer.id)
        location_url = api.url_for(CustomerResource, customer_id=customer.id, _external=True)
        return customer.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
