from flask import abort
from flask_api import status
from flask_restful import Resource
from service import app, api
from service.models import Customer


######################################################################
# DISABLE AN CUSTOMER
######################################################################

class DisableAction(Resource):
    """ Disable a Customer """
    def put(self, customer_id):
        """ Diable a Customer's active attributes in the database """
        app.logger.info('Disabling a Customer with id [{}]'.format(customer_id))
        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND, "Customer with id '{}' was not found.".format(customer_id))

        customer.active = "False"
        customer.save()
        message = customer.serialize()
        return_code = status.HTTP_200_OK
        return message, return_code
