"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
from flask import Flask
from flask_restful import Api
from .models import Customer, DataValidationError

# Create Flask application
app = Flask(__name__)
api = Api(app)

from service.resources import HomePage
from service.resources import CustomerResource
from service.resources import CustomerCollection
from service.resources import DisableAction

api.add_resource(HomePage, '/')
api.add_resource(CustomerCollection, '/customers')
api.add_resource(CustomerResource, '/customers/<int:customer_id>')
api.add_resource(DisableAction, '/customers/<int:customer_id>/disable')

#  import service

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
