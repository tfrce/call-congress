/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignLaunchForm = Backbone.View.extend({
    el: $('#launch'),

    events: {
      'click .test-call': 'makeTestCall',
    },

    makeTestCall: function() {
      var phone = $('#test_call_number').val();
      phone = phone.replace(/\s/g, '').replace(/\(/g, '').replace(/\)/g, ''); // remove spaces, parens
      phone = phone.replace("+", "").replace(/\-/g, ''); // remove plus, dash

      var campaignId = $('#campaignId').val();

      $.ajax({
        url: '/call/create',
        data: {userPhone: phone, campaignId: campaignId},
        success: function(data) {
          console.log(data);
          alert('calling '+phone+' now');
        },
        error: function(err) {
          console.error(err);
        }
      });
    }

  });

})();