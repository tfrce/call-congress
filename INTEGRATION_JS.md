
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

The embed script should interoperate with existing forms, but if you have a form with a submit callback already defined, you may want to write your own integration. You can add javascript that will be run after the success callback in the Custom JS field. For example, if you are using the overlay script display, you might want to manually trigger an action after the overlay is closed, like `$('.overlay').on('hide', function() { actionkit.form.submit(); });`

If your validation needs are more complex, you can include just CallPowerForm.js from `/api/campaign/ID/CallPowerForm.js` and define your own functions for location, phone, onSuccess or onError.
