/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignForm = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      // generic
      'click a.radio-inline.clear': 'clearRadioChoices',

      // campaign type
      'change select#campaign_type':  'changeCampaignType',
      'change input[name="segment_by"]': 'changeSegmentBy',

      // call limit
      'change input[name="call_limit"]': 'changeCallLimit',

      'submit': 'submitForm'
    },

    initialize: function() {
      // init child views
      this.searchForm = new CallPower.Views.TargetSearch();
      this.targetListView = new CallPower.Views.TargetList();

      // clear nested choices until updated by client
      if (!$('select.nested').val()) { $('select.nested').empty(); }

      // trigger change to targeting fields
      // so defaults show properly
      this.changeCampaignType();
      this.changeSegmentBy();
    },

    changeCampaignType: function() {
      // updates campaign_subtype with available choices from data-attr
      var field = $('select#campaign_type');
      var val = field.val();

      var nested_field = $('select#campaign_subtype');
      var nested_choices = nested_field.data('nested-choices');
      var nested_val = nested_field.val();
      nested_field.empty();

      // fill in new choices from data attr
      // - handle weird obj layout from constants
      var avail = _.find(nested_choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v) {
        var option = $('<option value="'+v[0]+'">'+v[1]+'</option>');
        nested_field.append(option);
      });

      // reset initial choice if still valid
      if (_.contains(_.flatten(avail), nested_val)) {
        nested_field.val(nested_val);
      } else {
        nested_field.val('');
      }

      // disable field if no choices present
      if (avail.length === 0) {
        nested_field.prop('disabled', true);
      } else {
        nested_field.prop('disabled', false);
      }

      // special cases

      // state: show/hide campaign_state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search Sunlight');
      }

      // local or custom: no search, show custom target_set
      if (val === "custom" || val === "local") {
        $('#target-search input[name="target-search"]').attr('disabled', true);
        $('#target-search button.search').attr('disabled', true);
        $('#set-targets').show();
      } else {
        $('#target-search input[name="target-search"]').attr('disabled', false);
        $('#target-search button.search').attr('disabled', false);
        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is also custom
        if (segment_by.val() !== 'custom') {
          $('#set-targets').hide();
        }
      }
    },

    clearRadioChoices: function(event) {
      var buttons = $(event.target).parent().find('input[type="radio"]');
      buttons.attr('checked',false).trigger('change'); //TODO, debounce this?
    },

    changeSegmentBy: function() {
      var selected = $('input[name="segment_by"]:checked');
      if (selected.val() !== "custom") {
        $('#set-targets').hide();
      } else {
        $('#set-targets').show();
      }
    },

    changeCallLimit: function(event) {
      var callMaxGroup = $('input[name="call_maximum"]').parents('.form-group');
      if ($(event.target).prop('checked')) {
        callMaxGroup.show();
      } else {
        callMaxGroup.hide();
        $('input[name="call_maximum"]').val('');
      }
    },

    validateForm: function() {
      // check segment compatibility for type

      // if type == custom, ensure we have targets

      // ensure we have a phone number allocated

      return true;

    },

    submitForm: function(event) {
      if (this.validateForm()) {
        this.targetListView.serialize();
        return true;
      }

      return false;
    }

  });

})();