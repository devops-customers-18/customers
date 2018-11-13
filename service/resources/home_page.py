"""
This module contains routes without Resources
"""
from flask_restful import Resource
from flask_api import status
from service import app, api
from . import CustomerCollection

######################################################################
# GET /
######################################################################
class HomePage(Resource):
    """ Resource fior the Home Page """
    def get(self):
        """ Return something useful by default """
        message = {
            'name': 'Customer Demo REST API Service',
            'version': '1.0',
            'url': api.url_for(CustomerCollection)
        }
        return message, status.HTTP_200_OK
