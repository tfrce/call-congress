/*global CallPower, Backbone */

(function () {
  CallPower.Models.AudioRecording = Backbone.Model.extend({
    defaults: {
      campaign: null,
      key: null,
      description: null,
      version: null
    },

  });

  CallPower.Collections.AudioRecordingList = Backbone.Collection.extend({
    model: CallPower.Models.AudioRecording,
    url: '/api/recording',
    comparator: 'version',
    parse: function(response) {
      return response.objects;
    }
  });

  CallPower.Views.RecordingItemView = Backbone.View.extend({
    tagName: 'tr',

    initialize: function() {
      this.template = _.template($('#recording-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var html = this.template(this.model.toJSON());
      this.$el.html(html);
      return this;
    },

  });

  CallPower.Views.VersionsModal = Backbone.View.extend({
    tagName: 'div',
    className: 'versions modal fade',

    events: {
      'change [name=show_all]': 'onFilterCampaigns'
    },

    initialize: function(modalData) {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });
      this.modalData = modalData;

      this.collection = new CallPower.Collections.AudioRecordingList();
      this.filterCollection({ key: this.modalData.key,
                              campaign_id: this.modalData.campaign_id });
      this.renderCollection();

      this.listenTo(this.collection, 'add remove select', this.renderCollection);
    },

    render: function() {
      var html = this.template(this.modalData);
      this.$el.html(html);
      
      this.$el.modal('show');

      return this;
    },

    renderCollection: function() {
      var $list = this.$('table tbody').empty();

      var rendered_items = [];
      this.collection.each(function(model) {
        var item = new CallPower.Views.RecordingItemView({
          model: model,
        });
        var $el = item.render().$el;

        rendered_items.push($el);
      }, this);
      $list.append(rendered_items);

    },

    filterCollection: function(values) {
      // filter fetch that matches the convoluted syntax used by flask-restless
      var filters = [];

      _.each(values, function(val, key) {
        filters.push({ name: key,
                        op: "eq",
                        val: val});
      });

      this.collection.fetch({
        data: { q: JSON.stringify({ filters: filters }) }
      });
    },

    onFilterCampaigns: function() {
      this.collection.reset(null);

      var showAll = !!this.$('[name=show_all]:checked').length;
      if (showAll) {
        this.filterCollection({ key: this.modalData.key });
      } else {
        this.filterCollection({ key: this.modalData.key,
                                campaign_id: this.modalData.campaign_id });
      }
    },

  });

})();