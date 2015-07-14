Installation
==============

Configure Settings
------------

The app requires several account keys to run. These should not be stored in version control, but in environment variables. For development, you can export these from your virtualenv/bin/activate script, or put them in a .env file and load them with [autoenv](https://github.com/kennethreitz/autoenv).

At a minimum, you will need to set:

* SECRET_KEY, to secure login sessions cryptographically
    * This will be created for you automatically if you use the deploy to Heroku button, or you can generate one using with this Javascript one-liner: `chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+:<>{}[]".split(''); key = ''; for (i = 0; i < 50; i++) key += chars[Math.floor(Math.random() * chars.length)]; alert(key);`
* SUNLIGHT_API_KEY, to do Congressional lookups. Sign up for one at [SunlightFoundation.com](https://sunlightfoundation.com/api/accounts/register/)
* TWILIO_ACCOUNT_SID, for an account with at least one purchased phone number
* TWILIO_AUTH_TOKEN, for the same account
* INSTALLED_ORG, displayed on the site homepage
* SITENAME, defaults to CallPower

To test Twilio functionality in development, you will need to set:

* APPLICATION_ROOT to point to a web-routable address. Twilio provides [ngrok](https://ngrok.com) to do this for free.

For production, you will also need to set:

* DATABASE_URI, a sqlalchemy [connection string](https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format) for a postgres or mysql database addresses
* APPLICATION_ROOT to the address where this application will live
* CACHE_MEMCACHED_SERVERS, a list or tuple of memcached servers

If you are storing assets on Amazon S3, or another [Flask-Store provider](http://flask-store.soon.build)

* STORE_S3_BUCKET
* STORE_S3_REGION
* S3_ACCESS_KEY
* S3_SECRET_KEY

If you would like to let users reset their passwords over email:

* MAIL_SERVER, defaults to `localhost`
* MAIL_PORT, defaults to 1025
* MAIL_USERNAME
* MAIL_PASSWORD
* MAIL_DEFAULT_SENDER, defaults to `info@callpower.org`


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
    npm install -g bower
    bower install
    python manager.py assets build
    
    # create an admin user
    python manager.py createadminuser
 
    # run local server for debugging
    python manager.py run
    
    # for testing twilio
    # run in another tab
    ngrok 5000

When the dev server is running, the front-end will be accessible at [http://localhost:5000/](http://localhost:5000/), and proxied to external routes at [http://ngrok.com](http://ngrok.com).

Unit tests can also be run with:

    python tests/run.py

Production server
------------------
To run in production:

    # create ENV variables
    
    # open correct port
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    
    # initialize the database
    python manager.py migrate up
    
    # create an admin user
    python manager.py createadminuser

    # run server - will charge real $ and connect real calls
    foreman start
    
Make sure your webserver can serve audio files out of `APPLICATION_ROOT/instance/uploads`. Or if you are using Amazon S3, ensure your buckets are configured for public access.

Performance Tips
--------------------------------
TBD, fill in once we benchmark

- How many dynos / uwsgi processes for incoming calls 
- gevent monkey-patch
