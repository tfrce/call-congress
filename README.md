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
    * specifying a target in the api call
    * or entering their zip code to look up their location
* Sign up for a call-back if the target is busy


Campaign Configuration
----------------------

### TODO update for new web interface


Installation Instructions
-------------------
Read detailed instrustions at [INSTALLATION.md](INSTALLATION.md)


Integration
-----------
For most uses, you can just place the `<script>` tag provided in the launch page into your action platform.

For more complex integrations, Call Power provides [INTEGRATION_API.md](json APIs). You will need to authenticate either as a logged in user, or with an ADMIN_API_KEY specified the python environment.


Updating political data
--------------------------------

Political data is downloaded from Sunlight as CSV files stored in this repository. These are read on startup and saved in a memory cache for fast local lookup.

To update these files with new data after elections, run `cd call_server/political_data/data && make clean && make`
