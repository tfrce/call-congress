/*global CallPower, Backbone, createAudioMeter */

/* Code adapted from volume-meter/main.js
* Copyright (c) 2014 Chris Wilson
* Available under the MIT License
*/

(function () {
  CallPower.Views.AudioMeter = Backbone.View.extend({
    el: $('.meter'),

    initialize: function(sourceId) {
      this.template = _.template($('#meter-canvas-tmpl').html());

      // bind getUserMedia triggered events to this backbone view
      _.bindAll(this, 'createMeterFromStream', 'drawLoop');

      this.mediaStreamSource = null;
      this.audioContext = null;
      this.meter = null;
      this.WIDTH = 500; //default, gets reset on page render
      this.HEIGHT = 25;
      this.canvasContext = null;
      this.rafID = null;

      // suppress chrome audio filters, which can cause feedback
      this.filters = {
        "audio": {
              "mandatory": {
                  "googEchoCancellation": "false",
                  "googAutoGainControl": "false",
                  "googNoiseSuppression": "false",
                  "googHighpassFilter": "false"
              },
        }
      };

      if (sourceId) {
        this.filters["audio"]["optional"] = [{ "sourceId": sourceId }];
      }
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

      // connect meter to stream
      navigator.getUserMedia(this.filters, this.createMeterFromStream, this.streamError);

      return this;
    },

    destroy: function() {
      this.undelegateEvents();
      this.$el.removeData().unbind();

      this.remove();
      Backbone.View.prototype.remove.call(this);
    },

    createMeterFromStream: function(stream) {
      // get audio context
      window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext;
      this.audioContext = new AudioContext();

      // create an AudioNode from the stream
      this.mediaStreamSource = this.audioContext.createMediaStreamSource(stream);

      // create a new volume meter and connect it
      this.meter = createAudioMeter(this.audioContext);
      this.mediaStreamSource.connect(this.meter);

      // kick off the visual updating
      this.drawLoop();
    },

    streamError: function(e) {
      var msg = 'Please allow microphone access in the permissions popup.';
      if (window.chrome !== undefined) {
        msg = msg + '<br>You may need to remove this site from your media exceptions at <a href="">chrome://settings/content</a>';
      }
      var flash = $('<div class="alert alert-warning">'+
                    '<button type="button" class="close" data-dismiss="alert">×</button>'+
                    msg+'</div>');
      $('#global_message_container').empty().append(flash).show();
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

  });

})();