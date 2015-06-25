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
      _.bindAll(this, 'setup', 'destroy', 'getSources', 'streamError', 'connectMeter');
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
        monitorGain: 0, // turn it up
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
      this.recorder.addEventListener('streamError', this.streamError);
      this.recorder.addEventListener('streamReady', this.connectMeter);
      this.recorder.initStream();

     
    },

    connectMeter: function() {
       // connect audio meter
      this.meter = new CallPower.Views.AudioMeter(this.recorder);
      this.meter.render();
    },

    onRecord: function() {
      console.log('recorder.state='+this.recorder.state);

      if (this.recorder.state === 'error') {
        console.log('reset source');
        this.setSource();
      } 
      else if (this.recorder.state === 'inactive') {
        console.log('start recording');

        // start recording
        this.recorder.start();

        $('button.record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-pause');
        $('button.record .text', this.$el).text('Pause');
      }
      else if (this.recorder.state === 'recording') {
        console.log('pause recording');
        
        // stop recording
        this.recorder.pause();

        // update button to show record
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-pause').addClass('glyphicon-record');
        $('button.record .text', this.$el).text('Record');
      }
      else if (this.recorder === 'paused') {
        console.log('start recording');

        // start recording
        this.recorder.resume();

        // update button to show pause
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-pause');
        $('button.record .text', this.$el).text('Pause');
      }
      else {
        console.error('recorder in invalid state');
      }
    },

    onPlay: function() {
      var self = this;
      this.recorder.getBuffer(function(buffers) {
        var playbackSource = self.audioContext.createBufferSource();
        var playbackBuffer = self.audioContext.createBuffer( 2, buffers[0].length, self.audioContext.sampleRate );
        playbackBuffer.getChannelData(0).set(buffers[0]);
        playbackBuffer.getChannelData(1).set(buffers[1]);
        playbackSource.buffer = playbackBuffer;

        playbackSource.connect( self.audioContext.destination );
        playbackSource.start(0);
      });

    },

    onReset: function() {
      this.recorder.stop();
    },

    onSave: function() {

    },


  });

})();