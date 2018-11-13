# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Customer Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
import json
from mock import patch
from redis import Redis, ConnectionError
from werkzeug.exceptions import NotFound
from service.models import Customer, DataValidationError

######################################################################
#  T E S T   C A S E S
######################################################################


class TestCustomers(unittest.TestCase):
    """ Test Cases for Customers """

    def setUp(self):
        Customer.init_db()
        Customer.remove_all()

    def test_a_customer(self):
        """ Create a customer and assert that it exists """
        customer = Customer(0, "Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True)
        self.assertTrue(customer != None)
        self.assertEqual(customer.id, 0)
        self.assertEqual(customer.first_name, "Arturo")
        self.assertEqual(customer.last_name, "Frank")
        self.assertEqual(customer.address, "USA")
        self.assertEqual(customer.email, "abc@abc.com")
        self.assertEqual(customer.username, "IAmUser")
        self.assertEqual(customer.password, "password")
        self.assertEqual(customer.phone_number, "1231231234")
        self.assertEqual(customer.active, True)

    def test_add_a_customer(self):
        """ Create a customer and add it to the database """
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = Customer(0, "Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True)
        self.assertTrue(customer != None)
        self.assertEqual(customer.id, 0)
        customer.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(customer.id, 1)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

    def test_update_a_customer(self):
        """ Update a Customer"""
        customer = Customer(0, "Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True)
        customer.save()
        self.assertEqual(customer.id, 1)
        # Change it an save it
        customer.category = "k9"
        customer.save()
        self.assertEqual(customer.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].category, "k9")

    def test_delete_a_customer(self):
        """ Delete a Customer"""
        customer = Customer(0, "Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True)
        customer.save()
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_serialize_a_customer(self):
        """ Test serialization of a Customer """
        customer = Customer(0, "Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True)
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('first_name', data)
        self.assertEqual(data['first_name'], "Arturo")
        self.assertIn('last_name', data)
        self.assertEqual(data['last_name'], "Frank")
        self.assertIn('address', data)
        self.assertEqual(data['address'], "USA")
        self.assertIn('email', data)
        self.assertEqual(data['email'], "abc@abc.com")
        self.assertIn('password', data)
        self.assertEqual(data['password'], "password")
        self.assertIn('phone_number', data)
        self.assertEqual(data['phone_number'], "1231231234")
        self.assertIn('active', data)
        self.assertEqual(data['active'], True)

    def test_deserialize_a_customer(self):
        """ Test deserialization of a Customer """
        data = {"id": 1, "first_name": "Arturo", "last_name": "Frank", "address": "USA", "email": "abc@abc.com", "username": "IAmUser", "password": "password", "phone_number": "1231231234", "active": True}
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, 0)  # id should be ignored
        self.assertEqual(customer.first_name, "Arturo")
        self.assertEqual(customer.last_name, "Frank")

    def test_deserialize_with_no_data(self):
        """ Deserialize a Customer with no data """
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Customer with bad data """
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, "data")

    def test_find_customer(self):
        """ Find a Customer by ID """
        Customer(0, "Hey", "Jude").save()
        Customer(0, "Beatles", "Band").save()
        customer = Customer.find(2)
        self.assertIsNot(customer, None)
        self.assertEqual(customer.id, 2)
        self.assertEqual(customer.first_name, "Beatles")

    def test_customer_not_found(self):
        """ Test for a Customer that doesn't exist """
        Customer(0, "Arturo", "Frank").save()
        customer = Customer.find(2)
        self.assertIs(customer, None)

    def test_find_by_query(self):
        """ Find Customers by Category """
        Customer(0, "Arturo", "Frank").save()
        Customer(0, "Hey", "Jude").save()
        customers = Customer.find_by_query("last_name", "Frank")
        self.assertNotEqual(len(customers), 0)
        self.assertEqual(customers[0].last_name, "Frank")

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
