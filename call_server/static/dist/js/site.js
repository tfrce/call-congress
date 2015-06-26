/*global $, _*/

window.CallPower = _.extend(window.CallPower || {}, {
    Models: {},
    Collections: {},
    Views: {},
    Routers: {},
    init: function () {
        console.log('Call Power');

        new this.Routers.Campaign({});
    }
});

window.renderTemplate = function(selector, context) {
    var template = _.template($('script[type="text/template"]'+selector).html(), { 'variable': 'data' });
    return $(template(context));
};

window.flashMessage = function(message, status, global) {
    if (status === 'undefined') { var status = 'info'; }
    var flash = $('<div class="alert alert-'+status+'">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          message+'</div>');
    if (global) {
        $('#global_message_container').empty().append(flash).show();
    } else {
        $('#flash_message_container').append(flash);
    }
};

$(document).ready(function () {
    var csrftoken = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    CallPower.init();
    Backbone.history.start({pushState: true, root: "/admin/"});
});

/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignAudioForm = Backbone.View.extend({
    el: $('form#audio'),

    events: {
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .upload': 'onUpload',
      'click .version': 'onVersion',

      'submit': 'submitForm'
    },

    initialize: function() {
  
    },

    onRecord: function(event) {
      event.preventDefault();

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    key: inputGroup.prev('label').attr('for'),
                    description: inputGroup.find('.description .help-inline').text(),
                    example_text: inputGroup.find('.description .example-text').text(),
                    campaign_id: $('input[name="campaign_id"]').val()
                  };
      this.microphoneView = new CallPower.Views.MicrophoneModal();
      this.microphoneView.render(modal);
    },

    onPlay: function(event) {
      event.preventDefault();
      console.log('onPlay');
    },

    onVersion: function(event) {
      event.preventDefault();
      console.log('onVersion');

      var inputGroup = $(event.target).parents('.input-group');
      var modal = {
        name: inputGroup.prev('label').text(),
        key: inputGroup.prev('label').attr('for'),
        campaign_id: $('input[name="campaign_id"]').val()
      };
      this.versionsView = new CallPower.Views.VersionsModal();
      this.versionsView.render(modal);
    },

    validateForm: function() {
      var isValid = true;

      // call validators
      
      return isValid;
    },

    submitForm: function(event) {
      event.preventDefault();

      if (this.validateForm()) {
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignForm = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      // generic
      'click a.radio-inline.clear': 'clearRadioChoices',

      // campaign targets
      'change select#campaign_type':  'changeCampaignType',
      'change select#campaign_subtype':  'changeCampaignType',
      'change input[name="segment_by"]': 'changeSegmentBy',

      // call limit
      'change input[name="call_limit"]': 'changeCallLimit',

      'submit': 'submitForm'
    },

    initialize: function() {
      // init child views
      this.searchForm = new CallPower.Views.TargetSearch();
      this.targetListView = new CallPower.Views.TargetList();

      // clear nested choices until updated by client
      if (!$('select.nested').val()) { $('select.nested').empty(); }

      // trigger change to targeting fields
      // so defaults show properly
      this.changeCampaignType();
      this.changeSegmentBy();

      // load existing items from hidden inputs
      this.targetListView.loadExistingItems();
    },

    changeCampaignType: function() {
      // updates campaign_subtype with available choices from data-attr
      var field = $('select#campaign_type');
      var val = field.val();

      var nested_field = $('select#campaign_subtype');
      var nested_choices = nested_field.data('nested-choices');
      var nested_val = nested_field.val();
      nested_field.empty();

      // fill in new choices from data attr
      // - handle weird obj layout from constants
      var avail = _.find(nested_choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v) {
        var option = $('<option value="'+v[0]+'">'+v[1]+'</option>');
        nested_field.append(option);
      });

      // reset initial choice if still valid
      if (_.contains(_.flatten(avail), nested_val)) {
        nested_field.val(nested_val);
      } else {
        nested_field.val('');
      }

      // hide field if no choices present
      if (avail.length === 0) {
        nested_field.hide();
      } else {
        nested_field.show();
      }

      // special cases

      // congress: show/hide target_ordering values senate_first and house_first
      if ((val === 'congress' && nested_val === 'both') ||
          (val === 'state' && nested_val === 'both')) {
        $('input[name="target_ordering"][value="senate-first"]').parent('label').show();
        $('input[name="target_ordering"][value="house-first"]').parent('label').show();
      } else {
        $('input[name="target_ordering"][value="senate-first"]').parent('label').hide();
        $('input[name="target_ordering"][value="house-first"]').parent('label').hide();
      }

      // state: show/hide campaign_state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search Sunlight');
      }

      // local or custom: no seegment or search, show custom target_set
      if (val === "custom" || val === "local") {
        $('.form-group.segment_by').hide();
        $('#target-search').addClass('invisible');
        
        $('#set-targets').show();
      } else {
        $('.form-group.segment_by').show();
        $('#target-search').removeClass('invisible');

        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is other
        if (segment_by.val() !== 'other') {
          $('#set-targets').hide();
        }
      }
    },

    clearRadioChoices: function(event) {
      var buttons = $(event.target).parent().find('input[type="radio"]');
      buttons.attr('checked',false).trigger('change'); //TODO, debounce this?
    },

    changeSegmentBy: function() {
      var selected = $('input[name="segment_by"]:checked');

      if (selected.val() === 'location') {
        $('.form-group.segment_location').show();
      } else {
        $('.form-group.segment_location').hide();
      }

      if (selected.val() === "other") {
        $('#set-targets').show();
      } else {
        $('#set-targets').hide();
      }
    },

    changeCallLimit: function(event) {
      var callMaxGroup = $('input[name="call_maximum"]').parents('.form-group');
      if ($(event.target).prop('checked')) {
        callMaxGroup.show();
      } else {
        callMaxGroup.hide();
        $('input[name="call_maximum"]').val('');
      }
    },

    validateNestedSelect: function(formGroup) {
      if ($('select.nested:visible').length) {
        return !!$('select.nested option:selected').val();
      } else {
        return true;
      }
    },

    validateState: function(formGroup) {
      var campaignType = $('select#campaign_type').val();
      if (campaignType === "state") {
        return !!$('select[name="campaign_state"] option:selected').val();
      } else {
        return true;
      }
    },

    validateSegmentBy: function(formGroup) {
      // if campaignType is custom or local, segmentBy must equal other
      var campaignType = $('select#campaign_type').val();
      if (campaignType === "custom" || campaignType === "local") {
        var segmentBy = $('input[name="segment_by"]:checked').val();
        if (segmentBy === "other") { return true; }
        else { return false; }
      }
      return true;
    },

    validateTargetList: function(formGroup) {
      // if type == custom, ensure we have targets
      if ($('select#campaign_type').val() === "custom") {
        return !!CallPower.campaignForm.targetListView.collection.length;
      } else {
        return true;
      }
    },

    validateSelected: function(formGroup) {
      return !!$('select option:selected', formGroup).length;
    },

    validateField: function(formGroup, validator, message) {
      // run validator for formGroup
      var isValid = validator(formGroup);

      // put message in last help-block
      $('.help-block', formGroup).last().text((!isValid) ? message : '');

      // toggle error states
      formGroup.parents('fieldset').find('legend').toggleClass('has-error', !isValid);
      formGroup.toggleClass('has-error', !isValid);
      return isValid;
    },


    validateForm: function() {
      var isValid = true;

      // campaign type
      isValid = this.validateField($('.form-group.campaign_type'), this.validateState, 'Select a state') && isValid;
      isValid = this.validateField($('.form-group.campaign_type'), this.validateNestedSelect, 'Select a sub-type') && isValid;

      // campaign targets
      isValid = this.validateField($('.form-group.segment_by'), this.validateSegmentBy, 'Campaign type requires custom targeting') && isValid;
      isValid = this.validateField($('.form-group#set-targets'), this.validateTargetList, 'Add a custom target') && isValid;

      // phone numbers
      isValid = this.validateField($('.form-group.phone_number_set'), this.validateSelected, 'Select a phone number') && isValid;
      
      return isValid;
    },

    submitForm: function(event) {
      event.preventDefault();

      if (this.validateForm()) {
        this.targetListView.serialize();
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();
/*global CallPower, Backbone, createAudioMeter */

/* Code adapted from volume-meter/main.js
* Copyright (c) 2014 Chris Wilson
* Available under the MIT License
*/

(function () {
  CallPower.Views.AudioMeter = Backbone.View.extend({
    el: $('.meter'),

    initialize: function(recorder) {
      this.template = _.template($('#meter-canvas-tmpl').html());

      // bind getUserMedia triggered events to this backbone view
      _.bindAll(this, 'drawLoop');

      this.meter = null;
      this.WIDTH = 500; // default, gets reset on page render
      this.HEIGHT = 30; // match button height
      this.canvasContext = null;
      this.rafID = null;

      // get stream source from audio context
      this.mediaStreamSource = recorder.audioContext.createMediaStreamSource(recorder.stream);
      this.meter = createAudioMeter(recorder.audioContext);
      this.mediaStreamSource.connect(this.meter);
    },

    render: function() {
      this.$el = $('.meter'); // re-bind once element is created

      var html = this.template({WIDTH: this.WIDTH, HEIGHT: this.HEIGHT});
      this.$el.html(html);

      // get canvas context
      this.canvasContext = document.getElementById( "meter" ).getContext("2d");

      // and newly calculated canvas width
      this.WIDTH = $('#meter').width();
      $('#meter').attr('width', this.WIDTH);

      // kick off the visual updating
      this.drawLoop();

      return this;
    },

    drawLoop: function(time) {
      // clear the background
      this.canvasContext.clearRect(0,0,this.WIDTH,this.HEIGHT);

      // check if we're currently clipping
      if (this.meter.checkClipping())
          this.canvasContext.fillStyle = "red";
      else
          this.canvasContext.fillStyle = "green";

      // draw a bar based on the current volume
      this.canvasContext.fillRect(0, 0, this.meter.volume*this.WIDTH*1.4, this.HEIGHT);

      // set up the next visual callback
      this.rafID = window.requestAnimationFrame( this.drawLoop );
    },

    destroy: function() {
      this.meter.shutdown();
      this.undelegateEvents();
      this.$el.removeData().unbind();

      this.remove();
      Backbone.View.prototype.remove.call(this);
    },

  });

})();
/*global CallPower, Backbone, Recorder */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'change select.source': 'setSource',
      'click .nav-tabs': 'switchTab',
      'click .btn-record': 'onRecord',
      'change input[type="file"]': 'chooseFile',
      'blur textarea[name="text_to_speech"]': 'validateTextToSpeech',
      'submit': 'onSave'
    },

    initialize: function() {
      this.template = _.template($('#microphone-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'setup', 'confirmClose', 'destroy', 'getSources', 'streamError', 'connectMeter', 'dataAvailable');
    },

    render: function(modal) {
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);

      this.$el.on('shown.bs.modal', this.setup);
      this.$el.on('hide.bs.modal', this.confirmClose);
      this.$el.on('hidden.bs.modal', this.destroy);
      this.$el.modal('show');

      return this;
    },

    setup: function() {
      if (Recorder && Recorder.isRecordingSupported()) {
        $('.nav-tabs a[href="#record"]', this.$el).tab('show');

        // get available sources (Chrome only)
        if (MediaStreamTrack.getSources !== undefined) {
          MediaStreamTrack.getSources( this.getSources );
        } else {
          this.setSource();
        }
      } else {
        // switch to upload tab
        $('.nav-tabs a[href="#upload"]', this.$el).tab('show');

        // disable record tab
        $('.nav-tabs a[href="#record"]', this.$el).parent('li').addClass('disabled')
          .attr('title','Sorry, recording is not supported in this browser.');
      }

      this.playback = $('audio[name="playback"]', this.$el);
    },

    switchTab: function(event) {
      event.preventDefault();
      // set up tab behavior manually instead of relying on data-toggle
      // because we have multiple modals on the page and IDs could conflict

      var tabID = $(event.target).attr('href');
      var tab = $('.nav-tabs a[href="'+tabID+'"]', this.$el);
      if (!tab.parent('li').hasClass('disabled')) {
        tab.tab('show');
      }
      return true;
    },

    confirmClose: function(event) {
      if (this.recorder && this.recorder.state === 'recording') {
        return false;
      }

      console.log('confirmClose');
      console.log(this.playback.attr('src'));
      console.log(!!this.playback.attr('src'));
      console.log(this.audioBlob);
      console.log(!!this.audioBlob);
      if (!!this.playback.attr('src') && !this.audioBlob) {
        // there is audio in the player, but not stored as a blob
        return confirm('You have recorded unsaved audio. Are you sure you want to close?');
      } else {
        return true;
      }
    },

    destroy: function() {
      if (this.recorder) {
        this.recorder.stop();
        this.meter.destroy();
      }
      this.undelegateEvents();
      this.$el.removeData().unbind();

      this.remove();
      Backbone.View.prototype.remove.call(this);
    },

    streamError: function(e) {
      this.recorder.state = "error";

      var msg = 'Please allow microphone access in the permissions popup.';
      if (window.chrome !== undefined) {
        msg = msg + '<br>You may need to remove this site from your media exceptions at <a href="">chrome://settings/content</a>';
      }
      window.flashMessage(msg, 'warning', true);
    },

    getSources: function(sourceInfos) {
      // fill in source info in selector
      sourceSelect = $('select.source', this.$el);
      sourceSelect.empty();

      for (var i = 0; i !== sourceInfos.length; ++i) {
        var sourceInfo = sourceInfos[i];
        var option = $('<option></option>');
        option.val(sourceInfo.id);
        if (sourceInfo.kind === 'audio') {
          option.text(sourceInfo.label || 'Microphone ' + (sourceSelect.children('option').length + 1));
          sourceSelect.append(option);
        }
      }
      this.setSource();
    },

    setSource: function() {
      var selectedSourceId = $('select.source', this.$el).children('option:selected').val();

      var recorderConfig = {
        bitRate: 8000, // downsample to what Twilio expects
        encoderPath: '/static/dist/js/oggopusEncoder.js',
        streamOptions: {
            mandatory: {
              // disable chrome filters
              googEchoCancellation: false,
              googAutoGainControl: false,
              googNoiseSuppression: false,
              googHighpassFilter: false
            }
        }
      };

      if (selectedSourceId) {
         // set selected source in config
        recorderConfig.streamOptions.optional = [{ sourceId: selectedSourceId }];
      } // if not, uses default

      // create recorder
      this.recorder = new Recorder(recorderConfig);

      // connect events
      this.recorder.addEventListener('streamError', this.streamError);
      this.recorder.addEventListener('streamReady', this.connectMeter);
      this.recorder.addEventListener('dataAvailable', this.dataAvailable);

      // start stream
      this.recorder.initStream();
    },

    connectMeter: function() {
       // connect audio meter
      this.meter = new CallPower.Views.AudioMeter(this.recorder);
      this.meter.render();
    },

    onRecord: function(event) {
      event.preventDefault();

      if (this.recorder.state === 'error') {
        // reset source
        this.setSource();
      }
      else if (this.recorder.state === 'inactive') {
        // start recording
        this.recorder.start();

        // show audio row and recording indicator
        $('.playback').show();
        $('.playback .glyphicon-record').addClass('active').show();

        // button to stop
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-stop');
        $('button.btn-record .text', this.$el).text('Stop');
      }
      else if (this.recorder.state === 'recording') {
        // stop recording
        this.recorder.stop();
        this.recorder.state = 'stopped'; // set custom state, so we know to re-init

        $('.playback .glyphicon-record').removeClass('active').hide();

        // button to reset
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-stop').addClass('glyphicon-step-backward');
        $('button.btn-record .text', this.$el).text('Reset');
      }
      else if (this.recorder.state === 'stopped') {
        // re-init streams
        this.recorder.initStream();
        this.recorder.state = 'inactive';

        // clear playback
        this.playback.attr('controls', false);
        this.playback.attr('src', '');
        $('.playback').hide();

        // button to record
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-step-backward').addClass('glyphicon-record');
        $('button.btn-record .text', this.$el).text('Record');
      }
      else {
        console.error('recorder in invalid state');
      }
    },

    dataAvailable: function(data) {
      console.log('dataAvailable', this);
      this.audioBlob = data.detail;
      this.playback.attr('controls', true);
      this.playback.attr('src',URL.createObjectURL(this.audioBlob));

      // reload media blob when done playing, because Chrome won't do it automatically
      this.playback.on('ended', function() {
        this.load();
      });
    },

    chooseFile: function() {
      this.filename = $('input[type="file"]').val().split(/(\\|\/)/g).pop();
    },

    validateTextToSpeech: function() {
      // TODO, run through simple jinja-like validator
      // provide auto-completion of available context?

      this.textToSpeech = $('textarea[name="text_to_speech"]').val();
    },

    validateField: function(parentGroup, validator, message) {
      // run validator for parentGroup, if present
      if (!parentGroup.length) {
        return true;
      }

      var isValid = validator(parentGroup);
      
      // put message in last help-block
      $('.help-block', parentGroup).last().text((!isValid) ? message : '');

      // toggle error states
      parentGroup.toggleClass('has-error', !isValid);
      return isValid;
    },


    validateForm: function() {
      var isValid = true;
      var self = this;

      if (!$('.tab-pane#record').hasClass('active')) {
        // if we are not on the recording tab, delete the blob
        delete this.audioBlob;
      }

      isValid = this.validateField($('.tab-pane.active#record'), function() {
        return !!self.playback.attr('src');
      }, 'Please record your message') && isValid;

      isValid = this.validateField($('.tab-pane.active#upload'), function() {
        return !!self.filename;
      }, 'Please select a file to upload') && isValid;

      isValid = this.validateField($('.tab-pane.active#text-to-speech'), function() {
        return !!self.textToSpeech;
      }, 'Please enter text to read') && isValid;

      return isValid;
    },

    onSave: function(event) {
      event.preventDefault();

      // submit file via ajax with html5 FormData
      // probably will not work in old IE
      var formData = new FormData();
      
      // add inputs individually, so we can control how we add files
      var formItems = $('form.modal-body', this.$el).find('input[type!="file"], select, textarea');
      _.each(formItems, function(item) {
        var $item = $(item);
        if ($item.val()) {
          formData.append($item.attr('name'), $item.val());
        }
      });
      // create file from blob
      if (this.audioBlob) {
        formData.append('file_storage', this.audioBlob);
      }

      var self = this;
      if (this.validateForm()) {
        $(this.$el).unbind('submit').submit();
        $.ajax($('form.modal-body').attr('action'), {
          method: "POST",
          data: formData,
          processData: false, // stop jQuery from munging our carefully constructed FormData
          contentType: false, // or faffing with the content-type
          success: function(response) {
            // build friendly message like "Audio recording uploaded: Introduction version 3"
            var fieldDescription = $('form label[for="'+response.key+'"]').text();
            var msg = response.message + ': '+fieldDescription + ' version ' + response.version;
            // and display to user
            window.flashMessage(msg, 'success');

            // close the parent modal
            self.$el.modal('hide');
          },
          error: function(xhr, status, error) {
            console.error(status, error);
            window.flashMessage(response.errors, 'error');
          }
        });
        this.delegateEvents(); // re-bind the submit handler
        return true;
      }
      return false;
    },

  });

})();
(function () {
  CallPower.Routers.Campaign = Backbone.Router.extend({
    routes: {
      "campaign/create": "campaignForm",
      "campaign/edit/:id": "campaignForm",
      "campaign/copy/:id": "campaignForm",
      "campaign/audio/:id": "audioForm",
    },

    campaignForm: function(id) {
      CallPower.campaignForm = new CallPower.Views.CampaignForm();
    },

    audioForm: function(id) {
      CallPower.campaignAudioForm = new CallPower.Views.CampaignAudioForm();
    }
  });
})();
/*global CallPower, Backbone */

