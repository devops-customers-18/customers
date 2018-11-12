"""
This module contains routes without Resources
"""
from flask_restful import Resource
from service import app

######################################################################
# GET /
######################################################################
class HomePage(Resource):
    """ Resource fior the Home Page """
    def get(self):
        """ Return something useful by default """
        return app.send_static_file('index.html')
