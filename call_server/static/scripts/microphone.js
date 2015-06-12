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
      this.modal = modal; // save modal info
      var html = this.template(modal);
      console.log(html);
      this.$el.html(html).modal('show');
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