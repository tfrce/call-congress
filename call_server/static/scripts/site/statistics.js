/*global CallPower, Backbone */

(function () {
  CallPower.Views.StatisticsView = Backbone.View.extend({
    el: $('#statistics'),

    events: {
      'change select[name="campaigns"]': 'renderChart',
      'change select[name="timespan"]': 'renderChart',
    },

    initialize: function() {
      this.$el.find('.input-daterange input').each(function (){
        $(this).datepicker({
          'format': "yyyy/mm/dd"
        });
      });

      this.renderChart();
      this.chartOpts = {
        "library":{"canvasDimensions":{"height":250}},
      };

      this.$el.on('changeDate', this.renderChart);
      this.$el.on('changeDate', this.renderChart);
    },

    renderChart: function(event) {
      var campaign = $('select[name="campaigns"]').val();
      if (campaign === "") {
        campaign = 1;
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


      var dataUrl = '/api/campaign/'+campaign+'/stats.json?timespan='+timespan;
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