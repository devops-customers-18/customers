# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/xenial64"

  config.vm.synced_folder "src/", "/src", create: true
  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Forward PostgreSQL port
  config.vm.network "forwarded_port", guest: 5432, host: 5432, host_ip: "127.0.0.1"

  config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "256"
    vb.cpus = 1
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your ssh keys for github so that your git credentials work
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Copy your ~/.vimrc file so that vi looks the same
  if Dir.exists?(File.expand_path("~/.vimrc"))
    config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
  end

  # Windows users need to change the permission of files and directories
  # so that nosetests runs without extra arguments.
  # Mac users can comment this next line out
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=775,fmode=664"]

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y git python-pip python-dev build-essential
    apt-get install pylint
    apt-get -y autoremove

    #pip install --upgrade pip
    # Install app dependencies
    cd /vagrant
    pip install -r /src/requirements.txt
  SHELL

  #build shared directory with vagrant
  #must behind installation of python; otherwise python will become python3
  # config.vm.provision "docker" do |d|
  #   d.build_image "/share_folder/flask",
  #   #   args: "-t flask-image:latest"
  #   # d.run "flask-image",
  #   #   args: "--restart=always -d -h flask_image -p 5000:5000/tcp"
  #   # d.build_image "/src/psql",
  #   #   args: "-t psql-image:latest"
  #   d.run "psql-image",
  #     args: "--restart=always -d --name my_psql -h postgres -p 127.0.0.1:5432:5432 -v /var/lib/psql/data:/var/lib/postgresql/data"
  #   #d.pull_images "postgres"
  # end

  # Install
  # Run init script
  # Listening on the port (default 5432)
  config.vm.provision "shell", inline: <<-INITDB
    apt-get install -y postgresql
    sudo -u postgres psql -f /src/psql/initdb.sql
    sudo service postgresql start
  INITDB


end