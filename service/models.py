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
import pickle
from cerberus import Validator
from redis import Redis
from redis.exceptions import ConnectionError

class DataValidationError(ValueError):
    pass

class Customer(object):
    """
    Class that represents a Customer

    This version uses an in-memory collection of customers for testing
    """
    logger = logging.getLogger(__name__)
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'name': {'type': 'string', 'required': True},
        'category': {'type': 'string', 'required': True},
        'available': {'type': 'boolean', 'required': True}
        }
    __validator = Validator(schema)

    def __init__(self, cust_id=0, first_name='', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=True):
        """ Initialize a Customer. """
        self.id = cust_id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.active = active
        self.customer_dict = {"id": cust_id,
                              "first_name": first_name,
                              "last_name": last_name,
                              "address": address,
                              "email": email,
                              "username": username,
                              "passward": password,
                              "phone_number": phone_number,
                              "active": active}

    def save(self):
        """
        Saves a Customer to the data store
        """
        # if self.id == 0:
        #     self.id = self.__next_index()
        #     Customer.data.append(self)
        # else:
        #     for i in range(len(Customer.data)):
        #         if Customer.data[i].id == self.id:
        #             Customer.data[i] = self
        #             break

        if self.username is None:   # name is the only required field
            raise DataValidationError('username attribute is not set')
        if self.id == 0:
            self.id = Customer.__next_index()
        Customer.redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        """ Removes a Customer from the data store """
        # Customer.data.remove(self)
        Customer.redis.delete(self.id)

    def serialize(self):
        """ Serializes a Customer into a dictionary """
        return {"id": self.id, "first_name": self.first_name,
                "last_name": self.last_name, "address": self.address,
                "email": self.email, "username": self.username,
                "password": self.password, "phone_number": self.phone_number,
                "active": self.active}

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the Customer data
        """
        if not isinstance(data, dict) or not Customer.__validator.validate(data):
            raise DataValidationError('Invalid customer: body of request contained bad or no data')
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.address = data["address"]
            self.email = data["email"]
            self.username = data["username"]
            self.password = data["password"]
            self.phone_number = data["phone_number"]
            self.active = data["active"]
        except KeyError as err:
            raise DataValidationError('Invalid customer: missing ' + err.args[0])
        return self

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        # with cls.lock:
        #     cls.index += 1
        # return cls.index
        return Customer.redis.incr('index')

    @staticmethod
    def all():
        """ Returns all of the Customers in the database """
        # return [customer for customer in cls.data]
        results = []
        for key in Customer.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Customer.redis.get(key))
                customer = Customer(data['id']).deserialize(data)
                results.append(customer)
        return results

    @staticmethod
    def remove_all():
        """ Removes all of the Customers from the database """
        # del cls.data[:]
        # cls.index = 0
        # return cls.data
        Customer.redis.flushall()

    @staticmethod
    def find(cls, customer_id):
        """ Finds a Customer by it's ID """
        # if not cls.data:
        #     return None
        # customers = [customer for customer in cls.data if customer.id == customer_id]
        # if customers:
        #     return customers[0]
        # return None

        if Customer.redis.exists(customer_id):
            data = pickle.loads(Customer.redis.get(customer_id))
            customer = Customer(data['id']).deserialize(data)
            return customer
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Returns the list of the Customers in a data list which
        satisfied the query

        Args:
            key (string): the attributes name
            value: attributes values
        """
        # return [customer for customer in cls.data if customer.__dict__.get(key) == value]


        """ Generic Query that finds a key with a specific value """
        Customer.logger.info('Processing %s query for %s', attribute, value)
        if isinstance(value, str):
            search_criteria = value.lower() # make case insensitive
        else:
            search_criteria = value
        results = []
        for key in Customer.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Customer.redis.get(key))
                # perform case insensitive search on strings
                if isinstance(data[attribute], str):
                    test_value = data[attribute].lower()
                else:
                    test_value = data[attribute]
                if test_value == search_criteria:
                    results.append(Customer(data['id']).deserialize(data))
        return results
    
    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Customer.logger.info("Testing Connection to: %s:%s", hostname, port)
        Customer.redis = Redis(host=hostname, port=port, password=password)
        try:
            Customer.redis.ping()
            Customer.logger.info("Connection established")
        except ConnectionError:
            Customer.logger.info("Connection Error from: %s:%s", hostname, port)
            Customer.redis = None
        return Customer.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection
        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object
        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        if redis:
            Customer.logger.info("Using client connection...")
            Customer.redis = redis
            try:
                Customer.redis.ping()
                Customer.logger.info("Connection established")
            except ConnectionError:
                Customer.logger.error("Client Connection Error!")
                Customer.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            Customer.logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Customer.logger.info("Conecting to Redis on host %s port %s",
                                 creds['hostname'], creds['port'])
            Customer.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            Customer.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
            Customer.connect_to_redis('127.0.0.1', 6379, None)
            if not Customer.redis:
                Customer.logger.info("No Redis on localhost, looking for redis host")
                Customer.connect_to_redis('redis', 6379, None)
        if not Customer.redis:
            # if you end up here, redis instance is down.
            Customer.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
