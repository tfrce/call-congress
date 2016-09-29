import os
from twilio.rest import TwilioRestClient


if __name__ == "__main__":
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    if not account_sid:
        account_sid = raw_input('Master Account SID: ')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    if not auth_token:
        auth_token = raw_input('Master Account Token: ')

    client = TwilioRestClient(account_sid, auth_token)
    friendly_name = raw_input('New SubAccount Name: ')
    account = client.accounts.create(friendly_name=friendly_name)
    print "SubAccount Created", account
    print "Put the following in your .env:"
    print "export TWILIO_ACCOUNT_SID=", account.sid
    print "export TWILIO_AUTH_TOKEN=", account.auth_token
