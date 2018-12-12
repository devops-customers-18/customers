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
Test cases for the Customer Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import os
import unittest
import logging
import json
import time
from flask_api import status    # HTTP Status Codes
from service import app
from service.models import Customer

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

if 'VCAP_SERVICES' in os.environ:
    WAIT_SECONDS = 0.5
else:
    WAIT_SECONDS = 0

######################################################################
#  T E S T   C A S E S
######################################################################


class TestCustomerServer(unittest.TestCase):
    """ Customer Server Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = app.test_client()
        Customer.init_db("tests")
        Customer.remove_all()
        Customer(first_name='fido',
                 last_name='dog',
                 address='ny',
                 email='a@b.com',
                 username='kerker',
                 password='aa',
                 phone_number='932',
                 active=True,
                 id = 1
        ).save()

        time.sleep(WAIT_SECONDS)

        Customer(first_name='afido',
                 last_name='cat',
                 address='ny',
                 email='c@b.com',
                 username='Ker',
                 password='ww',
                 phone_number='9321',
                 active=True,
                 id = 2
        ).save()

        time.sleep(WAIT_SECONDS)

        Customer(first_name='redo',
                 last_name='cat',
                 address='ny',
                 email='x@z.com',
                 username='haha',
                 password='qq',
                 phone_number='233',
                 active=False,
                 id = 3
        ).save()

        time.sleep(WAIT_SECONDS)

        Customer(first_name='tedo',
                 last_name='dog',
                 address='nj',
                 email='e@z.com',
                 username='kuku',
                 password='ee',
                 phone_number='423',
                 active=False,
                 id = 4
        ).save()

        self.app = app.test_client()

    def tearDown(self):
        """ Runs after each test """
        Customer.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Customer Demo RESTful Service', resp.data)

    def test_get_customer_list_without_queries(self):
        """ Get a list of Customer """
        resp = self.app.get('/customers')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 4)

    def test_get_a_customer(self):
        """ Find one customer """
        customer = self.get_customer('Ker')[0]  # returns a list
        resp = self.app.get('/customers/{}'.format(customer['_id']))

        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = json.loads(resp.data)
        self.assertEqual(data['first_name'], 'afido')
        self.assertEqual(data['last_name'], 'cat')
        self.assertEqual(data['address'], 'ny')
        self.assertEqual(data['email'], 'c@b.com')
        self.assertEqual(data['username'], 'Ker')
        self.assertEqual(data['password'], 'ww')
        self.assertEqual(data['phone_number'], '9321')
        self.assertEqual(data['id'], 2)

    def test_get_customer_not_found(self):
        """ Get a Customer thats not found """
        resp = self.app.get('/customers/ohno')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_customer(self):
        """ Create a customers """
        # save the current number of pets for later comparrison
        customers_count = self.get_customers_count()
        # add a new pet
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "id": 5}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
        self.assertEqual(new_json['first_name'], 'value1')
        self.assertEqual(new_json['last_name'], 'value2')
        self.assertEqual(new_json['address'], 'Jersey')
        self.assertEqual(new_json['email'], '3333')
        self.assertEqual(new_json['password'], 'bar')
        self.assertEqual(new_json['phone_number'], '773')
        self.assertEqual(new_json['id'], 5)

        # check that count has gone up and includes sammy
        resp = self.app.get('/customers')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), customers_count + 1)
        self.assertIn(new_json, data)

    def test_create_customer_no_content_type(self):
        """ Create a Customer with no Content-Type """
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "id": 5}
        data = json.dumps(new_customer)

        resp = self.app.post('/customers', data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_form_content_type(self):
        """ Create a Customer with form Content-Type """
        customers_count = self.get_customers_count()
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "id": 5}

        resp = self.app.post('/customers', data=new_customer, content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
        self.assertEqual(new_json['first_name'], 'value1')
        self.assertEqual(new_json['last_name'], 'value2')
        self.assertEqual(new_json['address'], 'Jersey')
        self.assertEqual(new_json['email'], '3333')
        self.assertEqual(new_json['password'], 'bar')
        self.assertEqual(new_json['phone_number'], '773')
        self.assertEqual(new_json['id'], 5)

        # check that count has gone up and includes sammy
        resp = self.app.get('/customers')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), customers_count + 1)
        self.assertIn(new_json, data)

    def test_create_customer_with_no_name(self):
        """ Create a customer with the name missing """
        new_customer = {"password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_spoof_customer_id(self):
        """ Create a customer passing in an _id """
        # add a new pet
        new_customer = {"username": "foo111", "password": "bar",
                        "first_name": "value1", "last_name": "value2", "id": 999,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "_id": "heyyoyoyoyoyoyoyoyo"}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'foo111')
        self.assertEqual(new_json['first_name'], 'value1')
        self.assertEqual(new_json['last_name'], 'value2')
        self.assertEqual(new_json['address'], 'Jersey')
        self.assertEqual(new_json['email'], '3333')
        self.assertEqual(new_json['password'], 'bar')
        self.assertEqual(new_json['phone_number'], '773')
        self.assertNotEqual(new_json['_id'], "heyyoyoyoyoyoyoyoyo")

    def test_update_customer(self):
        """ Update a customer """
        new_customer = {"username": "kerker", "password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "id": 77}
        data = json.dumps(new_customer)

        customer = self.get_customer('kerker')[0]  # returns a list

        resp = self.app.put('/customers/{}'.format(customer['_id']), data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/customers/{}'.format(customer['_id']))
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['username'], 'kerker')
        self.assertEqual(new_json['first_name'], 'value1')
        self.assertEqual(new_json['last_name'], 'value2')
        self.assertEqual(new_json['address'], 'Jersey')
        self.assertEqual(new_json['email'], '3333')
        self.assertEqual(new_json['password'], 'bar')
        self.assertEqual(new_json['phone_number'], '773')
        self.assertEqual(new_json['id'], 77)

    def test_update_customer_no_content_type(self):
        """ Update a customer Content-Type"""
        new_customer = {"password": "bar",
                        "first_name": "value1", "last_name": "value2", "id": 0,
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333"}
        data = json.dumps(new_customer)

        customer = self.get_customer('kerker')[0]
        resp = self.app.put('/customers/{}'.format(customer['_id']), data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_with_no_name(self):
        """ Update a customer with no username """
        new_customer = {"password": "bar", "first_name": "value1",
                        "last_name": "value2", "address": "Jersey",
                        "phone_number": "773", "active": True,
                        "email": "3333"}

        customer = self.get_customer('kerker')[0]
        data = json.dumps(new_customer)
        resp = self.app.put('/customers/{}'.format(customer['_id']), data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_not_found(self):
        """ Update a Customer that can't be found """
        new_man = {"username": "noguy", "password": "bar",
                   "first_name": "value1", "last_name": "value2", "id": 0,
                   "address": "Jersey", "phone_number": "773",
                   "active": True, "email": "3333"}

        data = json.dumps(new_man)
        resp = self.app.put('/customers/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_disable_customer(self):
        """ Disable a customer """
        customer = self.get_customer('kerker')[0]

        resp = self.app.put('/customers/{}/disable'.format(customer['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/customers/{}'.format(customer['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        new_json = json.loads(resp.data)
        self.assertEqual(new_json['active'], 'False')

    def test_disable_nonexisting_customer(self):
        resp = self.app.put('/customers/3/disable', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_disable_customer_no_content_type(self):
        """ Disable a customer no Content-Type"""
        resp = self.app.put('/customers/1/disable')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_customer(self):
        """ Delete a customer that exists """
        # save the current number of pets for later comparrison
        customer_count = self.get_customers_count()
        # delete a customer
        customer = self.get_customer('Ker')[0]  # returns a list
        resp = self.app.delete('/customers/{}'.format(customer['_id']), content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_customers_count()
        self.assertEqual(new_count, customer_count - 1)

    def test_get_customer_list_with_queries(self):
        """ Get Customers with queries """

        resp = self.app.get('/customers', query_string='address=ny')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)

    def test_call_create_with_an_id(self):
        """ Call create passing an id """
        new_customer = {"username": "kerker", "password": "bar",
                        "first_name": "value1", "last_name": "value2",
                        "address": "Jersey", "phone_number": "773",
                        "active": True, "email": "3333", "id": 77}
        data = json.dumps(new_customer)
        resp = self.app.post('/customers/1', data=data)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

######################################################################
# Utility functions
######################################################################

    def get_customer(self, username):
        """ retrieves a pet for use in other actions """
        resp = self.app.get('/customers',
                            query_string='username={}'.format(username))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn(username, resp.data)
        data = json.loads(resp.data)

        return data

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
