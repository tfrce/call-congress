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
      this.checkGetUserMedia();
    },

    checkGetUserMedia: function() {
      // browser prefix shim
      navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

      if (navigator.getUserMedia === undefined) {
        this.$el.find('button.record')
          .attr('title', 'This feature is not available in your browser.')
          .attr('disabled', 'disabled');
      }
    },

    onRecord: function(event) {
      event.preventDefault();

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    description: inputGroup.find('.description .help-inline').text(),
                    example_text: inputGroup.find('.description .example-text').text()
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