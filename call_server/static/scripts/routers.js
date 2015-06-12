(function () {
  CallPower.Routers.Campaign = Backbone.Router.extend({
    routes: {
      "campaign/create": "campaignForm",
      "campaign/edit/:id": "campaignForm",
      "campaign/copy/:id": "campaignForm",
      "campaign/record/:id": "recordForm",
    },

    campaignForm: function(id) {
      CallPower.campaignForm = new CallPower.Views.CampaignForm();
    },

    recordForm: function(id) {
      var recordForm = new CallPower.Views.RecordForm();
    }
  });
})();