# Wepublic Backend

## Dev Setup

Instruction for Ubuntu 16.04, Adapt them to your OS

1. install python3, pip3 and virtualenv on your machine
2. Create a new Directory for the backend source and the virtualenv: `$ cd /somewhere/you/like/ && mkdir wp_backend && cd wp_backend`
3. create a new python virtualenv with python3 as your interpreter of choice: ` $ virtualenv -p python3 ./venv`
4. Activate the virtualenv: `$ source ./venv/bin/activate`
5. clone repo from git: `$ git clone git@github.com:wepublic/backend.git`
6. move into repo and install dependencies: `$ cd backend && pip install -r requirements.txt`
7. migrate your local db: `$ python manage.py migrate`
8. create admin user: `$ python manage.py createsuperuser`
9. run the App: `$ python manage.py runserver`



## Authentication

Das Wepublic Backend setzt auf Token-Basierte Authentifizierung. 
