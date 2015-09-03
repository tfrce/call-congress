/*!
  * CallPowerForm.js
  * Connects embedded action form to CallPower campaign
  * Requires jQuery
  *
  * Displays call script in overlay or by replacing form
  * Override functions onSuccess or onError in CallPowerOptions
  * Instantiate with form selector to connect callbacks
  * (c) Spacedog.xyz 2015, license AGPLv3
  */

var CallPowerForm = function (formSelector) {
  // instance variables
  this.form = $(formSelector);
  this.locationField = $('{{campaign.embed.get("location_sel","#location_id")}}');
  this.phoneField = $('{{campaign.embed.get("phone_sel","#phone_id")}}');
  this.scriptDisplay = 'overlay';
  
  // allow options override
  for (var option in window.CallPowerOptions || []) {
    this[option] = CallPowerOptions[option];
  }

  this.form.on("submit", $.proxy(this.makeCall, this));
};

CallPowerForm.prototype = function() {
  // prototype variables
  var createCallURL = '{{url_for("call.create", campaign_id=campaign.id, _external=True)}}';
  var campaignId = "{{campaign.id}}";

  var getCountry = function() {
    return "{{campaign.country|default('US')}}";
  };

  var cleanUSZipcode = function() {
    var isValid = /(\d{5}([\-]\d{4})?)/.test(this.locationField.val());
    return isValid ? this.locationField.val() : false;
  };

  var cleanUSPhone = function() {
    var num = this.phoneField.val();
    // remove whitespace, parens
    num = num.replace(/\s/g, '').replace(/\(/g, '').replace(/\)/g, '');
    // plus, dashes
        num = num.replace("+", "").replace(/\-/g, '');
        // leading 1
        if (num.charAt(0) == "1")
            num = num.substr(1);
        var isValid = (num.length == 10); // ensure just 10 digits remain 

    return isValid ? num : false;
  };

  // default to US validators
  var cleanPhone = cleanUSPhone;
  var cleanLocation = cleanUSZipcode;

  var onSuccess = function(response) {
    if (response.script === undefined) { return false; }
    if (response.campaign !== 'active') { return false; }

    if (this.scriptDisplay === 'overlay') {
      // display simple overlay with script content
      var scriptOverlay = $('<div class="overlay"><div class="modal">'+response.script+'</div></div>');
      $('body').append(scriptOverlay);
      scriptOverlay.overlay();
      scriptOverlay.trigger('show');
      return true;
    }

    if (this.scriptDisplay === 'replace') {
      // replace form with script content
      this.form.html(response.script);
      return true;
    }

    return false;
  };

  var onError = function(message) {
    console.error(message);
    return false;
  };

  var makeCall = function(event) {
    if (event !== undefined) { event.preventDefault(); }

    if (!(this.location() && this.phone())) {
      return this.onError('form invalid');
    }
    $.ajax(createCallURL, {
      method: 'GET',
      data: {
        campaignId: campaignId,
        userLocation: this.location(),
        userPhone: this.phone(),
        userCountry: this.country()
      },
      success: $.proxy(this.onSuccess, this),
      error: $.proxy(this.onError, this)
    });
  };

  // public method interface
  return {
    country: getCountry,
    location: cleanLocation,
    phone: cleanPhone,
    onError: onError,
    onSuccess: onSuccess,
    makeCall: makeCall,
  };
} ();