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

import os
import json
import time  # use for rate limiting Cloudant Lite :(
import unittest
from mock import patch
from service.models import Customer, DataValidationError
from requests import HTTPError, ConnectionError

######################################################################
#  T E S T   C A S E S
######################################################################
if 'BLUEMIX_TEST' in os.environ:
    VCAP_SERVICES = {
        "cloudantNoSQLDB": [
            {"credentials": json.loads(os.environ['BINDING_CLOUDANT'])
            }
        ]
    }
else:
    VCAP_SERVICES = {
        'cloudantNoSQLDB': [
            {'credentials': {
                'username': 'admin',
                'password': 'pass',
                'host': '127.0.0.1',
                'port': 5984,
                'url': 'http://admin:pass@127.0.0.1:5984'
            }
            }
        ]
    }

ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

if 'BLUEMIX_TEST' in os.environ:
    TEST_CREDS = json.loads(os.environ['BINDING_CLOUDANT'])
else:
    TEST_CREDS = {
        "username": CLOUDANT_USERNAME,
        "password": CLOUDANT_PASSWORD,
        "host": CLOUDANT_HOST,
        "port": 5984,
        "url": "http://" + CLOUDANT_HOST + ":5984/"
    }

if 'VCAP_SERVICES' in os.environ or 'BINDING_CLOUDANT' in os.environ:
    WAIT_SECONDS = 0.5
else:
    WAIT_SECONDS = 0

class TestCustomers(unittest.TestCase):
    """ Test Cases for Customers """

    def setUp(self):
        """ Initialize the Cloudant database """
        Customer.init_db('test')
        Customer.remove_all()
        time.sleep(WAIT_SECONDS)

    def tearDown(self):
        time.sleep(WAIT_SECONDS)

    def test_create_a_customer(self):
        """ Create a customer and assert that it exists """
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        self.assertTrue(customer != None)
        self.assertEqual(customer.first_name, "Arturo")
        self.assertEqual(customer.last_name, "Frank")
        self.assertEqual(customer.address, "USA")
        self.assertEqual(customer.email, "abc@abc.com")
        self.assertEqual(customer.username, "IAmUser")
        self.assertEqual(customer.password, "password")
        self.assertEqual(customer.phone_number, "1231231234")
        self.assertEqual(customer.active, True)
        self.assertEqual(customer.id, 1)
        self.assertEqual(customer._id, None)
        customer2 = Customer(first_name='ac',
                             last_name='bd',
                             username=None,
                             password='poi')
        self.assertRaises(DataValidationError, customer2.create)
        self.assertRaises(DataValidationError, customer2.save)

    def test_add_a_customer(self):
        """ Create a customer and add it to the database """
        customers = Customer.all()
        time.sleep(WAIT_SECONDS)
        self.assertEqual(customers, [])
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        self.assertTrue(customer != None)
        self.assertEqual(customer._id, None)
        customer.save()
        time.sleep(WAIT_SECONDS)
        self.assertNotEqual(customer._id, None)
        customers = Customer.all()
        time.sleep(WAIT_SECONDS)
        self.assertEqual(len(customers), 1)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_create_customer_with_http_error(self, bad_mock):
        """ Create a customer with http error """
        bad_mock.side_effect = HTTPError()
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)

    def test_update_a_customer(self):
        """ Update a Customer"""
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        self.assertNotEqual(customer._id, None)
        # Change it an save it
        customer.first_name = "k9"
        customer.save()
        time.sleep(WAIT_SECONDS)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        time.sleep(WAIT_SECONDS)
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].first_name, "k9")

    def test_delete_a_customer(self):
        """ Delete a Customer"""
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_serialize_a_customer(self):
        """ Test serialization of a Customer """
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn('_id', data)
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
        data = {"first_name": "Arturo", "last_name": "Frank", "address": "USA", "email": "abc@abc.com", "username": "IAmUser", "password": "password", "phone_number": "1231231234", "active": True, "id": 1}
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer._id, None)
        self.assertEqual(customer.first_name, "Arturo")
        self.assertEqual(customer.last_name, "Frank")

    def test_deserialize_with_no_data(self):
        """ Deserialize a Customer with no data """
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, {})

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Customer with bad data """
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, {"first_name": 123})

    def test_find_customer(self):
        """ Find a Customer by ID """
        customer = Customer("Hey", "Jude")
        customer.save()
        time.sleep(WAIT_SECONDS)
        saved_customer = Customer.find(customer._id)
        self.assertIsNot(customer, None)
        self.assertEqual(customer._id, saved_customer._id)
        self.assertEqual(customer.first_name, "Hey")

    def test_customer_not_found(self):
        """ Test for a Customer that doesn't exist """
        customer = Customer.find('this_is_uuid')
        time.sleep(WAIT_SECONDS)
        self.assertIs(customer, None)

    def test_find_by_query(self):
        """ Find Customers by Category """
        Customer("Arturo", "Frank").save()
        Customer("Hey", "Jude").save()
        time.sleep(WAIT_SECONDS)
        customers = Customer.find_by_query(last_name="Frank")
        self.assertNotEqual(len(customers), 0)
        self.assertEqual(customers[0].last_name, "Frank")

    def test_find_by_name(self):
        """ Find Customers by Username """
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        customers = Customer.find_by_query(username="IAmUser")
        self.assertNotEqual(len(customers), 0)
        self.assertEqual(customers[0].username, "IAmUser")

    def test_find_by_address(self):
        """ Find Customers by Address """
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        customers = Customer.find_by_query(address="USA")
        self.assertNotEqual(len(customers), 0)
        self.assertEqual(customers[0].address, "USA")

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_delete(self, bad_key_mock):
        """ Test KeyError on delete"""
        bad_key_mock.side_effect = KeyError()
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        customer.delete()
        time.sleep(WAIT_SECONDS)

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_update(self, bad_key_mock):
        """ Test KeyError on update """
        bad_key_mock.side_effect = KeyError()
        customer = Customer("Arturo", "Frank", "USA", "abc@abc.com", "IAmUser", "password", "1231231234", True, 1)
        customer.save()
        time.sleep(WAIT_SECONDS)
        customer.first_name = "k9"
        customer.save()
        time.sleep(WAIT_SECONDS)

    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Customer.init_db, 'test')

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES), })
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Customer.init_db()
        self.assertIsNotNone(Customer.client)
        Customer("fido", "dog", True).save()
        time.sleep(WAIT_SECONDS)
        customer = Customer.find_by_query(first_name="fido")
        self.assertNotEqual(len(customer), 0)
        self.assertEqual(customer[0].first_name, "fido")

    @patch.dict(os.environ, {'BINDING_CLOUDANT': json.dumps(TEST_CREDS), })
    def test_binding_services(self):
        """ Test if BINDING_CLOUDANT works """
        Customer.init_db()
        self.assertIsNotNone(Customer.client)
        Customer("fido", "dog", True).save()
        time.sleep(WAIT_SECONDS)
        customer = Customer.find_by_query(first_name="fido")
        self.assertNotEqual(len(customer), 0)
        self.assertEqual(customer[0].first_name, "fido")

    def test_not_vcap_services(self):
        """ Test if no VCAP_SERVICES works """
        Customer.init_db()
        self.assertIsNotNone(Customer.client)
        Customer("fido", "dog", True).save()
        time.sleep(WAIT_SECONDS)
        customer = Customer.find_by_query(first_name="fido")
        self.assertNotEqual(len(customer), 0)
        self.assertEqual(customer[0].first_name, "fido")

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
