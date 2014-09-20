# Setting up with Fabric

First install fabric to your local system, not your virtualenv (`sudo pip install fabric`)

To generate your virtual environment, you can run either create a default environment manually with 

    $ fab create_env

## Config File

When creating your environment, a configuration file (call_congress.config) will be generated in the git root. Edit this file to add the appropriate values before trying to run the application. When you run the application (with `fab run`) all of these values will be exported as environment variables.

## Running with Fabric 

Once you've set up the config file, you should be able to run the application by running:

    $ fab run

If you want to specify that the app should run in development or production, then run the following:

    $ fab run:production
    $ fab run:development

By default, the app runs in development.

## Other Fabric operations

- `fab clean` removes all .pyc files from the project
