/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignAudioForm = Backbone.View.extend({
    el: $('form#audio'),

    events: {
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .upload': 'onUpload',
      'click .version': 'onVersion',

      'submit': 'submitForm'
    },

    requiredFields: ['msg_intro', 'msg_call_block_intro', 'msg_final_thanks'],

    initialize: function() {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);
      window.URL = window.URL || window.webkitURL;

      // add required client-side
      _.each(this.requiredFields, function(f) {
        $('label[for='+f+']').addClass('required');
      });
    },

    onRecord: function(event) {
      event.preventDefault();

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    key: inputGroup.prev('label').attr('for'),
                    description: inputGroup.find('.description .help-inline').text(),
                    example_text: inputGroup.find('.description .example-text').text(),
                    campaign_id: $('input[name="campaign_id"]').val()
                  };
      this.microphoneView = new CallPower.Views.MicrophoneModal();
      this.microphoneView.render(modal);
    },

    onPlay: function(event) {
      event.preventDefault();
      console.log('onPlay TBD');
    },

    onVersion: function(event) {
      event.preventDefault();

      var inputGroup = $(event.target).parents('.input-group');
      var modal = {
        name: inputGroup.prev('label').text(),
        key: inputGroup.prev('label').attr('for'),
        campaign_id: $('input[name="campaign_id"]').val()
      };
      this.versionsView = new CallPower.Views.VersionsModal(modal);
      this.versionsView.render();
    },

    validateForm: function() {
      var isValid = true;

      // check required fields for valid class
      _.each(this.requiredFields, function(f) {
        var formGroup = $('.form-group.'+f);
        var fieldValid = formGroup.hasClass('valid');
        if (!fieldValid) {
          formGroup.find('.input-group .help-block')
            .text('This field is required.')
            .addClass('error');
        }
        isValid = isValid && fieldValid;
      });

      // call validators
      
      return isValid;
    },

    submitForm: function(event) {
      if (this.validateForm()) {
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();