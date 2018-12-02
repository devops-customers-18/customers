Feature: The pet store service back-end
    As a Pet Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my pets

"id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "phone_number": self.phone_number,
            "active": self.active


Background:
    Given the following pets
    | id  | first_name | last_name | address | email       | username  | password | phone_number | active |
    | 1   | Arno       | Fido      | USA     | arno@email  | userarno  | password | 1111         | true   |
    | 2   | Larno      | Dido      | Taiwan  | larno@email | userlarno | password | 2222         | true   |
    | 3   | Barno      | Gido      | USA     | barno@email | userbarno | password | 3333         | true   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "first_name" to "Carno"
    And I set the "last_name" to "Rido"
    And I set the "address" to "USA"
    And I set the "email" to "carno@email"
    And I set the "username" to "usercarno"
    And I set the "password" to "password"
    And I set the "phone_number" to "4444"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: List all Customers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Arno" in the results
    And I should see "Larno" in the results
    And I should see "Barno" in the results

Scenario: Delete a Customer
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Delete" button
    And I press the "Search" button
    Then I should not see "Arno" in the results
    And I should see "Larno" in the results
    And I should see "Barno" in the results

Scenario: List all Customer living in USA
    When I visit the "Home Page"
    And I set the "address" to "USA"
    And I press the "Search" button
    Then I should see "Arno" in the results
    And I should not see "Larno" in the results
    And I should see "Barno" in the results

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Retrieve" button
    Then I should see "Arno" in the "first_name" field
    When I change "first_name" to "Boxer"
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "Boxer" in the "first_name" field

Scenario: Disable a Customer
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Retrieve" button
    Then I should see "Arno" in the "first_name" field
    When I select the "active" option
    And I press the "Update" button
    Then I should see the message "Success"
    When I set the "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "false" in the "active" field