(function () {
  CallPower.Views.TargetSearch = Backbone.View.extend({
    el: $('div#target-search'),

    events: {
      // target search
      'keydown input[name="target-search"]': 'searchKey',
      'focusout input[name="target-search"]': 'searchTab',
      'click .search': 'doTargetSearch',
      'click .search-results .result': 'selectSearchResult',
      'click .search-results .close': 'closeSearch',
    },

    initialize: function() { },

    searchKey: function(event) {
      if(event.which === 13) { // enter key
        event.preventDefault();
        this.doTargetSearch();
      }
    },

    searchTab: function(event) {
      // TODO, if there's only one result add it
      // otherwise, let iterate through the results and let user select one
    },

    doTargetSearch: function(event) {
      var self = this;
      // search the Sunlight API for the named target
      var query = $('input[name="target-search"]').val();

      var campaign_type = $('select[name="campaign_type"]').val();
      var campaign_state = $('select[name="campaign_state"]').val();
      var chamber = $('select[name="campaign_subtype"]').val();

      if (campaign_type === 'congress') {
        // hit Sunlight OpenCongress v3

        $.ajax({
          url: CallPower.Config.SUNLIGHT_CONGRESS_URL,
          data: {
            apikey: CallPower.Config.SUNLIGHT_API_KEY,
            in_office: true,
            chamber: chamber,
            query: query
          },
          beforeSend: function(jqXHR, settings) { console.log(settings.url); },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }

      if (campaign_type === 'state') {
        // hit Sunlight OpenStates

        // TODO, request state metadata
        // display latest_json_date to user

        $.ajax({
          url: CallPower.Config.SUNLIGHT_STATES_URL,
          data: {
            apikey: CallPower.Config.SUNLIGHT_API_KEY,
            state: campaign_state,
            in_office: true,
            chamber: chamber,
            last_name: query // NB, we can't do generic query for OpenStates, let user select field?
          },
          beforeSend: function(jqXHR, settings) { console.log(settings.url); },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }
    },

    renderSearchResults: function(response) {
      var results;
      if (response.results) {
        results = response.results;
      } else {
        // openstates doesn't paginate
        results = response;
      }

      var dropdownMenu = renderTemplate("#search-results-dropdown-tmpl");
      if (results.length === 0) {
        dropdownMenu.append('<li class="result close"><a>No results</a></li>');
      }

      _.each(results, function(person) {
        // standardize office titles
        if (person.title === 'Sen')  { person.title = 'Senator'; }
        if (person.title === 'Rep')  { person.title = 'Representative'; }

        // render display
        var li = renderTemplate("#search-results-item-tmpl", person);

        // if person has multiple phones, show only the first office
        if (person.phone === undefined && person.offices) {
          if (person.offices) { li.find('span.phone').html(person.offices[0].phone); }
        }
        dropdownMenu.append(li);
      });
      $('.input-group .search-results').append(dropdownMenu);
    },

    errorSearchResults: function(response) {
      // TODO: show bootstrap warning panel
      console.log(response);
    },

    closeSearch: function() {
      var dropdownMenu = $('.search-results .dropdown-menu').remove();
    },

    selectSearchResult: function(event) {
      // pull json data out of data-object attr
      var obj = $(event.target).data('object');
      
      // add it to the targetListView collection
      CallPower.campaignForm.targetListView.collection.add(obj);

      // if only one result, closeSearch
      if ($('.search-results .dropdown-menu').children('.result').length <= 1) {
        this.closeSearch();
      }
    },

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Models.Target = Backbone.Model.extend({
    defaults: {
      id: null,
      title: null,
      name: null,
      number: null,
      order: null
    },

  });

  CallPower.Collections.TargetList = Backbone.Collection.extend({
    model: CallPower.Models.Target,
    comparator: 'order'
  });

  CallPower.Views.TargetItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'list-group-item target',

    initialize: function() {
      this.template = _.template($('#target-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var html = this.template(this.model.toJSON());
      this.$el.attr('id', 'target_set-'+this.model.get('order'));
      this.$el.html(html);
      return this;
    },

    events: {
      'keydown [contenteditable]': 'onEdit',
      'blur [contenteditable]': 'onSave',
      'click .remove': 'onRemove',
    },

    onEdit: function(event) {
      var target = $(event.target);
      var esc = event.which == 27,
          nl = event.which == 13,
          tab = event.which == 9;


      if (esc) {
        document.execCommand('undo');
        target.blur();
      } else if (nl) {
        event.preventDefault(); // stop user from creating multi-line spans
        target.blur();
      } else if (tab) {
        event.preventDefault(); // prevent focus from going back to first field
        target.next('[contenteditable]').focus(); // send it to next editable
      } else if (target.text() === target.attr('placeholder')) {
        target.text(''); // overwrite placeholder text
        target.removeClass('placeholder');
      }
    },

    onSave: function(event) {
      var field = $(event.target);

      if (field.text() === '') {
        // empty, reset to placeholder
        field.text(field.attr('placeholder'));
      }
      if (field.text() === field.attr('placeholder')) {
        field.addClass('placeholder');
        return;
      }

      var fieldName =field.data('field');
      this.model.set(fieldName, field.text());
      field.removeClass('placeholder');
    },

    onRemove: function(event) {
      // clear related inputs
      var sel = 'input[name^="target_set-'+this.model.get('order')+'"]';
      this.$el.remove(sel);

      // and destroy the model
      this.model.destroy();
    },

  });

  CallPower.Views.TargetList = Backbone.View.extend({
    el: '#set-targets',

    initialize: function() {
      this.collection = new CallPower.Collections.TargetList();
      // bind to future render events
      this.listenTo(this.collection, 'add remove sort reset', this.render);

      // make target-list items sortable
      $('.target-list.sortable').sortable({
         items: 'li',
         handle: '.handle',
      }).bind('sortupdate', this.onSortUpdate);
    },

    loadExistingItems: function() {
      // check for items in serialized inputs
      if(this.$el.find('input[name="target_set_length"]').val()) {
        this.deserialize();
        this.recalculateOrder(this);
      }
    },

    render: function() {
      var $list = this.$('ol.target-list').empty().show();

      var rendered_items = [];
      this.collection.each(function(model) {
        var item = new CallPower.Views.TargetItemView({
          model: model,
          attributes: {'data-cid': model.cid}
        });
        var $el = item.render().$el;

        _.each(model.attributes, function(val, key) {
          if (val === null) {
            // set text of $el, without triggering blur
            var sel = 'span[data-field="'+key+'"]';
            var span = $el.children(sel);
            var pl = span.attr('placeholder');
            span.text(pl).addClass('placeholder');
          }
        });

        rendered_items.push($el);
      }, this);
      $list.append(rendered_items);

      var target_set_errors = this.$el.find('input[name^="target_set-"]').filter('[name$="-error"]');
      target_set_errors.each(function(error) {
        var id = $(this).attr('name').replace('-error','');
        var item = $('#'+id);
        item.addClass('error');

        var message = $(this).val();
        item.append('<span class="message">'+message+'</span>');
      });

      $('.target-list.sortable').sortable('update');

      return this;
    },

    serialize: function() {
      // write collection to hidden inputs in format WTForms expects
      var target_set = this.$el.find('#target-set');

      // clear any existing target_set-N inputs
      target_set.find('input').remove('[name^="target_set-"]');

      this.collection.each(function(model, index) {
        // create new hidden inputs named target_set-N-FIELD
        var fields = ['order','title','name','number'];
        _.each(fields, function(field) {
          var input = $('<input name="target_set-'+index+'-'+field+'" type="hidden" />');
          input.val(model.get(field));

          // append to target-set div
          target_set.append(input);
        });
      });
    },

    deserialize: function() {
      // destructive operation, create models from data in inputs
      var self = this;

      // clear rendered targets
      var $list = this.$('ol.target-list').empty();

      // figure out how many items we have
      var target_set_length = this.$el.find('input[name="target_set_length"]').val();

      // iterate over total
      var items = [];
      _(target_set_length).times(function(n) {
        var model = new CallPower.Models.Target();
        var fields = ['order','title','name','number'];
        _.each(fields, function(field) {
          // pull field values out of each input
          var sel = 'input[name="target_set-'+n+'-'+field+'"]';
          var val = self.$el.find(sel).val();
          model.set(field, val);
        });
        items.push(model);
      });
      self.collection.reset(items);
    },

    events: {
      'click .add': 'onAdd',
    },

    onAdd: function() {
      // create new empty item
      var item = this.collection.add({});
      this.recalculateOrder(this);
    },

    onSortUpdate: function() {
      // because this event is bound by jQuery, 'this' is the element, not the parent view
      var view = CallPower.campaignForm.targetListView; // get a reference to it manually
      return view.recalculateOrder(); // pass it to the backbone view
    },

    recalculateOrder: function() {
      var self = this;
      // iterate over DOM objects to set item order
      $('.target-list .list-group-item').each(function(index) {
        var elem = $(this); // in jquery.each, 'this' is the element
        var cid = elem.data('cid');
        var item = self.collection.get(cid);
        if(item) { item.set('order', index); }
      });
    },

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Models.AudioRecording = Backbone.Model.extend({
    defaults: {
      campaign: null,
      key: null,
      description: null,
      version: null
    },

  });

  CallPower.Collections.AudioRecordingList = Backbone.Collection.extend({
    model: CallPower.Models.AudioRecording,
    url: '/api/recording',
    comparator: 'version',
    parse: function(response) {
      return response.objects;
    }
  });

  CallPower.Views.RecordingItemView = Backbone.View.extend({
    tagName: 'tr',

    initialize: function() {
      this.template = _.template($('#recording-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var html = this.template(this.model.toJSON());
      this.$el.html(html);
      return this;
    },

  });

  CallPower.Views.VersionsModal = Backbone.View.extend({
    tagName: 'div',
    className: 'versions modal fade',

    initialize: function() {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });

      this.collection = new CallPower.Collections.AudioRecordingList();
      this.collection.fetch(); // stop trying to make fetch happen
      this.renderCollection();

      this.listenTo(this.collection, 'add remove select', this.renderCollection);
    },

    render: function(modal) {
      console.log('versions view render', modal);
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);
      
      this.$el.modal('show');

      return this;
    },

    renderCollection: function() {
      var $list = this.$('table tbody').empty();

      var rendered_items = [];
      this.collection.each(function(model) {
        var item = new CallPower.Views.RecordingItemView({
          model: model,
        });
        var $el = item.render().$el;

        rendered_items.push($el);
      }, this);
      $list.append(rendered_items);

    },



  });

})();