/*global CallPower, Backbone, Recorder */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'change select.source': 'setSource',
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .reset': 'onReset',
      'submit': 'onSave'
    },

    initialize: function() {
      this.template = _.template($('#microphone-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'setup', 'destroy', 'getSources', 'streamError', 'connectMeter', 'dataAvailable');
    },

    render: function(modal) {
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);

      this.$el.on('shown.bs.modal', this.setup);
      this.$el.on('hidden.bs.modal', this.destroy);
      this.$el.modal('show');

      return this;
    },

    setup: function() {
      // get available sources (Chrome only)
      if (MediaStreamTrack.getSources !== undefined) {
        MediaStreamTrack.getSources( this.getSources );
      } else {
        this.setSource();
      }

      this.playback = $('audio.playback', this.$el);
    },

    destroy: function() {
      this.recorder.stop();
      this.meter.destroy();
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

    onRecord: function() {
      if (this.recorder.state === 'error') {
        // reset source
        this.setSource();
      }
      else if (this.recorder.state === 'inactive') {
        // start recording
        this.recorder.start();

        // button to stop
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-stop');
        $('button.record .text', this.$el).text('Stop');
      }
      else if (this.recorder.state === 'recording') {
        // stop recording
        this.recorder.stop();
        this.recorder.state = 'stopped'; // set custom state, so we know to re-init

        // button to reset
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-stop').addClass('glyphicon-step-backward');
        $('button.record .text', this.$el).text('Reset');
      }
      else if (this.recorder.state === 'stopped') {
        // re-init streams
        this.recorder.initStream();
        this.recorder.state = 'inactive';

        // clear playback
        this.playback.attr('controls', false);
        this.playback.attr('src', '');

        // button to record
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-step-backward').addClass('glyphicon-record');
        $('button.record .text', this.$el).text('Record');
      }
      else {
        console.error('recorder in invalid state');
      }
    },

    dataAvailable: function(data) {
      this.audioBlob = data.detail;
      this.playback.attr('controls', true);
      this.playback.attr('src',URL.createObjectURL(this.audioBlob));

      // reload media blob when done playing
      this.playback.on('ended', function() {
        this.load();
      });
    },

    onSave: function() {
      // save blob to parent form as file

    },


  });

})();