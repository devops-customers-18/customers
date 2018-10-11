FROM ubuntu:16.04

MAINTAINER Your Name "slydomon@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /home/vagrant/requirements.txt

RUN pwd

RUN ls

# WORKDIR /share_folder/flask

# RUN pwd

RUN pip install -r /home/vagrant/requirements.txt

# COPY . /home/vagrant

#ENTRYPOINT [ "python" ]

#CMD [ "app.py" ]