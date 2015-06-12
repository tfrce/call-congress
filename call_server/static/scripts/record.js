/*global CallPower, Backbone */

(function () {
  CallPower.Views.RecordForm = Backbone.View.extend({
    el: $('form#record'),

    events: {
      '.audio .record': 'onRecord',
      '.audio .play': 'onPlay',
      '.audio .upload': 'onUpload',
      '.audio .version': 'onVersion',

      'submit': 'submitForm'
    },

    initialize: function() {

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