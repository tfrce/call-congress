/*global CallPower, Backbone */

(function () {
  CallPower.Models.AudioRecording = Backbone.Model.extend({
    defaults: {
      id: null,
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
    },

    fetchFilter: function(options) {
      // filter fetch that matches the convoluted syntax used by flask-restless
      // checks for values in options.filters

      var filters = [];
      _.each(options.filters, function(val, key) {
        filters.push({ name: key,
                        op: "eq",
                        val: val});
      });

      var flaskQuery = {
        q: JSON.stringify({ filters: filters })
      };
      var fetchOptions = _.extend({ data: flaskQuery }, options);
      this.fetch(fetchOptions);
    }
  });

  CallPower.Views.RecordingItemView = Backbone.View.extend({
    tagName: 'tr',

    events: {
      'click button.select': 'onSelect',
      'click button.delete': 'onDelete',
      'mouseenter button.select': 'toggleSuccess',
      'mouseleave button.select': 'toggleSuccess',
      'mouseenter button.delete': 'toggleDanger',
      'mouseleave button.delete': 'toggleDanger',
    },

    initialize: function() {
      this.template = _.template($('#recording-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var html = this.template(this.model.toJSON());
      this.$el.html(html);
      return this;
    },

    toggleSuccess: function(event) {
      $(event.target).toggleClass('btn-success');
    },

    toggleDanger: function(event) {
      $(event.target).toggleClass('btn-danger');
    },

    onSelect: function(event) {
      this.model.collection.trigger('select', this.model.attributes);
    },

    onDelete: function(event) {
      this.model.collection.trigger('delete', this.model.attributes);
    }

  });

  CallPower.Views.VersionsModal = Backbone.View.extend({
    tagName: 'div',
    className: 'versions modal fade',

    events: {
      'change [name=show_all]': 'onFilterCampaigns',
    },

    initialize: function(viewData) {
      this.template = _.template($('#recording-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'destroyViews');

      this.viewData = viewData;

      this.collection = new CallPower.Collections.AudioRecordingList();
      this.collection.fetchFilter({
        filters: { key: this.viewData.key,
                 /*campaign_id: this.viewData.campaign_id*/
                },
        reset: true
      });
      this.views = [];

      this.listenTo(this.collection, 'reset add remove', this.render);
      this.listenTo(this.collection, 'select', this.selectVersion);
      this.listenTo(this.collection, 'delete', this.deleteVersion);

      this.$el.on('hidden.bs.modal', this.destroyViews);
    },

    render: function() {
      // clear any existing subviews
      this.destroyViews();

      // render template
      var html = this.template(this.viewData);
      this.$el.html(html);
      var $list = this.$('table tbody').empty();

      // create subviews for each item in collection
      this.views = this.collection.map(this.createItemView, this);
      $list.append( _.map(this.views,
        function(view) { return view.render().el; },
        this)
      );

      // show the modal
      this.$el.modal('show');

      return this;
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

    selectVersion: function(data) {
      // make ajax POST to API
      var url = '/admin/campaign/'+this.viewData.campaign_id+'/audio/'+data.id+'/select';
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
              self.hide();
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

    deleteVersion: function(data) {
      // make ajax DELETE to API
      var url = '/admin/campaign/'+this.viewData.campaign_id+'/audio/'+data.id+'/delete';
      var self = this;
      $.ajax({
        url: url,
        method: 'DELETE',
        success: function(response) {
          if (response.success) {
              // build friendly message like "Audio recording deleted: Introduction version 3"
              var fieldDescription = $('form label[for="'+response.key+'"]').text();
              var msg = response.message + ': '+ fieldDescription + ' version ' + response.version;
              // and display to user
              window.flashMessage(msg, 'success');

              // close the parent modal
              self.hide();
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

    onFilterCampaigns: function() {
      this.collection.reset(null);

      var showAll = !!this.$('[name=show_all]:checked').length;
      if (showAll) {
        this.collection.fetchFilter({ filters: { key: this.viewData.key } });
      } else {
        this.collection.fetchFilter({ filters: { key: this.viewData.key,
                                /*campaign_id: this.viewData.campaign_id*/ } });
      }
    },
  });

})();