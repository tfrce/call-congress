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
      _.bindAll(this, 'setup', 'destroy', 'getSources', 'connectRecorder');
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
      this.meter.destroy();
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

      // create and render meter
      this.meter = new CallPower.Views.AudioMeter(selectedSourceId, this.connectRecorder);
      this.meter.render();
    },

    connectRecorder: function(source, audioContext) {
      console.log('connectRecorder callback');
      this.recorder = new Recorder(source, {
        workerPath: '/static/dist/ds/recorderWorker.js'
      });
      this.recorder.recording = false;
      this.audioContext = audioContext;
    },

    onRecord: function() {
      console.log('recorder.recording', this.recorder.recording);
      if (this.recorder.recording) {
        console.log('stop recording');
        
        // stop recording
        this.recorder.stop();
        this.recorder.recording = false;

        // update button to show record
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-stop').addClass('glyphicon-record');
        $('button.record .text', this.$el).text('Record');

      } else {
        console.log('start recording');

        // start recording
        this.recorder.record();
        this.recorder.recording = true;

        // update button to show stop
        $('button.record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-stop');
        $('button.record .text', this.$el).text('Stop');

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
      this.recorder.clear();
    },

    onSave: function() {

    },


  });

})();