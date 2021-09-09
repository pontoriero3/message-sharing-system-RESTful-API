message-sharing-system-RESTful-API
===============

This is a RESTful API implementing a messaging system, built with Flask and Bootstrap for the style.
Python >= 3.4 is needed for all the features to work.

Installation:
-------------

1. Clone this repository.

run python3 in virtual environment/your local machine

```
pip3 install -r requirements.txt
```
or (depending on your pip version)
```
pip install -r requirements.txt
```

Run the app:
-----------
```
python message_sharing_system.py
```

Once the app is up and running:
-----------
Visit http://0.0.0.0:5000/ 

You will be able to:

- Create a message from the homepage (Home).
- Search by uid to read a specific message (Messages) or visit http://0.0.0.0:5000/message/**enter**uid** 
- Log in as an admin and view all the messages that have been sent and delete them if needed. (Admin/Log in (username:admin, password:psw))


Run the unit tests:
------------------
```
python message_sharing_system_unittest.py
```

Security Risks:
--------

- This RESTful API doesn't use authentication. 
- The POST requests are  currently vulnerable to CSRF attacks.
