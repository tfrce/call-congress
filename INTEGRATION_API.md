
REST API
===========

A read-only REST API is available for integrating with external services. Access is allowed by passing an api_key parameter, or through flask user authentication. Results can be filtered by any field, using a [flask-restless](http://flask-restless.readthedocs.org/en/latest/searchformat.html) formatted parameter.

`GET /api/calls` returns a paginated list of Call objects. Fields include:

* id
* timestamp (UTC)
* campaign_id
* target_id
* call_id (from Twilio, a 40 character string)
* status (from Twilio, one of [completed, no-answer, canceled, failed])
* duration (in seconds)

`GET /api/campaign/ID` returns a read-only representation of a campaign object, including:

* id
* name
* campaign_country: a two-character ISO code of the country, used for political data lookups (optional, default US)
* campaign_state: a two-character postal abbreviation of the state (optional)
* campaign_type: one of [executive, congress, state, local, custom]
* campaign_subtype: depends on campaign_type, see `call_server/campaign/constants.py for valid choices`
* audio_msgs
* phone_numbers: [formatted for Twilio]
* required_fields: a hash of field names and values required to place a call. May include
	* userCountry: a two-character ISO code of the country (default US)
	* userLocation: method to locate user, one of [postal, latlon]
* status: one of [archived, paused, live]
* target_ordering: one of [in-order, shuffle, upper-first, lower-first]

`GET /api/audiorecording` returns a paginated list of AudioRecording objects. Fields include:

* id
* key: 
* version: an incrementing version counter
* description: a textual description of the recording, provided by the user
* file_url: an external url to the recorded file (optional)
* text_to_speech: text to be read by the Twilio <Say> verb (optional)
* selected_campaigns: list of campaign names that have selected this recording
* selected_campaign_ids: list of campaign ids that have selected this recording

`GET /api/campaign/ID/stats.json` returns aggregate statistics for a campaign, including:

* name
* completed
* total_counts

`GET /api/campaign/ID/call_chart.json` returns a list of campaign calls by status and date to graph, formatted for ChartKick. Results can be further limited by passing start or end parameters in ISO format, and a timespan as one of (minute, hour, day, month, year). Each chart includes

* name
* data 
	* date
	* value

