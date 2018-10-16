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
import threading


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Customer(object):
    """
    Class that represents a Customer

    This version uses an in-memory collection of customers for testing
    """
    lock = threading.Lock()
    data = []
    index = 0

    def __init__(self, id=0, first_name='', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=True):
        """ Initialize a Customer. """
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.active = active
        self.customer_dict = {"id":id, "first_name":first_name, "last_name":last_name,"address":address, "email":email, "username":username, "passward":password, "phone_number":phone_number, "active":active}

    def save(self):
        """
        Saves a Customer to the data store
        """
        if self.id == 0:
            self.id = self.__next_index()
            Customer.data.append(self)
        else:
            for i in range(len(Customer.data)):
                if Customer.data[i].id == self.id:
                    Customer.data[i] = self
                    break

    def delete(self):
        """ Removes a Customer from the data store """
        Customer.data.remove(self)

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
        if not isinstance(data, dict):
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
        return

    @classmethod
    def __next_index(cls):
        """ Generates the next index in a continual sequence """
        with cls.lock:
            cls.index += 1
        return cls.index

    @classmethod
    def all(cls):
        """ Returns all of the Customers in the database """
        return [customer for customer in cls.data]

    @classmethod
    def remove_all(cls):
        """ Removes all of the Customers from the database """
        del cls.data[:]
        cls.index = 0
        return cls.data

    @classmethod
    def find(cls, customer_id):
        """ Finds a Customer by it's ID """
        if not cls.data:
            return None
        customers = [customer for customer in cls.data if customer.id == customer_id]
        if customers:
            return customers[0]
        return None

    @classmethod
    def find_by_query(cls, key, value):
        """ Returns the list of the Customers in a data list which
        satisfied the query

        Args:
            key (string): the attributes name
            value: attributes values
        """
        return [customer for customer in cls.data if customer.__dict__.get(key) == value]
