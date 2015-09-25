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
        "stacked": true,
        "library": {
          "canvasDimensions":{"height":250},
          "yAxis": { "allowDecimals": false },
        }
      };
      this.campaignDataTemplate = _.template($('#campaign-data-tmpl').html(), { 'variable': 'data' });
      this.targetDataTemplate = _.template($('#target-data-tmpl').html(), { 'variable': 'targets'});
    },

    changeCampaign: function(event) {
      var self = this;

      this.campaignId = $('select[name="campaigns"]').val();
      $.getJSON('/api/campaign/'+this.campaignId+'/stats.json',
        function(data) {
          if (data.sessions_completed && data.sessions_started) {
            var conversion_rate = (data.sessions_completed / data.sessions_started);
            conversion_pct = Number((conversion_rate*100).toFixed(2));
            data.conversion_rate = (conversion_pct+"%");
          } else {
            data.conversion_rate = 'n/a';
          }
          if (!data.sessions_completed) {
            data.calls_per_session = 'n/a';
          }
          $('#campaign_data').html(
            self.campaignDataTemplate(data)
          ).show();

          if (data.date_start && data.date_end) {
            $('input[name="start"]').datepicker('setDate', data.date_start);
            $('input[name="end"]').datepicker('setDate', data.date_end);
          }
          self.renderChart();
        });
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

      var chartDataUrl = '/api/campaign/'+this.campaignId+'/call_chart.json?timespan='+timespan;
      if (start) {
        chartDataUrl += ('&start='+start);
      }
      if (end) {
        chartDataUrl += ('&end='+end);
      }

      this.chart = new Chartkick.ColumnChart('calls_for_campaign', chartDataUrl, this.chartOpts);

      var tableDataUrl = '/api/campaign/'+this.campaignId+'/target_calls.json?';
      if (start) {
        tableDataUrl += ('&start='+start);
      }
      if (end) {
        tableDataUrl += ('&end='+end);
      }

      var self = this;
      $.getJSON(tableDataUrl, function(data) {
        var content = self.targetDataTemplate(data);
        $('table#target_data').html(content);
        $('#target_counts').show();
      });
    }

  });

})();