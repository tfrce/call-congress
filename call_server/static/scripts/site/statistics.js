/*global CallPower, Backbone */

(function () {
  CallPower.Views.StatisticsView = Backbone.View.extend({
    el: $('#statistics'),

    events: {
      'change select[name="campaigns"]': 'renderCampaign',
    },

    initialize: function() {
      this.renderCampaign();

      this.chartOpts = {
        "library":{"canvasDimensions":{"height":250}}
      };
    },

    renderCampaign: function(event) {
      var campaign = $('select[name="campaigns"]').val();
      if (campaign === "") {
        campaign = 1;
      }

      this.chart = new Chartkick.LineChart(
          'calls_for_campaign',
          '/api/campaign/'+campaign+'/stats.json',
          this.chartOpts
      );
    }

  });

})();