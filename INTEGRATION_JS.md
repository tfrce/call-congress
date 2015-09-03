
Embedding Javascript
===========

Campaigns can be easily embedded in external forms by including `<script src="/api/campaign/ID/embed.js"></script>`. 
This script loads jQuery from a CDN (if not already available), and attaches a post-submit callback to the specified form.

Additional parameters can be specified on the `CallPowerOptions` object before inserting the script:

* form: form id to attach, defaults to 'call_form'
* phoneField: input id with the user phone number, defaults to 'phone_id'
* locationField: input id with the user location, defaults to 'location_id'

To render a complete form, include `<iframe src="/api/campaign/ID/embed_iframe.html"></iframe>">` to create a form ready to be filled out.

Custom Embeds
-------------

If you have a form with a submit callback already defined, you may want to do more complex integrations. Include the CallPowerForm.js from `/api/campaign/ID/CallPowerForm.js` and define your own callbacks for onSuccess and onError.

