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

        if request.args:
            # Query customers.
            costumer_lists = [Customer.find_by_query(key, val) for key, val in request.args.items()]
            costumer_set_list = [set(costumer_list) for costumer_list in costumer_lists]
            costumer_set = set.intersection(*costumer_set_list)
            message = [costumer.serialize() for costumer in costumer_set]
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
        if not content_type or content_type != 'application/json':
            abort(status.HTTP_400_BAD_REQUEST, "No Content-Type set")

        customer_info = request.get_json()
        customer = Customer()
        try:
            customer.deserialize(customer_info)
        except DataValidationError as error:
            raise BadRequest(str(error))
        customer.save()

        app.logger.info('Customer with new id [%s] saved!', customer.id)
        location_url = api.url_for(CustomerResource, customer_id = customer.id, _external=True)

        message = customer.serialize()
        return message, status.HTTP_201_CREATED, { 'Location': location_url }
