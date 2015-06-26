/*global CallPower, Backbone, Recorder */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'change select.source': 'setSource',
      'click .nav-tabs': 'switchTab',
      'click .btn-record': 'onRecord',
      'click .btn-file': 'onFile',
      'click .btn-text-to-speech': 'toggleText',
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
      var tab = $('.nav-tabs a[href="'+tabID+'"]', this.$el)
      if (!tab.parent('li').hasClass('disabled')) {
        tab.tab('show');
      }
      return true;
    },

    confirmClose: function(event) {
      if (this.recorder && this.recorder.state === 'recording') {
        return false;
      }

      if (this.playback.attr('src')) {
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
    },

    streamError: function(e) {
      this.recorder.state = "error";

      var msg = 'Please allow microphone access in the permissions popup.';
      if (window.chrome !== undefined) {
        msg = msg + '<br>You may need to remove this site from your media exceptions at <a href="">chrome://settings/content</a>';
      }
      var flash = $('<div class="alert alert-warning">'+
                    '<button type="button" class="close" data-dismiss="alert">×</button>'+
                    msg+'</div>');
      $('#global_message_container').empty().append(flash).show();
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
      this.audioBlob = data.detail;
      this.playback.attr('controls', true);
      this.playback.attr('src',URL.createObjectURL(this.audioBlob));

      // reload media blob when done playing, because Chrome won't do it automatically
      this.playback.on('ended', function() {
        this.load();
      });
    },

    validateForm: function() {
      var isValid = true;

      // require either recording, file upload selected, or text-to-speech entered
      isValid = isValid && (this.playback.attr('src'))
      
      return isValid;
    },

    onSave: function(event) {
      event.preventDefault();

      // save blob to parent form as file


      if (this.validateForm()) {
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    },

  });

})();