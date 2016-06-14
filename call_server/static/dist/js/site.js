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
    if (status === undefined) { var status = 'info'; }
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

    requiredFields: ['msg_intro', 'msg_call_block_intro'],

    initialize: function() {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);
      window.URL = window.URL || window.webkitURL;

      // add required fields client-side
      _.each(this.requiredFields, function(f) {
        $('label[for='+f+']').addClass('required');
      });

      this.campaign_id = $('input[name="campaign_id"]').val();

      $('audio', this.el).on('ended', this.onPlayEnded);
      _.bindAll(this, 'onPlayEnded');
    },

    onRecord: function(event) {
      event.preventDefault();

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    key: inputGroup.prev('label').attr('for'),
                    description: inputGroup.find('.description .help-inline').text(),
                    example_text: inputGroup.find('.description .example-text').text(),
                    campaign_id: this.campaign_id
                  };
      this.microphoneView = new CallPower.Views.MicrophoneModal();
      this.microphoneView.render(modal);
    },

    onPlay: function(event) {
      event.preventDefault();
      
      var button = $(event.target);
      var inputGroup = button.parents('.input-group');
      var key = inputGroup.prev('label').attr('for');
      var playback = button.children('audio');

      var self = this;
      $.getJSON('/api/campaign/'+self.campaign_id,
        function(data) {
          var recording = data.audio_msgs[key];

          if (recording === undefined) {
            button.addClass('disabled');
            return false;
          }
          if (recording.substring(0,4) == 'http') {
            // play file url through <audio> object
            playback.attr('src', data.audio_msgs[key]);
            playback[0].play();
          } else if (CallPower.Config.TWILIO_CAPABILITY) {
            //connect twilio API to read text-to-speech
            twilio = Twilio.Device.setup(CallPower.Config.TWILIO_CAPABILITY, 
              {"rtc": (navigator.getUserMedia !== undefined), "debug":true});
            twilio.connect({'text': recording });
            twilio.disconnect(self.onPlayEnded);
          } else {
            return false;
          }

          button.children('.glyphicon').removeClass('glyphicon-play').addClass('glyphicon-pause');
          button.children('.text').html('Pause');
        }
      );
    },

    onPlayEnded: function(event) {
      var button = $(event.target).parents('.btn');
      button.children('.glyphicon').removeClass('glyphicon-pause').addClass('glyphicon-play');
      button.children('.text').html('Play');
    },

    onVersion: function(event) {
      event.preventDefault();

      var inputGroup = $(event.target).parents('.input-group');
      var modal = {
        name: inputGroup.prev('label').text(),
        key: inputGroup.prev('label').attr('for'),
        campaign_id: this.campaign_id
      };
      this.versionsView = new CallPower.Views.VersionsModal(modal);
      this.versionsView.render();
    },

    validateForm: function() {
      var isValid = true;

      // check required fields for valid class
      _.each(this.requiredFields, function(f) {
        var formGroup = $('.form-group.'+f);
        var fieldValid = formGroup.hasClass('valid');
        if (!fieldValid) {
          formGroup.find('.input-group .help-block')
            .text('This field is required.')
            .addClass('error');
        }
        isValid = isValid && fieldValid;
      });

      // call validators
      
      return isValid;
    },

    submitForm: function(event) {
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
    CallPower.Models.Call = Backbone.Model.extend({
    defaults: {
      id: null,
      timestamp: null,
      campaign_id: null,
      target_id: null,
      call_id: null,
      status: null,
      duration: null
    },
  });


  CallPower.Collections.CallList = Backbone.Collection.extend({
    model: CallPower.Models.Call,
    url: '/api/call',

    initialize: function(campaign_id) {
      this.campaign_id = campaign_id;
    },

    parse: function(response) {
      return response.objects;
    },

    fetch: function(options) {
      // transform filters to flask-restless style
      // always include campaign_id filter
      var filters = [{name: 'campaign_id', op: 'eq', val: this.campaign_id}];
      if (options.filters) {
        Array.prototype.push.apply(filters, options.filters);
      }
      var flaskQuery = {
        q: JSON.stringify({ filters: filters })
      };

      var fetchOptions = _.extend({ data: flaskQuery }, options);
      return Backbone.Collection.prototype.fetch.call(this, fetchOptions);
    }
  });

  CallPower.Views.CallItemView = Backbone.View.extend({
    tagName: 'tr',

    initialize: function() {
      this.template = _.template($('#call-log-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var data = this.model.toJSON();
      var html = this.template(data);
      this.$el.html(html);
      return this;
    },
  });

  CallPower.Views.CallLog = Backbone.View.extend({
    el: $('#call_log'),

    events: {
      'change .filters input': 'updateFilters',
      'change .filters select': 'updateFilters',
    },


    initialize: function(campaign_id) {
      this.collection = new CallPower.Collections.CallList(campaign_id);
      this.listenTo(this.collection, 'reset add remove', this.renderCollection);
      this.views = [];

      this.$el.find('.input-daterange input').each(function (){
        $(this).datepicker({
          'format': "yyyy/mm/dd",
          'orientation': 'top',
        });
      });

      this.updateFilters();
    },

    updateFilters: function(event) {
      var status = $('select[name="status"]').val();
      var start = new Date($('input[name="start"]').datepicker('getDate'));
      var end = new Date($('input[name="end"]').datepicker('getDate'));

      if (start > end) {
        $('.input-daterange input[name="start"]').addClass('error');
        return false;
      } else {
        $('.input-daterange input').removeClass('error');
      }

      var filters = [];
      if (status) {
        filters.push({'name': 'status', 'op': 'eq', 'val': status});
      }
      if (start) {
        filters.push({'name': 'timestamp', 'op': 'gt', 'val': start.toISOString()});
      }
      if (end) {
        filters.push({'name': 'timestamp', 'op': 'lt', 'val': end.toISOString()});
      }

      this.collection.fetch({filters: filters});
    },

    renderCollection: function() {
      var self = this;

      // clear any existing subviews
      this.destroyViews();
      var $list = this.$('table tbody').empty();

      // create subviews for each item in collection
      this.views = this.collection.map(this.createItemView, this);
      $list.append( _.map(this.views,
        function(view) { return view.render(self.campaign_id).el; },
        this)
      );

      var renderedItems = this.$('table tbody tr');
      if (renderedItems.length === 0) {
        this.$('table tbody').html('<p>No results. Try adjusting filters.</p>');
      }
    },

    destroyViews: function() {
      // destroy each subview
      _.invoke(this.views, 'destroy');
      this.views.length = 0;
    },

    createItemView: function (model) {
      return new CallPower.Views.CallItemView({ model: model });
    },

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignForm = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      // generic
      'click a.clear': 'clearRadioChoices',

      // campaign targets
      'change select#campaign_type':  'changeCampaignType',
      'change select#campaign_subtype':  'changeCampaignSubtype',
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

      if ($('input[name="call_maximum"]').val()) {
        $('input[name="call_limit"]').attr('checked', 'checked');
      }

      // load existing items from hidden inputs
      this.targetListView.loadExistingItems();
    },

    changeCampaignType: function() {
      // updates campaign_subtype with available choices from data-attr
      var field = $('select#campaign_type');
      var val = field.val();

      var nested_field = $('select#campaign_subtype');
      var nested_choices = nested_field.data('nested-choices');
      var nested_val = nested_field.data('nested-selected');
      nested_field.empty();

      // fill in new choices from data attr
      // - handle weird obj layout from constants
      var avail = _.find(nested_choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v) {
        var option = $('<option value="'+v[0]+'">'+v[1]+'</option>');
        nested_field.append(option);
      });
      var nested_avail = _.find(avail, function(v) { return v[0] === nested_val; });

      // reset initial choice if still valid
      if (nested_avail) {
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

      // state: show/hide campaign_state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search Sunlight');
      }

      // local or custom: no segment, location or search, show custom target_set
      if (val === "custom" || val === "local" || val === "executive") {
        // set default values
        $('.form-group.locate_by input[name="locate_by"][value=""]').click();
        $('.form-group.segment_by input[name="segment_by"][value="custom"]').click();
        // hide fields
        $('.form-group.segment_by').hide();
        $('.form-group.locate_by').hide();
        $('#target-search').hide();
        // show custom target search
        $('#set-targets').show();
      } else {
        $('.form-group.segment_by').show();
        $('.form-group.locate_by').show();
        $('#target-search').show();

        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is custom
        if (segment_by.val() !== 'custom') {
          $('#set-targets').hide();
        }
      }

      this.changeCampaignSubtype();
    },

    changeCampaignSubtype: function(event) {
      var type = $('select#campaign_type').val();
      var subtype = $('select#campaign_subtype').val();

      // congress: show/hide target_ordering values upper_first and lower_first
      if ((type === 'congress' && subtype === 'both') ||
          (type === 'state' && subtype === 'both')) {
        $('input[name="target_ordering"][value="upper-first"]').parent('label').show();
        $('input[name="target_ordering"][value="lower-first"]').parent('label').show();
      } else {
        $('input[name="target_ordering"][value="upper-first"]').parent('label').hide();
        $('input[name="target_ordering"][value="lower-first"]').parent('label').hide();
      }

    },

    clearRadioChoices: function(event) {
      var buttons = $(event.target).parent().find('input[type="radio"]');
      buttons.attr('checked',false).trigger('change'); //TODO, debounce this?
    },

    changeSegmentBy: function() {
      var selected = $('input[name="segment_by"]:checked');

      if (selected.val() === 'location') {
        $('.form-group.locate_by').show();
      } else {
        $('.form-group.locate_by').hide();
      }

      if (selected.val() === 'custom') {
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
      var campaignSubtype = $('select#campaign_subtype').val();
      if (campaignType === "state") {
        if (campaignSubtype === "exec") {
          // governor campaigns can cross states
          return true;
        } else {
          // other types require a state to be selected
          return !!$('select[name="campaign_state"] option:selected').val();
        }
      } else {
        return true;
      }
    },

    validateSegmentBy: function(formGroup) {
      // if campaignType is custom or local, set segmentBy to custom and uncheck locate_by
      var campaignType = $('select#campaign_type').val();
      if (campaignType === "custom" || campaignType === "local") {
        $('input[name="segment_by"][value="custom"]').click();
        $('input[name="locate_by"]').attr('checked', false);
      }
      return true;
    },

    validateLocateBy: function(formGroup) {
      // if segmentBy is location, locateBy must have value
      var segmentBy = $('input[name="segment_by"]:checked').val();
      if (segmentBy === "location") {
        return !!$('input[name="locate_by"]:checked').val();
      } else {
        return true;
      }
    },

    validateTargetList: function(f) {
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

      // campaign segmentation
      isValid = this.validateField($('.form-group.segment_by'), this.validateSegmentBy, 'Campaign type requires custom targeting') && isValid;
      isValid = this.validateField($('.form-group.locate_by'), this.validateLocateBy, 'Please pick a location attribute') && isValid;
      
      // campaign targets
      isValid = this.validateField($('.form-group#set-targets'), this.validateTargetList, 'Add a custom target') && isValid;

      // phone numbers
      isValid = this.validateField($('.form-group.phone_number_set'), this.validateSelected, 'Select a phone number') && isValid;
      
      return isValid;
    },

    submitForm: function(event) {
      if (this.validateForm()) {
        this.targetListView.serialize();
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignLaunchForm = Backbone.View.extend({
    el: $('#launch'),

    events: {
      'click .test-call': 'makeTestCall',
      'change #embed_type': 'toggleCustomEmbedPanel',
      'blur #custom_embed_options input': 'updateEmbedCode',
    },

    initialize: function() {
      this.campaignId = $('#campaignId').val();
      $('.readonly').attr('readonly', 'readonly');
      this.toggleCustomEmbedPanel();
    },

    makeTestCall: function(event) {
      var statusIcon = $(event.target).next('.glyphicon');
      statusIcon.removeClass('error').addClass('glyphicon-earphone');
      if (window.location.hostname === 'localhost') {
        alert("Call Power cannot place test calls unless hosted on an externally routable address. Try using ngrok and restarting with the --server option.");
        $(event.target).addClass('disabled');
        statusIcon.addClass('error');
        return false;
      }

      statusIcon.addClass('active');

      var phone = $('#test_call_number').val();
      phone = phone.replace(/\s/g, '').replace(/\(/g, '').replace(/\)/g, ''); // remove spaces, parens
      phone = phone.replace("+", "").replace(/\-/g, ''); // remove plus, dash

      var location = $('#test_call_location').val();

      $.ajax({
        url: '/call/create',
        data: {campaignId: this.campaignId, userPhone: phone, userLocation: location},
        success: function(data) {
          console.log(data);
          alert('Calling you at '+$('#test_call_number').val()+' now!');
          if (data.message == 'queued') {
            statusIcon.removeClass('active').addClass('success');
          } else {
            console.error(data.message);
            statusIcon.addClass('error');
          }
        },
        error: function(err) {
          console.error(err);
        }
      });
    },

    toggleCustomEmbedPanel: function(event) {
      var formType = $('#embed_type').val();
      if (formType) {
        $('.form-group.embed_code').removeClass('hidden');
      } else {
        $('.form-group.embed_code').addClass('hidden');
      }

      if (formType === 'custom' || formType === 'iframe') {
        $('#custom_embed_options').collapse('show');
      } else {
        $('#custom_embed_options').collapse('hide');
      }
      if (formType === 'iframe') {
        $('#custom_embed_options h3').text('iFrame Embed Options');
        $('#custom_embed_options .form-group').hide().filter('.iframe').show();
      } else {
        $('#custom_embed_options h3').text('Custom Embed Options');
        $('#custom_embed_options .form-group').show();
      }
      this.updateEmbedCode();
    },

    updateEmbedCode: function(event) {
      $.ajax({
        url: '/api/campaign/'+this.campaignId+'/embed_code.html',
        data: {
          'embed_type': $('#embed_type').val(),
          'embed_form_sel': $('#embed_form_sel').val(),
          'embed_phone_sel': $('#embed_phone_sel').val(),
          'embed_location_sel': $('#embed_location_sel').val(),
          'embed_custom_css': $('#embed_custom_css').val(),
          'embed_custom_js': $('#embed_custom_js').val(),
          'embed_script_display': $('#embed_script_display').val(),
        },
        success: function(html) {
          $('textarea#embed_code').val(html);
        }
      });
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
      this.mediaStreamSource = recorder.source;
      this.meter = createAudioMeter(recorder.context);
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
/*global CallPower, Backbone, audioRecorder */

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
      _.bindAll(this, 'setup', 'confirmClose', 'destroy', 'getSources', 'streamError', 'connectRecorder', 'dataAvailable');
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
      if (this.isRecordingSupported()) {
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

    isRecordingSupported: function() {
      return !!(navigator.getUserMedia || navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia || navigator.msGetUserMedia);
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

      if (!!this.playback.attr('src') && !this.saved) {
        // there is audio in the player, but not yet saved
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

      var mediaConstraints = { audio: {
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
        mediaConstraints.audio.optional = [{ sourceId: selectedSourceId }];
      } // if not, uses default

      navigator.getUserMedia(mediaConstraints, this.connectRecorder, this.streamError);
    },

    connectRecorder: function(stream) {
      var audioContext = new AudioContext;
      var source = audioContext.createMediaStreamSource(stream);

      var recorderConfig = {
        workerPath: '/static/dist/js/lib/recorderWorker.js',
        mp3LibPath: '/static/dist/js/lib/lame.all.js',
        vorbisLibPath: '/static/dist/js/lib/lame.all.js', // not really, but we only want mp3 recording
        // reuse exisiting path to avoid double downloading large emscripten compiled js
        recordAsMP3: true,
        bitRate: 8,

      };
      this.recorder  = audioRecorder.fromSource(source, recorderConfig);
      this.recorder.context = audioContext;
      this.recorder.source = source;
      this.recorder.state = 'inactive';

       // connect audio meter
      this.meter = new CallPower.Views.AudioMeter(this.recorder);
      this.meter.render();
    },

    onRecord: function(event) {
      event.preventDefault();

       // track custom state beyond what audioRecord.js provides

      if (this.recorder.state === 'error') {
        // reset source
        this.setSource();
      }
      else if (this.recorder.state === 'inactive') {
        // start recording
        this.recorder.record();
        this.recorder.state = 'recording';

        // show audio row and recording indicator
        $('.playback').show();
        $('.playback .status').addClass('active').show();

        // button to stop
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-stop');
        $('button.btn-record .text', this.$el).text('Stop');
      }
      else if (this.recorder.state === 'recording' || this.recorder.recording) {
        // stop recording
        this.recorder.stop();
        this.recorder.state = 'stopped';
        this.recorder.exportMP3(this.dataAvailable);

        $('.playback .status').removeClass('active').hide();

        // button to reset
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-stop').addClass('glyphicon-step-backward');
        $('button.btn-record .text', this.$el).text('Reset');
      }
      else if (this.recorder.state === 'stopped') {
        // clear buffers and restart
        this.recorder.clear();
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
      console.log('dataAvailable', this, data);
      this.audioBlob = data;
      this.playback.attr('controls', true);
      this.playback.attr('src',URL.createObjectURL(this.audioBlob));

      // reload media blob when done playing, because Chrome won't do it automatically
      this.playback.on('ended', function() {
        this.load();
      });
    },

    chooseFile: function() {
      this.filename = $('input[type="file"]').val().split(/(\\|\/)/g).pop();
      $('span.filename').text(this.filename);
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

      // change save button to spinner
      $('.btn.save .glyphicon')
        .removeClass('glyphicon-circle-arrow-down')
        .addClass('glyphicon-refresh')
        .addClass('glyphicon-spin');

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
      } else if (this.filename) {
        formData.append('file_storage', $('input[type="file"]')[0].files[0]);
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
            if (response.success) {
              // build friendly message like "Audio recording uploaded: Introduction version 3"
              var fieldDescription = $('form label[for="'+response.key+'"]').text();
              var msg = response.message + ': '+fieldDescription + ' version ' + response.version;
              // and display to user
              window.flashMessage(msg, 'success');

              // update parent form-group status and description
              var parentFormGroup = $('.form-group.'+response.key);
              parentFormGroup.addClass('valid');
              parentFormGroup.find('.input-group .help-block').text('');
              parentFormGroup.find('.description .status').addClass('glyphicon-check');

              // close the parent modal
              self.saved = true;
              self.$el.modal('hide');
            } else {
              console.error(response);
              window.flashMessage(response.errors, 'error', true);
            }
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
      "campaign/:id/edit": "campaignForm",
      "campaign/:id/copy": "campaignForm",
      "campaign/:id/audio": "audioForm",
      "campaign/:id/launch": "launchForm",
      "campaign/:id/calls": "callLog",
      "system": "systemForm",
      "statistics": "statisticsView",
    },

    campaignForm: function(id) {
      CallPower.campaignForm = new CallPower.Views.CampaignForm();
    },

    audioForm: function(id) {
      CallPower.campaignAudioForm = new CallPower.Views.CampaignAudioForm();
    },

    launchForm: function(id) {
      CallPower.campaignLaunchForm = new CallPower.Views.CampaignLaunchForm();
    },

    callLog: function(id) {
      CallPower.callLog = new CallPower.Views.CallLog(id);
    },

    systemForm: function() {
      CallPower.systemForm = new CallPower.Views.SystemForm();
    },

    statisticsView: function() {
      CallPower.statisticsView = new CallPower.Views.StatisticsView();
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
      // otherwise, let user select one
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

        //convert generic chamber names to House / Senate
        if (chamber === 'lower') {
          chamber = 'house';
        }
        if (chamber === 'upper') {
          chamber = 'senate';
        }
        if (chamber === 'both') {
          chamber = '';
        }

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

        person.uid = 'us:bioguide:'+person.bioguide_id;

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
  CallPower.Views.StatisticsView = Backbone.View.extend({
    el: $('#statistics'),
    campaignId: null,

    events: {
      'change select[name="campaigns"]': 'changeCampaign',
      'change select[name="timespan"]': 'renderChart',
    },

    initialize: function() {
      this.$el.find('.input-daterange input').each(function (){
        $(this).datepicker({
          'format': "yyyy/mm/dd"
        });
      });

      _.bindAll(this, 'renderChart');
      this.$el.on('changeDate', _.debounce(this.renderChart, this));

      this.chartOpts = {
        stacked: true,
        discrete: true,
        library: {
          canvasDimensions:{ height:250},
          xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e. %b'
            }
          },
          yAxis: { allowDecimals: false, min: null },
        }
      };
      this.campaignDataTemplate = _.template($('#campaign-data-tmpl').html(), { 'variable': 'data' });
      this.targetDataTemplate = _.template($('#target-data-tmpl').html(), { 'variable': 'targets'});
    },

    changeCampaign: function(event) {
      var self = this;

      this.campaignId = $('select[name="campaigns"]').val();
      $.getJSON('/api/campaign/'+this.campaignId+'/stats.json',
        function(data) {
          if (data.sessions_completed && data.sessions_started) {
            var conversion_rate = (data.sessions_completed / data.sessions_started);
            conversion_pct = Number((conversion_rate*100).toFixed(2));
            data.conversion_rate = (conversion_pct+"%");
          } else {
            data.conversion_rate = 'n/a';
          }
          if (!data.sessions_completed) {
            data.calls_per_session = 'n/a';
          }
          $('#campaign_data').html(
            self.campaignDataTemplate(data)
          ).show();

          if (data.date_start && data.date_end) {
            $('input[name="start"]').datepicker('setDate', data.date_start);
            $('input[name="end"]').datepicker('setDate', data.date_end);
          }
          self.renderChart();
        });
    },

    renderChart: function(event) {
      var self = this;

      if (!this.campaignId) {
        return false;
      }

      var timespan = $('select[name="timespan"]').val();
      var start = new Date($('input[name="start"]').datepicker('getDate')).toISOString();
      var end = new Date($('input[name="end"]').datepicker('getDate')).toISOString();

      if (start > end) {
        $('.input-daterange input[name="start"]').addClass('error');
        return false;
      } else {
        $('.input-daterange input').removeClass('error');
      }

      var chartDataUrl = '/api/campaign/'+this.campaignId+'/date_calls.json?timespan='+timespan;
      if (start) {
        chartDataUrl += ('&start='+start);
      }
      if (end) {
        chartDataUrl += ('&end='+end);
      }

      $('#calls_for_campaign').html('loading');
      $.getJSON(chartDataUrl, function(data) {
        // api data is by date, map to series by status
        var DISPLAY_STATUS = ['completed', 'busy', 'failed', 'no-answer', 'canceled', 'unknown'];
        series = _.map(DISPLAY_STATUS, function(status) { 
          var s = _.map(data, function(value, date) {
            return [date, value[status]];
          });
          return {'name': status, 'data': s };
        });
        self.chart = new Chartkick.ColumnChart('calls_for_campaign', series, self.chartOpts);
      });

      var tableDataUrl = '/api/campaign/'+this.campaignId+'/target_calls.json?';
      if (start) {
        tableDataUrl += ('&start='+start);
      }
      if (end) {
        tableDataUrl += ('&end='+end);
      }

      $('table#target_data').html('loading');
      $.getJSON(tableDataUrl, function(data) {
        var content = self.targetDataTemplate(data);
        $('table#target_data').html(content);
        $('#target_counts').show();
      });
    }

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Views.SystemForm = Backbone.View.extend({
    el: $('#system'),

    events: {
      'click .reveal': 'toggleSecret',
    },

    toggleSecret: function(event) {
      var input = $(event.target).parent().siblings('input');
        if (input.prop('type') === 'password') {
            input.prop('type','text');
        } else {
            input.prop('type','password');
        }
    }

  });

})();
/*global CallPower, Backbone */

(function () {
  CallPower.Models.Target = Backbone.Model.extend({
    defaults: {
      id: null,
      uid: null,
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

    events: {
      'click .add': 'onAdd',
    },

    initialize: function() {
      this.collection = new CallPower.Collections.TargetList();
      // bind to future render events
      this.listenTo(this.collection, 'add remove sort reset', this.render);
      this.listenTo(this.collection, 'add', this.recalculateOrder);

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
        var fields = ['order','title','name','number','uid'];
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
        var fields = ['order','title','name','number','uid'];
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

    shortRandomString: function(prefix, length) {
      // generate a random string, with optional prefix
      // should be good enough for use as uid
      if (length === undefined) { length = 6; }
      var randstr = ((Math.random()*Math.pow(36,length) << 0).toString(36)).slice(-1*length);
      if (prefix !== undefined) { return prefix+randstr; }
      return randstr;
    },

    onAdd: function() {
      // create new empty item
      var item = this.collection.add({
        uid: this.shortRandomString('custom:', 6)
      });
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
      id: null,
      key: null,
      description: null,
      version: null,
      hidden: null,
      campaign_ids: null,
      selected_campaign_ids: null,
      file_url: null,
      text_to_speech: null
    },

  });

  CallPower.Collections.AudioRecordingList = Backbone.Collection.extend({
    model: CallPower.Models.AudioRecording,
    url: '/api/audiorecording',
    comparator: 'version',

    initialize: function(key, campaign_id) {
      this.key = key;
      this.campaign_id = campaign_id;
    },

    parse: function(response) {
      return response.objects;
    },

    fetch: function(options) {
      // do specific pre-processing for server-side filters
      // always filter on AudioRecording key
      var keyFilter = [{name: 'key', op: 'eq', val: this.key}];
      var flaskQuery = {
        q: JSON.stringify({ filters: keyFilter })
      };
      var fetchOptions = _.extend({ data: flaskQuery }, options);

      return Backbone.Collection.prototype.fetch.call(this, fetchOptions);
    }
  });

  CallPower.Views.RecordingItemView = Backbone.View.extend({
    tagName: 'tr',

    events: {
      'click button.select': 'onSelect',
      'click button.delete': 'onDelete',
      'click button.undelete': 'onUnDelete',
      'mouseenter button.select': 'toggleSuccess',
      'mouseleave button.select': 'toggleSuccess',
      'mouseenter button.delete': 'toggleDanger',
      'mouseleave button.delete': 'toggleDanger',
      'mouseenter button.undelete': 'toggleWarning',
      'mouseleave button.undelete': 'toggleWarning',
    },

    initialize: function() {
      this.template = _.template($('#recording-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var data = this.model.toJSON();
      data.campaign_id = parseInt(this.model.collection.campaign_id);
      var html = this.template(data);
      this.$el.html(html);
      return this;
    },

    toggleSuccess: function(event) {
      $(event.target).toggleClass('btn-success');
    },

    toggleDanger: function(event) {
      $(event.target).toggleClass('btn-danger');
    },

    toggleWarning: function(event) {
      $(event.target).toggleClass('btn-warning');
    },

    onSelect: function(event) {
      this.model.collection.trigger('select', this.model.attributes);
    },

    onDelete: function(event) {
      this.model.collection.trigger('delete', this.model.attributes);
    },

    onUnDelete: function(event) {
      this.model.collection.trigger('undelete', this.model.attributes);
    },

  });

  CallPower.Views.VersionsModal = Backbone.View.extend({
    tagName: 'div',
    className: 'versions modal fade',

    events: {
      'change input.filter': 'onFilterCampaigns'
    },

    initialize: function(viewData) {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'destroyViews');

      this.viewData = viewData;
      this.collection = new CallPower.Collections.AudioRecordingList(this.viewData.key, this.viewData.campaign_id);
      this.filteredCollection = new FilteredCollection(this.collection);
      this.collection.fetch({ reset: true });
      this.views = [];

      this.listenTo(this.collection, 'reset add remove', this.renderFilteredCollection);
      this.listenTo(this.filteredCollection, 'filtered:reset filtered:add filtered:remove', this.renderFilteredCollection);
      this.listenTo(this.collection, 'select', this.selectVersion);
      this.listenTo(this.collection, 'delete', this.deleteVersion);
      this.listenTo(this.collection, 'undelete', this.unDeleteVersion);

      this.$el.on('hidden.bs.modal', this.destroyViews);
    },

    render: function() {
      // render template
      var html = this.template(this.viewData);
      this.$el.html(html);

      // reset initial filters
      this.onFilterCampaigns();

      // show the modal
      this.$el.modal('show');

      return this;
    },

    renderFilteredCollection: function() {
      var self = this;

      // clear any existing subviews
      this.destroyViews();
      var $list = this.$('table tbody').empty();

      // create subviews for each item in collection
      this.views = this.filteredCollection.map(this.createItemView, this);
      $list.append( _.map(this.views,
        function(view) { return view.render(self.campaign_id).el; },
        this)
      );
    },

    destroyViews: function() {
      // destroy each subview
      _.invoke(this.views, 'destroy');
      this.views.length = 0;
    },

    hide: function() {
      this.$el.modal('hide');
    },

    createItemView: function (model) {
      return new CallPower.Views.RecordingItemView({ model: model });
    },

    onFilterCampaigns: function() {
      var self = this;

      var showAllCampaigns = ($('input.filter[name=show_all_campaigns]:checked', this.$el).length > 0);
      var showHidden = ($('input.filter[name=show_hidden]:checked', this.$el).length > 0);

      if (showAllCampaigns) {
        this.filteredCollection.removeFilter('campaign_id');
      } else {
        this.filteredCollection.filterBy('campaign_id', function(model) {
          return _.contains(model.get('campaign_ids'), parseInt(self.viewData.campaign_id));
        });
      }
      if (showHidden) {
        this.filteredCollection.removeFilter('hidden');
      } else {
        this.filteredCollection.filterBy('hidden', function(model) {
          return (model.get('hidden') !== true); // show only those not hidden
        });
      }
    },

    ajaxPost: function(data, endpoint, hideOnComplete) {
      // make ajax POST to API
      var url = '/admin/campaign/'+this.viewData.campaign_id+'/audio/'+data.id+'/'+endpoint;
      var self = this;
      $.ajax({
        url: url,
        method: 'POST',
        success: function(response) {
          if (response.success) {
              // build friendly message like "Audio recording selected: Introduction version 3"
              var fieldDescription = $('form label[for="'+response.key+'"]').text();
              var msg = response.message + ': '+ fieldDescription + ' version ' + response.version;
              // and display to user
              window.flashMessage(msg, 'success');

              // close the modal, and cleanup subviews
              if (hideOnComplete) {
                self.hide();
              }
            } else {
              console.error(response);
              window.flashMessage(response.errors, 'error', true);
            }
        }, error: function(xhr, status, error) {
          console.error(status, error);
          window.flashMessage(response.errors, 'error');
        }
      });
    },

    selectVersion: function(data) {
      return this.ajaxPost(data, 'select', true);
    },

    deleteVersion: function(data) {
      // TODO, confirm with user
      // this doesn't actually delete objects in database or on file system
      // just hides from API

      return this.ajaxPost(data, 'hide');
    },

    unDeleteVersion: function(data) {
      return this.ajaxPost(data, 'show');
    }

  });
})();