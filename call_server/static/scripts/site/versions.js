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

    initialize: function() {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });

      this.collection = new CallPower.Collections.AudioRecordingList();
      this.collection.fetch(); // stop trying to make fetch happen
      this.renderCollection();

      this.listenTo(this.collection, 'add remove select', this.renderCollection);
    },

    render: function(modal) {
      console.log('versions view render', modal);
      this.modal = modal;
      var html = this.template(modal);
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



  });

})();