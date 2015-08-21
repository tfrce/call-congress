/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignLaunchForm = Backbone.View.extend({
    el: $('#launch'),

    events: {
      'click .test-call': 'makeTestCall',
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

      var campaignId = $('#campaignId').val();

      var phone = $('#test_call_number').val();
      phone = phone.replace(/\s/g, '').replace(/\(/g, '').replace(/\)/g, ''); // remove spaces, parens
      phone = phone.replace("+", "").replace(/\-/g, ''); // remove plus, dash

      var location = $('#test_call_location').val();

      $.ajax({
        url: '/call/create',
        data: {campaignId: campaignId, userPhone: phone, userLocation: location},
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
    }

  });

})();