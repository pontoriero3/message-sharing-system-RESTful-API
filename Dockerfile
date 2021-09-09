FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# copy the requirements.txt to leverage Docker cache
COPY ./requirements.txt /message-sharing-system-RESTful-API-main/requirements.txt

WORKDIR /message-sharing-system-RESTful-API-main

RUN pip install -r requirements.txt

COPY . /message-sharing-system-RESTful-API-main

ENTRYPOINT [ "python" ]

CMD [ "message-sharing-system-RESTful-API.py" ]
