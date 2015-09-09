/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignLaunchForm = Backbone.View.extend({
    el: $('#launch'),

    events: {
      'click .test-call': 'makeTestCall',
      'change #embed_type': 'toggleCustomEmbedPanel',
      'blur #custom_embed_options input': 'updateEmbedCode',
    },

    initialize: function() {
      this.campaignId = $('#campaignId').val();
      $('.readonly').attr('readonly', 'readonly');
      this.toggleCustomEmbedPanel();
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
      var formType = $('#embed_type').val();
      if (formType) {
        $('.form-group.embed_code').removeClass('hidden');
      } else {
        $('.form-group.embed_code').addClass('hidden');
      }

      if (formType === 'custom' || formType === 'iframe') {
        $('#custom_embed_options').collapse('show');
      } else {
        $('#custom_embed_options').collapse('hide');
      }
      if (formType === 'iframe') {
        $('#custom_embed_options h3').text('iFrame Embed Options');
        $('#custom_embed_options .form-group').hide().filter('.iframe').show();
      } else {
        $('#custom_embed_options h3').text('Custom Embed Options');
        $('#custom_embed_options .form-group').show();
      }
      this.updateEmbedCode();
    },

    updateEmbedCode: function(event) {
      $.ajax({
        url: '/api/campaign/'+this.campaignId+'/embed_code.html',
        data: {
          'embed_type': $('#embed_type').val(),
          'embed_form_sel': $('#embed_form_sel').val(),
          'embed_phone_sel': $('#embed_phone_sel').val(),
          'embed_location_sel': $('#embed_location_sel').val(),
          'embed_custom_css': $('#embed_custom_css').val(),
          'embed_custom_js': $('#embed_custom_js').val(),
          'embed_script_display': $('#embed_script_display').val(),
        },
        success: function(html) {
          $('textarea#embed_code').val(html);
        }
      });
    }

  });

})();