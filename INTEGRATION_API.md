`GET /api/campaign/ID` returns a read-only representation of a campaign object, including:

* audio_msgs
* campaign_state
* campaign_type: [executive, congress, state, local, custom]
* campaign_subtype: depends on campaign_type, see `call_server/campaign/constants.py for valid choices`
* id
* name
* phone_numbers: [formatted for twilio]
* required_fields: 
* status: [archived, paused, live]
* target_ordering: [in-order, shuffle, upper-first, lower-first]
* and others

`GET /api/campaign/ID/stats.json` returns a list of campaign calls statistics to graph:

* Total Calls
* Calls by Day: {YYYY-MM-DD: num}
