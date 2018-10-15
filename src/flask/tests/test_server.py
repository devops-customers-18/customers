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
Test cases for the Pet Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
from app.models import DataValidationError
import app.service as service

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(unittest.TestCase):
    """ Pet Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        service.Customer.remove_all()
        service.Customer(0, 'fido', 'dog', 'nj', 'a@b.com',
                        'kerker', 'aa', '932').save()
        service.Customer(0, 'afido', 'cat', 'ny', 'c@b.com',
                        'Ker', 'ww', '9321').save()
        # first_name='', last_name='',
        # address='', email='', username='', password='',
        # phone_number='', active=True
        self.app = service.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        service.Customer.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Customer Demo REST API Service')

    def test_get_customer_list(self):
        """ Get a list of Customer """
        resp = self.app.get('/customers')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_customer(self):
        """ Get one customer """
        resp = self.app.get('/customers/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['username'], 'Ker')
        self.assertEqual(data['first_name'], 'afido')
        self.assertEqual(data['last_name'], 'cat')

    def test_get_customer_not_found(self):
        """ Get a Pet thats not found """
        resp = self.app.get('/customers/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_create_customer(self):
        """ Create a customers """
        # save the current number of pets for later comparrison
        customers_count = self.get_customers_count()
        # add a new pet
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name":"value1", "last_name":"value2", "id": 0,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
        # check that count has gone up and includes sammy
        resp = self.app.get('/customers')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), customers_count + 1)
        self.assertIn(new_json, data)

    def test_spoof_customer_id(self):
        """ Create a customer passing in an id """
        # add a new pet
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name":"value1", "last_name":"value2", "id": 999,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
        self.assertNotEqual(new_json['id'], 999)

    def test_update_customer(self):
        """ Update a customer """
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name":"value1", "last_name":"value2", "id": 0,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.put('/customers/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/customers/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
    
    def test_disable_customer(self):
        """ Disable a customer """
        resp = self.app.put('/customers/1/disable', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/customers/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['active'], 'False')

    def test_update_customer_with_no_name(self):
        """ Update a customer with no username """
        new_customer = {"password": "bar", "first_name":"value1",
                        "last_name":"value2", "address": "Jersey",
                        "phone_number": "773", "active": True,
                        "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.put('/customers/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_not_found(self):
        """ Update a Customer that can't be found """
        new_man = {"username": "noguy", "password": "bar",
                   "first_name":"value1", "last_name":"value2", "id": 0,
                   "address": "Jersey", "phone_number": "773",
                   "active": True, "email": "3333"}
        data = json.dumps(new_man)
        resp = self.app.put('/customers/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_customer(self):
        """ Delete a customer that exists """
        # save the current number of pets for later comparrison
        customer_count = self.get_customers_count()
        # delete a pet
        resp = self.app.delete('/customers/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_customers_count()
        self.assertEqual(new_count, customer_count - 1)

    def test_create_customer_with_no_name(self):
        """ Create a customer with the name missing """
        new_customer = {"password": "bar",
                        "first_name":"value1", "last_name":"value2", "id": 0,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_customer(self):
        """ Get a customer that doesn't exist """
        resp = self.app.get('/customers/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_customer_list_by_category(self):
        """ Query Customers by Category """
        resp = self.app.get('/customers', query_string='username=kerker')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('fido' in resp.data)
        self.assertFalse('afido' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['username'], 'kerker')

    def test_method_not_allowed(self):
        """ Call a Method thats not Allowed """
        resp = self.app.post('/customers/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
# Utility functions
######################################################################

    def get_customers_count(self):
        """ save the current number of customers """
        resp = self.app.get('/customers')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
