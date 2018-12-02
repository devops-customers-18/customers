# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Models for Customer

All of the models are stored in this module

Models
------
Customer - A Customer used in the Customer Store

"""
import os
import json
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')


class DataValidationError(Exception):
    """ Custom Exception with data validation fails """
    pass

class Customer(object):
    """
    Class that represents a Customer

    This version uses an in-memory collection of customers for testing
    """
    logger = logging.getLogger(__name__)
    client = None
    database = None

    def __init__(self, first_name='', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=True):
        """ Initialize a Customer. """
        self.id = None
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.active = active
        self.customer_dict = {"first_name": first_name,
                              "last_name": last_name,
                              "address": address,
                              "email": email,
                              "username": username,
                              "passward": password,
                              "phone_number": phone_number,
                              "active": active}

    def create(self):
        """
        Creates a new Customer in the database POST
        """
        if self.username is None:   # name is the only required field
            raise DataValidationError('username attribute is not set')

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Customer.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = str(document['_id'])

    def update(self):
        """
        Updates a Customer in the database
        """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()

    def save(self):
        """
        Saves a Customer to the data store
        """
        if self.username is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id:
            self.update()
        else:
            self.create()

    def delete(self):
        """ Removes a Customer from the data store """
        # Customer.data.remove(self)
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.delete()

    def serialize(self):
        """ serializes a Customer into a dictionary """
        customer = {"id": self.id,
                    "first_name": self.first_name,
                    "last_name": self.last_name,
                    "address": self.address,
                    "email": self.email,
                    "username": self.username,
                    "password": self.password,
                    "phone_number": self.phone_number,
                    "active": self.active
                    }

        if self.id:
            customer['_id'] = self.id
        return customer

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the Customer data
        """
        Customer.logger.info(data)
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.address = data["address"]
            self.email = data["email"]
            self.username = data["username"]
            self.password = data["password"]
            self.phone_number = data["phone_number"]
            self.active = data["active"]
        except KeyError as error:
            raise DataValidationError('Invalid customer: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid customer: body of request contained bad or no data')

        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    def all(cls):
        """ Query that returns all Customers """
        results = []
        for doc in cls.database:
            customer = Customer().deserialize(doc)
            customer.id = doc['_id']
            results.append(customer)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################
    @classmethod
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            customer = Customer()
            customer.deserialize(doc)
            results.append(customer)
        # return [doc for doc in query.result]
        return results

    @classmethod
    def find(cls, customer_id):
        """ Finds a Customer by it's ID """
        try:
            document = cls.database[customer_id]
            return Customer().deserialize(document)
        except KeyError:
            return None

    @classmethod
    def find_by_query(cls, **kwargs):
        """ Returns the list of the Customers in a data list which
        satisfied the query
        Args:
            key (string): the attributes name
            value: attributes values
        """
        query = Query(cls.database, selector=kwargs)
        key = kwargs.keys()[0]
        results = []
        for doc in query.result:
            customer = Customer()
            customer.deserialize(doc)
            if doc[key] == kwargs[key]:
                results.append(customer)
        return results

    @classmethod
    def find_by_name(cls, username):
        """ Query that finds Pets by their name """
        return cls.find_by(username=username)

    @classmethod
    def find_by_address(cls, address):
        """ Query that finds Pets by their address """
        return cls.find_by(address=address)

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='customers', connect=True):
        """
        Initialized Coundant database connection
        """
        opts = {}
        vcap_services = {}
        Customer.logger.info("Mananananana")
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Customer.logger.info('Running in Bluemix mode.')
            Customer.logger.info(os.environ['VCAP_SERVICES'])
            creds = json.loads(os.environ['VCAP_SERVICES'])
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
            Customer.logger.info("Mananananana")
            Customer.logger.info(vcap_services)
        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        elif 'BINDING_CLOUDANT' in os.environ:
            Customer.logger.info('Found Kubernetes Bindings')
            creds = json.loads(os.environ['BINDING_CLOUDANT'])
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
        else:
            Customer.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            creds = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

        # opts['username'] = vcap_services['username']
        # opts['password'] = vcap_services['password']
        # opts['host'] = vcap_services['host']
        # opts['port'] = vcap_services['port']
        # opts['url'] = vcap_services['url']
        Customer.logger.info("Mananananana")
        Customer.logger.info(vcap_services)
        print(vcap_services)

        # Look for Cloudant in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('cloudantNoSQLDB'):
                cloudant_service = vcap_services[service][0]
                Customer.logger.info(cloudant_service)
                opts['username'] = cloudant_service['credentials']['username']
                opts['password'] = cloudant_service['credentials']['password']
                opts['host'] = cloudant_service['credentials']['host']
                opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = cloudant_service['credentials']['url']
        
        Customer.logger.info(opts)
        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            Customer.logger.info('Error - Failed to retrieve options. '
                                 'Check that app is bound to a Cloudant service.')
            exit(-1)

        Customer.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Customer.logger.info('Running in Admin Party Mode...')
            Customer.client = Cloudant(opts['username'],
                                        opts['password'],
                                        url=opts['url'],
                                        connect=True,
                                        auto_renew=True,
                                        admin_party=ADMIN_PARTY
                                       )

        except ConnectionError:
            raise AssertionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Customer.database = Customer.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Customer.database = Customer.client.create_database(dbname)
        # check for success
        if not Customer.database.exists():
            raise AssertionError('Database [{}] could not be obtained'.format(dbname))
