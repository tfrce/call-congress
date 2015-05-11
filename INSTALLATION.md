Installation
==============

Account Keys
------------

The app uses environment variables to store account keys. For development you will need to set:

* SUNLIGHTLABS_KEY
* TWILIO_DEV_ACCOUNT_SID
* TWILIO_DEV_AUTH_TOKEN
* TW_NUMBER

and for production:

* SUNLIGHTLABS_KEY
* TWILIO_ACCOUNT_SID
* TWILIO_AUTH_TOKEN
* APPLICATION_ROOT (url for application server)
* TASKFORCE_KEY (used for querying statistics)


Development mode
-------------------
To install locally and run in debug mode use:

    # create ENV variables
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements/development.txt

    # create the database
    python manager.py migrate up

    # compile assets
    bower install
    python manage.py assets build
 
    # run local server for debugging
    python manage.py run
    # for testing twilio, need internet-visible urls to do call handling
    ngrok -subdomain="1cf55a5a" 5000

When the dev server is running, the front-end will be accessible at [http://localhost:5000/](http://localhost:5000/).

Unit tests can also be run, using:

    python tests/test.py

Production server
------------------
To run in production:

    # create ENV variables
    # open correct port
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    
    # initialize the database
    python manage.py migrate up

    # run server - will charge real $ and connect real calls
    foreman start

Updating for changes in congress
--------------------------------
Just download the latest data from Sunlight Congress API using:

    cd data && make -B
    git commit data/districts.csv data/legislators.csv
