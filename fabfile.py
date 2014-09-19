from fabric.api import local, task

@task
def create_env():
    local("virtualenv venv")
    virtualenv("pip install -r requirements.txt --allow-external mysql-connector-python")


def virtualenv(command):
    """
    Runs a command in the virtual environment
    """
    local('source venv/bin/activate && {command}'.format(command=command),
          shell='/bin/bash')
