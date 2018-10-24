# customers
It is to build the `/customers` resource.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```
    $ git clone https://github.com/devops-customers-18/customers.git
    $ cd customers
    $ vagrant up
```


## Access Flask

In the vm, run
```
    $ vagrant ssh
    $ cd /vagrant
    $ python run.py
```

## Run test
In the vm, run
```
    $ vagrant ssh
    $ cd /vagrant
    $ nosetests
```
it will show the test result and coverage rate

## API Docs.

### List Resources 
1. ```/customers```
    Use this URL to GET the list of all customer resources.
2. Example: (the double quotes matter in this case)
    ```curl -X GET http://0.0.0.0:5000/customers```
### Read a Resource
1. ```/customers/{id}```
    Use this URL to retrieve a customer with specific id.
2. Example: (the double quotes matter in this case)
    ```
    Create one entry, id = 1.
    curl -d '{"username": "foo111", "password": "bar", "first_name":"value1", "last_name":"value2", "id": 0, "address": "New York", "phone_number": "773", "active": "True", "email": "1@3"}' -H "Content-Type: application/json" -X POST http://0.0.0.0:5000/customers
    
    Retrive it.
    curl -X GET http://0.0.0.0:5000/customers/1
    ```

### Create a Resource 

1. ```/customers```

    Use this URL to send POST request to our customer resources. This URL allows user to create an entry in our resources.

2. When setting id = 0, meaning "create a new entry"

3. Example:

    ```
    curl -d '{"username": "foo111", "password": "bar", "first_name":"value1", "last_name":"value2", "id": 0, "address": "New York", "phone_number": "773", "active": "True", "email": "1@3"}' -H "Content-Type: application/json" -X POST http://0.0.0.0:5000/customers
    ```
### Update a Resource
1. ```/customers/{id}```
    Use this URL to update an existing entry in our resources where the customer id is ```{id}```
2. Example:
    ```
    curl -d '{"username": "foo111", "password": "bar", "first_name":"value1", "last_name":"value2", "id": 0, "address": "Jersey", "phone_number": "773", "active": "True", "email": "3333"}' -H "Content-Type: application/json" -X PUT http://0.0.0.0:5000/customers/2
    ```
### Delete a Resource
1. ```/customers/{id}```
    Use this URL to DELETE the customer resources which satisfied the id equals to ```{id}```
2. Example
    ```
    Create one entry, id = 1.
    curl -d '{"username": "foo111", "password": "bar", "first_name":"value1", "last_name":"value2", "id": 0, "address": "New York", "phone_number": "773", "active": "True", "email": "1@3"}' -H "Content-Type: application/json" -X POST http://0.0.0.0:5000/customers
    
    Delete it.
    curl -X DELETE http://0.0.0.0:5000/customers/1
    ```

### Query Resources by some attribute of the Resource
1. ```/customers?query1=value&query2=value```
    Use this URL to GET the customer resources which satisfied all the query conditions.
2. Example: (the double quotes matter in this case)
    ```curl -X GET "http://0.0.0.0:5000/customers?active=True&username=foo111"```


### Perform some Action on the Resource - Disable the active
1. ```/customers/{id}/disable```
    Use this URL to send PUT request to disable the customer resources.
2. Example:
    ``` curl -X PUT http://0.0.0.0:5000/customers/2/disable```


## Shutdown

When you are done, you can use the `exit` command to get out of the virtual machine just as if it were a remote server and shut down the vm with the following:

```
    $ exit
    $ vagrant halt
```


If the VM is no longer needed you can remove it with from your computer to free up disk space with:

```
    $ vagrant destroy
```

This repo is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created by John Rofrano.
