(function () {
  CallPower.Routers.Campaign = Backbone.Router.extend({
    routes: {
      "campaign/create": "campaignForm",
      "campaign/edit/:id": "campaignForm",
      "campaign/copy/:id": "campaignForm",
      "campaign/audio/:id": "audioForm",
    },

    campaignForm: function(id) {
      CallPower.campaignForm = new CallPower.Views.CampaignForm();
    },

    audioForm: function(id) {
      CallPower.campaignAudioForm = new CallPower.Views.CampaignAudioForm();
    }
  });
})();