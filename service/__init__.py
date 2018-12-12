"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import os
import sys
import logging
from flask import Flask
from flask_restful import Api
from flask_restplus import Api as  BaseApi, Resource, fields
from .models import Customer, DataValidationError

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

api = Api(app)

class Api(BaseApi):
    def _register_doc(self, app_or_blueprint):
        # HINT: This is just a copy of the original implementation with the last line commented out.
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
        #app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)
    @property
    def base_path(self):
        return ''

######################################################################
# Configure Swagger before initilaizing it
######################################################################
apii = Api(app,
          version='3.0.0',
          title='Customer REST API Service ',
          description='This is a customer server.',
          doc='/apidocs/index.html'
         )

# This namespace is the start of the path i.e., /cutomers
ns = apii.namespace('Customers',default=None, description='Customer operations')
apii.namespaces.pop(0)

# Define the model so that the docs reflect what can be sent
Customer_model = apii.model('Customer', {
    '_id': fields.String(readOnly=True,
                         description='The unique id assigned internally by service'),
    'first_name': fields.String(required=True,
                          description='The first name of a Customer'),
    'last_name': fields.String(required=True,
                              description='The last name of a Customer'),
    'address': fields.String(required=True,
                              description='The address of a Customer'),
    'phone_number': fields.String(required=True,
                              description='The phone_number of a Customer'),
    'email': fields.String(required=True,
                              description='The last name of a Customer'),
    'username': fields.String(required=True,
                              description='The last username of a Customer'),
    'password': fields.String(required=True,
                              description='The last password of a Customer'),
    'active': fields.String(required=True,
                              description='The acive status of a Customer'),
    'id': fields.Integer(required=True,
                              description='The ID of a Customer'),

})


from service.resources import HomePage
from service.resources import CustomerResource
from service.resources import CustomerCollection
from service.resources import DisableAction

api.add_resource(HomePage, '/')
api.add_resource(CustomerCollection, '/customers')
api.add_resource(CustomerResource, '/customers/<customer_id>')
api.add_resource(DisableAction, '/customers/<customer_id>/disable')

#  import service

# Overwirte the original implementation to enable using the '/' as root
# from github flask-restplus/issues/247

# Set up logging for production
print 'Setting up logging for {}...'.format(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

app.logger.info('************************************************************')
app.logger.info('     C U S T O M E R   R E S T   A P I   S E R V I C E ')
app.logger.info('************************************************************')
app.logger.info('Logging established')


@app.before_first_request
def init_db(dbname="customers"):
    print("Creating")
    """ Initlaize the model """
    Customer.init_db(dbname)
