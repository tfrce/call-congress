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

    requiredFields: ['msg_intro', 'msg_call_block_intro'],

    initialize: function() {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);
      window.URL = window.URL || window.webkitURL;

      // add required fields client-side
      _.each(this.requiredFields, function(f) {
        $('label[for='+f+']').addClass('required');
      });

      this.campaign_id = $('input[name="campaign_id"]').val();

      $('audio', this.el).on('ended', this.onPlayEnded);
      _.bindAll(this, 'onPlayEnded');
    },

    onRecord: function(event) {
      event.preventDefault();

      // pull modal info from related fields
      var inputGroup = $(event.target).parents('.input-group');
      var modal = { name: inputGroup.prev('label').text(),
                    key: inputGroup.prev('label').attr('for'),
                    description: inputGroup.find('.description .help-inline').text(),
                    example_text: inputGroup.find('.description .example-text').text(),
                    campaign_id: this.campaign_id
                  };
      this.microphoneView = new CallPower.Views.MicrophoneModal();
      this.microphoneView.render(modal);
    },

    onPlay: function(event) {
      event.preventDefault();
      
      var button = $(event.target);
      var inputGroup = button.parents('.input-group');
      var key = inputGroup.prev('label').attr('for');
      var playback = button.children('audio');

      var self = this;
      $.getJSON('/api/campaign/'+self.campaign_id,
        function(data) {
          var recording = data.audio_msgs[key];

          if (recording === undefined) {
            button.addClass('disabled');
            return false;
          }
          if (recording.substring(0,4) == 'http') {
            // play file url through <audio> object
            playback.attr('src', data.audio_msgs[key]);
            playback[0].play();
          } else if (CallPower.Config.TWILIO_CAPABILITY) {
            //connect twilio API to read text-to-speech
            twilio = Twilio.Device.setup(CallPower.Config.TWILIO_CAPABILITY, 
              {"rtc": (navigator.getUserMedia !== undefined), "debug":true});
            twilio.connect({'text': recording });
            twilio.disconnect(self.onPlayEnded);
          } else {
            return false;
          }

          button.children('.glyphicon').removeClass('glyphicon-play').addClass('glyphicon-pause');
          button.children('.text').html('Pause');
        }
      );
    },

    onPlayEnded: function(event) {
      var button = $(event.target).parents('.btn');
      button.children('.glyphicon').removeClass('glyphicon-pause').addClass('glyphicon-play');
      button.children('.text').html('Play');
    },

    onVersion: function(event) {
      event.preventDefault();

      var inputGroup = $(event.target).parents('.input-group');
      var modal = {
        name: inputGroup.prev('label').text(),
        key: inputGroup.prev('label').attr('for'),
        campaign_id: this.campaign_id
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