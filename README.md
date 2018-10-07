# customers
It is to build the `/customers` resource.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```
    $ git clone https://github.com/devops-customers-18/customers.git
    $ cd customers/vm
    $ vagrant up
```

Once the VM is up you can use it with:

```
    $ vagrant ssh
    $ cd /share_folder/flask
    $ python run.py
```

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
