/*global CallPower, Backbone */

(function () {
  CallPower.Models.AudioRecording = Backbone.Model.extend({
    defaults: {
      id: null,
      key: null,
      description: null,
      version: null,
      hidden: null,
      campaign_ids: null,
      selected_campaign_ids: null,
      file_url: null,
      text_to_speech: null
    },

  });

  CallPower.Collections.AudioRecordingList = Backbone.Collection.extend({
    model: CallPower.Models.AudioRecording,
    url: '/api/audiorecording',
    comparator: 'version',

    initialize: function(key, campaign_id) {
      this.key = key;
      this.campaign_id = campaign_id;
    },

    parse: function(response) {
      return response.objects;
    },

    fetch: function(options) {
      // do specific pre-processing for server-side filters
      // always filter on AudioRecording key
      var keyFilter = [{name: 'key', op: 'eq', val: this.key}];
      var flaskQuery = {
        q: JSON.stringify({ filters: keyFilter })
      };
      var fetchOptions = _.extend({ data: flaskQuery }, options);

      return Backbone.Collection.prototype.fetch.call(this, fetchOptions);
    }
  });

  CallPower.Views.RecordingItemView = Backbone.View.extend({
    tagName: 'tr',

    events: {
      'click button.select': 'onSelect',
      'click button.delete': 'onDelete',
      'click button.undelete': 'onUnDelete',
      'mouseenter button.select': 'toggleSuccess',
      'mouseleave button.select': 'toggleSuccess',
      'mouseenter button.delete': 'toggleDanger',
      'mouseleave button.delete': 'toggleDanger',
      'mouseenter button.undelete': 'toggleWarning',
      'mouseleave button.undelete': 'toggleWarning',
    },

    initialize: function() {
      this.template = _.template($('#recording-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var data = this.model.toJSON();
      data.campaign_id = parseInt(this.model.collection.campaign_id);
      var html = this.template(data);
      this.$el.html(html);
      return this;
    },

    toggleSuccess: function(event) {
      $(event.target).toggleClass('btn-success');
    },

    toggleDanger: function(event) {
      $(event.target).toggleClass('btn-danger');
    },

    toggleWarning: function(event) {
      $(event.target).toggleClass('btn-warning');
    },

    onSelect: function(event) {
      this.model.collection.trigger('select', this.model.attributes);
    },

    onDelete: function(event) {
      this.model.collection.trigger('delete', this.model.attributes);
    },

    onUnDelete: function(event) {
      this.model.collection.trigger('undelete', this.model.attributes);
    },

  });

  CallPower.Views.VersionsModal = Backbone.View.extend({
    tagName: 'div',
    className: 'versions modal fade',

    events: {
      'change input.filter': 'onFilterCampaigns'
    },

    initialize: function(viewData) {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'destroyViews');

      this.viewData = viewData;
      this.collection = new CallPower.Collections.AudioRecordingList(this.viewData.key, this.viewData.campaign_id);
      this.filteredCollection = new FilteredCollection(this.collection);
      this.collection.fetch({ reset: true });
      this.views = [];

      this.listenTo(this.collection, 'reset add remove', this.renderFilteredCollection);
      this.listenTo(this.filteredCollection, 'filtered:reset filtered:add filtered:remove', this.renderFilteredCollection);
      this.listenTo(this.collection, 'select', this.selectVersion);
      this.listenTo(this.collection, 'delete', this.deleteVersion);
      this.listenTo(this.collection, 'undelete', this.unDeleteVersion);

      this.$el.on('hidden.bs.modal', this.destroyViews);
    },

    render: function() {
      // render template
      var html = this.template(this.viewData);
      this.$el.html(html);

      // reset initial filters
      this.onFilterCampaigns();

      // show the modal
      this.$el.modal('show');

      return this;
    },

    renderFilteredCollection: function() {
      var self = this;

      // clear any existing subviews
      this.destroyViews();
      var $list = this.$('table tbody').empty();

      // create subviews for each item in collection
      this.views = this.filteredCollection.map(this.createItemView, this);
      $list.append( _.map(this.views,
        function(view) { return view.render(self.campaign_id).el; },
        this)
      );
    },

    destroyViews: function() {
      // destroy each subview
      _.invoke(this.views, 'destroy');
      this.views.length = 0;
    },

    hide: function() {
      this.$el.modal('hide');
    },

    createItemView: function (model) {
      return new CallPower.Views.RecordingItemView({ model: model });
    },

    onFilterCampaigns: function() {
      var self = this;

      var showAllCampaigns = ($('input.filter[name=show_all_campaigns]:checked', this.$el).length > 0);
      var showHidden = ($('input.filter[name=show_hidden]:checked', this.$el).length > 0);

      if (showAllCampaigns) {
        this.filteredCollection.removeFilter('campaign_id');
      } else {
        this.filteredCollection.filterBy('campaign_id', function(model) {
          return _.contains(model.get('campaign_ids'), parseInt(self.viewData.campaign_id));
        });
      }
      if (showHidden) {
        this.filteredCollection.removeFilter('hidden');
      } else {
        this.filteredCollection.filterBy('hidden', function(model) {
          return (model.get('hidden') !== true); // show only those not hidden
        });
      }
    },

    ajaxPost: function(data, endpoint, hideOnComplete) {
      // make ajax POST to API
      var url = '/admin/campaign/'+this.viewData.campaign_id+'/audio/'+data.id+'/'+endpoint;
      var self = this;
      $.ajax({
        url: url,
        method: 'POST',
        success: function(response) {
          if (response.success) {
              // build friendly message like "Audio recording selected: Introduction version 3"
              var fieldDescription = $('form label[for="'+response.key+'"]').text();
              var msg = response.message + ': '+ fieldDescription + ' version ' + response.version;
              // and display to user
              window.flashMessage(msg, 'success');

              // close the modal, and cleanup subviews
              if (hideOnComplete) {
                self.hide();
              }
            } else {
              console.error(response);
              window.flashMessage(response.errors, 'error', true);
            }
        }, error: function(xhr, status, error) {
          console.error(status, error);
          window.flashMessage(response.errors, 'error');
        }
      });
    },

    selectVersion: function(data) {
      return this.ajaxPost(data, 'select', true);
    },

    deleteVersion: function(data) {
      // TODO, confirm with user
      // this doesn't actually delete objects in database or on file system
      // just hides from API

      return this.ajaxPost(data, 'hide');
    },

    unDeleteVersion: function(data) {
      return this.ajaxPost(data, 'show');
    }

  });
})();