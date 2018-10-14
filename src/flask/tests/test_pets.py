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
Test cases for Pet Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.models import Customer, DataValidationError
#, db
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(unittest.TestCase):
    """ Test Cases for Pets """

#    @classmethod
#    def setUpClass(cls):
#        """ These run once per Test suite """
#        app.debug = False
#        # Set up the test database
#        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
#
#    @classmethod
#    def tearDownClass(cls):
#        pass
#
#    def setUp(self):
#        Pet.init_db(app)
#        db.drop_all()    # clean up the last tests
#        db.create_all()  # make our sqlalchemy tables
#
#    def tearDown(self):
#        db.session.remove()
#        db.drop_all()
#
    def test_create_a_pet(self):
        """ Create a pet and assert that it exists """
        customer = Customer(first_name='Fido', last_name='',
                 address='', email='Fido@gmail', username='', password='',
                 phone_number='888', active=True)
        self.assertTrue(customer != None)
        self.assertEqual(customer.id, 0)
        self.assertEqual(customer.first_name, "Fido")
        self.assertEqual(customer.email, "Fido@gmail")
        self.assertEqual(customer.active, True)

    def test_add_a_pet(self):
        """ Create a pet and add it to the database """
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = Pet(name="fido", category="dog", available=True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, None)
        pet.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(pet.id, 1)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)

    def test_update_a_pet(self):
        """ Update a Pet """
        customer = Customer(first_name='Fido', last_name='',
                 address='', email='Fido@gmail', username='', password='',
                 phone_number='888', active=True)
        customer.save()
        #self.assertEqual(customer.id, 0)
        # Change it an save it
        customer.phone_number = "777"
        customer.save()
        self.assertEqual(customer.phone_number, "777")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        #self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].email, "Fido@gmail")

    def test_delete_a_pet(self):
        """ Delete a Pet """
        customer = Customer(first_name='Fido', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=True)
        customer.save()
        self.assertEqual(len(Customer.all()), 1)
        # delete the pet and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_serialize_a_pet(self):
        """ Test serialization of a Pet """
        customer = Customer(first_name='kevin', last_name='yang',
                 address='', email='', username='', password='',
                 phone_number='', active=False)
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('first_name', data)
        self.assertEqual(data['first_name'], "kevin")
        self.assertIn('last_name', data)
        self.assertEqual(data['last_name'], "yang")
        self.assertIn('active', data)
        self.assertEqual(data['active'], False)

    def test_deserialize_a_pet(self):
        """ Test deserialization of a Pet """
        data = {"id":0, "first_name":'Fido', "last_name":'',
                "address":'', "email":'Fido@gmail', "username":'', "password":'',
                "phone_number":'', "active":True}
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, 0)
        self.assertEqual(customer.first_name, "Fido")
        self.assertEqual(customer.email, "Fido@gmail")
        self.assertEqual(customer.active, True)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_find_pet(self):
        """ Find a Pet by ID """
        Customer(first_name='Fido', last_name='',
                 address='', email='', username='', password='',
                 phone_number='888', active=False).save()
        kevin = Customer(first_name="Fido", phone_number="888", active=False)
        kevin.save()
        customer = Customer.find(kevin.id)
        self.assertIsNot(customer, None)
        self.assertEqual(customer.id, kevin.id)
        self.assertEqual(customer.first_name, "Fido")
        self.assertEqual(customer.active, False)

    def test_find_by_phone_number(self):
        """ Find Pets by Category """
        Customer(first_name='Fido', last_name='',
                 address='', email='', username='', password='',
                 phone_number='888', active=True).save()
        Customer(first_name='Dodo', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=False).save()
        customers = Customer.find_by_feature("phone_number","888")
        self.assertEqual(customers[0].phone_number, "888")
        self.assertEqual(customers[0].first_name, "Fido")
        self.assertEqual(customers[0].active, True)

    def test_find_by_name(self):
        """ Find a Pet by Name """
        Customer(first_name='Fido', last_name='',
                 address='', email='Fido@gmail', username='', password='',
                 phone_number='', active=True).save()
        Customer(first_name='Dido', last_name='',
                 address='', email='', username='', password='',
                 phone_number='', active=True).save()
        customers = Customer.find_by_feature("first_name","Fido")
        self.assertEqual(customers[0].email, "Fido@gmail")
        self.assertEqual(customers[0].first_name, "Fido")
        self.assertEqual(customers[0].active, True)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
