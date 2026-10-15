# PROJECT 2
Initially creating the development virtual environment:\
python -m venv venv\
python -m pip -r requirements.txt


# LINKING TO JIRA
Include the Jira issue key in your branch name / commit message\
Example: git checkout -b SCRUM-29-Basic-Backend\
This will create a branch (and move you to that branch) named SCRUM-29-Basic-Backend, which will then show up in JIRA as a related change under stated issue

# MAKING THE POSTGRESQL DB
Currently, I'm on windows, so I used WSL to make a linux environment (google how to do that if you need it) and did everything from there\

For a linux system:\
sudo apt install postgresql postgresql-contrib postgis gdal-bin libgdal-dev libgeos-dev libproj-dev libpq-dev\
sudo service postgresql start\
sudo service postgresql status (will check if it is running)\
sudo -u postgres psql (start a sql prompter)\
CREATE USER normaluser WITH PASSWORD 'normalpassword'; (user, password, and name are all settings in django settings.py)\
CREATE DATABASE perfectrole OWNER normaluser;\
\c perfectrole (goes into the database)\
CREATE EXTENSION postgis; (adds geographic extension)\
\q (quit)\

Might change to a docker later on to make this easier, but this gets it working at least