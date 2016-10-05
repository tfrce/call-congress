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

To test Twilio functionality in development, you will need your server to have a web-routable address. 

* Twilio provides [ngrok](https://ngrok.com) to do this for free. When using the debug server you can use --external=SERVERID.ngrok.com to set SERVER_NAME and STORE_DOMAIN
* To test text-to-speech playback in the browser, you will need to create a [TwiML app](https://www.twilio.com/user/account/apps) with the Voice request URL http://YOUR_HOSTNAME/api/twilio/text-to-speech. Place the resulting application SID in your environment as TWILIO_PLAYBACK_APP

For production, you will also need to set:

* CALLPOWER_CONFIG='call_server.config:ProductionConfig', so that manager.py knows to use a real database for migrations
* DATABASE_URI, a sqlalchemy [connection string](https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format) for a postgres or mysql database addresses
* REDIS_URL, a URI for the Redis server
* APPLICATION_ROOT to the path where the application will live. If you are using a whole domain or subdomain, this *SHOULD NOT* be defined. Otherwise, it will mess up cookie handling and cause CSRF 400 errors on login.

If you are storing assets on Amazon S3, or another [Flask-Store provider](http://flask-store.soon.build)

* STORE_S3_BUCKET
* STORE_S3_REGION (eg: us-east-1, or us-west-2)
* STORE_DOMAIN (automatically set by S3 region and bucket, override if you are using another provider)
* S3_ACCESS_KEY
* S3_SECRET_KEY

If you would like to let users reset their passwords over email:

* MAIL_SERVER, defaults to `localhost`
* MAIL_PORT, defaults to 25
* MAIL_USERNAME
* MAIL_PASSWORD
* MAIL_DEFAULT_SENDER, defaults to `info@callpower.org`

For more information on default configuration values, check the [Flask Documentation](http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values)

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

    # if testing twilio, run in another tab
    ngrok http 5000
 
    # run local server for debugging, pass external name from ngrok
    python manager.py runserver --external=SERVERID.ngrok.io

When the dev server is running, the front-end will be accessible at [http://localhost:5000/](http://localhost:5000/), and proxied to external routes at [http://ngrok.com](http://ngrok.com).

Unit tests can also be run with:

    python tests/run.py

Production server
------------------
To run in production, with compiled assets:

    # create ENV variables
    
    # open correct port
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    
    # initialize the database
    python manager.py migrate up
    
    # create an admin user
    python manager.py createadminuser

    # prime cache with political data
    python manager.py loadpoliticaldata

    # if you are running a reverse proxy, you can start the application with foreman start
    foreman start

    # or point your WSGI server to `call_server.wsgi:application`
    # to load the application directly
    
Make sure your webserver can serve audio files out of `APPLICATION_ROOT/instance/uploads`. Or if you are using Amazon S3, ensure your buckets are configured for public access.

Docker setup
------------------
A Dockerfile is included for building a container environment suitable for both development and production. To begin, copy `docker-compose.yml.example` to `docker-compose.yml` and fill in the appropriate values. Consult [the first part of this guide](#configure-settings) to learn what the required variables are.

In the dockerized environment, there is one additional variable which may be set. `FLASK_ENV` will be consulted in the container's entrypoint to determine how to boot the app:

FLASK_ENV           | Result
--------------------|--------
production          | App is brought up using `uwsgi`. In this case, the environment variable `PORT` should also be set.
development         | App is brought up with flask's built in http server.
development-expose  | App is brought up with flask's built in http server and then exposed externally using `ngrok`. Use this environment to test twilio functionality.

If `FLASK_ENV` is not provided, the default is to bring the app up in the development environment.


Performance Tips
--------------------------------
TBD, fill in once we benchmark

- How many dynos / uwsgi processes for incoming calls 
- gevent monkey-patch
