To run, install the following pre-requisites:

sudo apt install python3 python3-pip mysql-server python3-mysqldb libmysqlclient-dev python3-dev python3-tk rabbitmq-server
MySQL Server requires you to set a root password

Then install the Python pre-requisites:
sudo -H pip3 install -U Django Celery Django-Celery-beat mysqldb-python matplotlib --upgrade pip

A database must be set up for the project:
mysql -u root -p
CREATE DATABASE softeng;

The password set in softeng/settings.py must match your local MySQL database.

RabbitMQ must be configured next:
sudo rabbitmqctl add_user user password
sudo rabbitmqctl add_vhost vhostname
sudo rabbitmqctl set_permissions -p vhostname user ".*" ".*" ".*"

The values for user/password/vhost must match the values in softeng/settings.py


There is a number of helper scripts that can be executed:
./migrate.sh - Must be executed once in order to configure the database layout.
./run_celery.sh - Starts Celery workers, to allow for multiple actions running in parallel.
./run.sh - Starts the web server and puts the website online.
./run_live.sh - Connects to the stocks feed in order to start fetching trades. This is called daily at 1AM automatically.