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