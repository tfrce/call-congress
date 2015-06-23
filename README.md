Call Power
==============

Connecting people to power through their phones.

The admin interface lets activists:

* Create and edit campaigns
* Adjust call targets and phone numbers
* Record audio prompts and select versions
* Easily embed campaign forms on their website
* View campaign statistics and system analytics

The server lets callers:

* Dial in directly to the campaign number
* Fill out a web form and get a call back on their phone
    * can specify target in the api call
    * can have the user enter their zip code to look up the target
* Sign up for a call-back if the target is busy


Campaign Configuration
----------------------

# TODO update for new web interface


Installation Instructions
-------------------
Read detailed instrustions at [INSTALLATION.md](INSTALLATION.md)


Updating political data
--------------------------------
Just download the latest data from Sunlight Congress API using:

    cd data && make -B
    git commit data/districts.csv data/legislators.csv
