"""
This module contains all of Resources for the Customer API
"""
from flask import abort, request
from flask_restful import Resource
from flask_api import status
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Customer, DataValidationError

######################################################################
#  PATH: /pets/{id}
######################################################################


class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer/{id} - Returns a Customer with the id
    PUT /customer/{id} - Updates a Customer with the id
    DELETE /customer/{id} - Deletes a Customer with the id
    """

    def get(self, customer_id):
        """
        Retrieve a single Customer
        """
        app.logger.info('Finding a Customer with id [{}]'.format(customer_id))
        customer = Customer.find(customer_id)
        if customer:
            message = customer.serialize()
            return_code = status.HTTP_200_OK
        else:
            message = {'error': 'Customer with id: %s was not found' % str(customer_id)}
            return_code = status.HTTP_404_NOT_FOUND
        return message, return_code

    def put(self, customer_id):
        """
        Update a single Customer
        """
        app.logger.info('Updating a Customer with id [{}]'.format(customer_id))

        content_type = request.headers.get('content_type')

        if not content_type or content_type != 'application/json':
            app.logger.info('11111111')
            abort(status.HTTP_400_BAD_REQUEST, "No Content-Type set")

        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND, "Customer with id '{}' was not found.".format(customer_id))

        customer_info = request.get_json()
        try:
            customer.deserialize(customer_info)
        except DataValidationError as error:
            raise BadRequest(str(error))

        customer.id = customer_id
        customer.save()

        message = customer.serialize()
        return_code = status.HTTP_200_OK
        return message, return_code

    def delete(self, customer_id):
        """
        Delete a Customer
        """
        app.logger.info('Deleting a Customer with id [{}]'.format(customer_id))
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()
        return '', status.HTTP_204_NO_CONTENT

######################################################################
# DELETE ALL PET DATA (for testing only)
######################################################################
    @app.route('/customers/reset', methods=['DELETE'])
    def customers_reset():
        """ Removes all customers from the database """
        Customer.remove_all()
        return '', status.HTTP_204_NO_CONTENT
