/*global CallPower, Backbone */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .reset': 'onReset',
      'submit': 'onSave'
    },

    initialize: function() {
      this.template = _.template($('#microphone-modal-tmpl').html(), { 'variable': 'modal' });
    },

    render: function(modal) {
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);

      this.meter = new CallPower.Views.AudioMeter();

      var self = this;
      this.$el.on('shown.bs.modal', function() {
        // render meter after modal is visible
        self.meter.render();
      });
      this.$el.on('hidden.bs.modal', function() {
        self.meter.destroy();
      });
      this.$el.modal('show');

      return this;
    },

    onRecord: function() {
      
    },

    onPlay: function() {

    },

    onReset: function() {

    },

    onSave: function() {

    },


  });

})();