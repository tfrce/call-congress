/*global CallPower, Backbone */

(function () {
  CallPower.Views.StatisticsView = Backbone.View.extend({
    el: $('#statistics'),
    campaignId: null,

    events: {
      'change select[name="campaigns"]': 'changeCampaign',
      'change select[name="timespan"]': 'renderChart',
    },

    initialize: function() {
      this.$el.find('.input-daterange input').each(function (){
        $(this).datepicker({
          'format': "yyyy/mm/dd"
        });
      });

      _.bindAll(this, 'renderChart');
      this.$el.on('changeDate', this.renderChart);

      this.chartOpts = {
        "library":{"canvasDimensions":{"height":250}},
      };
    },

    changeCampaign: function(event) {
      this.campaignId = $('select[name="campaigns"]').val();
      $.getJSON('/api/campaign/'+this.campaignId+'/stats.json',
        function(data) {
          $('input#calls_completed').val(data.completed);
          if (data.completed && data.total_count) {
            var conversion_rate = (data.completed / data.total_count);
            conversion_pct = Number((conversion_rate*100).toFixed(2));
            $('input#conversion_rate').val(conversion_pct+"%");
          } else {
            $('input#conversion_rate').val('n/a');
          }
        });
      this.renderChart();
    },

    renderChart: function(event) {
      if (!this.campaignId) {
        return false;
      }

      var timespan = $('select[name="timespan"]').val();
      var start = new Date($('input[name="start"]').datepicker('getDate')).toISOString();
      var end = new Date($('input[name="end"]').datepicker('getDate')).toISOString();

      if (start > end) {
        $('.input-daterange input[name="start"]').addClass('error');
        return false;
      } else {
        $('.input-daterange input').removeClass('error');
      }

      var dataUrl = '/api/campaign/'+this.campaignId+'/call_chart.json?timespan='+timespan;
      if (start) {
        dataUrl += ('&start='+start);
      }
      if (end) {
        dataUrl += ('&end='+end);
      }

      this.chart = new Chartkick.LineChart('calls_for_campaign', dataUrl, this.chartOpts);
    }

  });

})();