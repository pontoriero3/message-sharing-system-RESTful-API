FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /message-sharing-system-RESTful-API/requirements.txt

WORKDIR /message-sharing-system-RESTful-API

RUN pip install -r requirements.txt

COPY . /message-sharing-system-RESTful-API

ENTRYPOINT [ "python" ]

CMD [ "message-sharing-system-RESTful-API.py" ]
