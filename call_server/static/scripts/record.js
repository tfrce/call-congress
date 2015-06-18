/*global CallPower, Backbone */

(function () {
  CallPower.Views.RecordForm = Backbone.View.extend({
    el: $('form#record'),

    events: {
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .upload': 'onUpload',
      'click .version': 'onVersion',

      'submit': 'submitForm'
    },

    initialize: function() {
      console.log('record form');

      // webkit shim
      window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext;
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      this.checkGetUserMedia();
    },

    checkGetUserMedia: function() {
      if (navigator.getUserMedia === undefined) {
        this.$el.find('button.record')
          .attr('title', 'This feature not available in your browser.')
          .attr('disabled', 'disabled');
      }
    },

    onRecord: function(event) {
      event.preventDefault();
      console.log('onRecord');

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    example_text: inputGroup.next('.description').text()
                  };
      this.microphoneView = new CallPower.Views.MicrophoneModal();
      this.microphoneView.render(modal);
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