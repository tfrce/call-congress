/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignLaunchForm = Backbone.View.extend({
    el: $('#launch'),

    events: {
      'click .test-call': 'makeTestCall',
      'change #custom_embed': 'toggleCustomEmbedPanel',
      'blur #custom_embed_options input': 'updateEmbedCode',
    },

    initialize: function() {
      this.campaignId = $('#campaignId').val();
      $('.readonly').attr('readonly', 'readonly');
    },

    makeTestCall: function(event) {
      var statusIcon = $(event.target).next('.glyphicon');
      statusIcon.removeClass('error').addClass('glyphicon-earphone');
      if (window.location.hostname === 'localhost') {
        alert("Call Power cannot place test calls unless hosted on an externally routable address. Try using ngrok and restarting with the --server option.");
        $(event.target).addClass('disabled');
        statusIcon.addClass('error');
        return false;
      }

      statusIcon.addClass('active');

      var phone = $('#test_call_number').val();
      phone = phone.replace(/\s/g, '').replace(/\(/g, '').replace(/\)/g, ''); // remove spaces, parens
      phone = phone.replace("+", "").replace(/\-/g, ''); // remove plus, dash

      var location = $('#test_call_location').val();

      $.ajax({
        url: '/call/create',
        data: {campaignId: this.campaignId, userPhone: phone, userLocation: location},
        success: function(data) {
          console.log(data);
          alert('Calling you at '+$('#test_call_number').val()+' now!');
          if (data.message == 'queued') {
            statusIcon.removeClass('active').addClass('success');
          } else {
            console.error(data.message);
            statusIcon.addClass('error');
          }
        },
        error: function(err) {
          console.error(err);
        }
      });
    },

    toggleCustomEmbedPanel: function(event) {
      $('#custom_embed_options').collapse('toggle');
      this.updateEmbedCode();
    },

    updateEmbedCode: function(event) {
      $.ajax({
        url: '/api/campaign/'+this.campaignId+'/embed_code.html',
        data: {
          'custom_embed': $('#custom_embed:checked').length,
          'embed_form_id': $('#embed_form_id').val(),
          'embed_phone_id': $('#embed_phone_id').val(),
          'embed_location_id': $('#embed_location_id').val(),
          'embed_custom_css': $('#embed_custom_css').val(),
        },
        success: function(html) {
          $('textarea#embed_code').val(html);
        }
      });
    }

  });

})();