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
    """ Resource for the Home Page """
    def get(self):
        """ Return something useful by default """
        return app.send_static_file('index.html')
