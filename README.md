Call Congress
==============

A simple flask server that connects calls between citizens and their congress person using the Twilio API.

The server handles two cases:

* A phone call made to the campaign number
* A web-initiated call to connect a user's phone number to congress
    * can specify congress person(s) in the api call
    * can have the user punch in their zip code and look up their congressional members

### Incoming phone calls
Each new campaign's Twilio phone number needs to be [configured](http://twilio.com/user/account/phone-numbers/incoming) to point to:

    /incoming_call?campaignId=abc-1234

The user will be prompted to punch in their zip code, the server will locate their members of congress using the [Sunlight Labs locate data](http://sunlightlabs.github.io/congress/index.html#bulk-data/zip-codes-to-congressional-districts), and dial them.

### Web-initiated connection calls
These calls are made from a web form where the user enters their phone number to be connected to Congress (will be prompted for zip code):

    /create?campaignId=abc-123&userPhone=1234567890

or a specific member of congress:

    /create?campaignId=abc-123&userPhone=1234567890&repIds=P000197

or to member(s) based on zip code:

    /create?campaignId=abc-123&userPhone=1234567890&zipcode=98102

Required Params:

* **userPhone**
* **campaignId**

Optional Params: *(either or)*

* **zipcode**
* **repIds**: identifiers (can be more than one) from the Sunlight API's [**bioguide_id**](http://sunlightlabs.github.io/congress/legislators.html#fields/identifiers) field


Campaign Configuration
----------------------

# todo update for new web interface


Installation Instructions
-------------------
Read detailed instrustions at [INSTALLATION.md](INSTALLATION.md)


Updating political data
--------------------------------
Just download the latest data from Sunlight Congress API using:

    cd data && make -B
    git commit data/districts.csv data/legislators.csv
