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
      this.viewData = viewData;

      this.collection = new CallPower.Collections.AudioRecordingList();
      this.filterCollection({ key: this.viewData.key,
                              /*campaign_id: this.viewData.campaign_id*/ });
      this.renderCollection();

      this.listenTo(this.collection, 'add remove', this.renderCollection);
      this.listenTo(this.collection, 'select', this.selectVersion);
      this.listenTo(this.collection, 'delete', this.deleteVersion);
    },

    render: function() {
      var html = this.template(this.viewData);
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

              // close the parent modal
              self.$el.modal('hide');
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
              self.destroy();
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
        this.filterCollection({ key: this.viewData.key });
      } else {
        this.filterCollection({ key: this.viewData.key,
                                /*campaign_id: this.viewData.campaign_id*/ });
      }
    },
  });

})();