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

      // load existing items from hidden inputs
      this.targetListView.loadExistingItems();
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

      // hide field if no choices present
      if (avail.length === 0) {
        nested_field.hide();
      } else {
        nested_field.show();
      }

      // special cases

      // congress: show/hide target_ordering values senate_first and house_first
      if ((val === 'congress' && nested_val === 'both') ||
          (val === 'state' && nested_val === 'both')) {
        $('input[name="target_ordering"][value="senate-first"]').parent('label').show();
        $('input[name="target_ordering"][value="house-first"]').parent('label').show();
      } else {
        $('input[name="target_ordering"][value="senate-first"]').parent('label').hide();
        $('input[name="target_ordering"][value="house-first"]').parent('label').hide();
      }

      // state: show/hide campaign_state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search Sunlight');
      }

      // local or custom: no seegment or search, show custom target_set
      if (val === "custom" || val === "local") {
        $('.form-group.segment_by').hide();
        $('#target-search').addClass('invisible');
        
        $('#set-targets').show();
      } else {
        $('.form-group.segment_by').show();
        $('#target-search').removeClass('invisible');

        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is other
        if (segment_by.val() !== 'other') {
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

      if (selected.val() === 'location') {
        $('.form-group.segment_location').show();
      } else {
        $('.form-group.segment_location').hide();
      }

      if (selected.val() === "other") {
        $('#set-targets').show();
      } else {
        $('#set-targets').hide();
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

    validateSegmentBy: function(formGroup) {
      // if campaignType is custom or local, segmentBy must equal other
      var campaignType = $('select#campaign_type').val();
      if (campaignType === "custom" || campaignType === "local") {
        var segmentBy = $('input[name="segment_by"]:checked').val();
        if (segmentBy === "other") { return true; }
        else { return false; }
      }
      return true;
    },

    validateTargetList: function(formGroup) {
      // if type == custom, ensure we have targets
      if ($('select#campaign_type').val() === "custom") {
        return !!CallPower.campaignForm.targetListView.collection.length;
      } else {
        return true;
      }
    },

    validateSelected: function(formGroup) {
      return !!$('select option:selected', formGroup).length;
    },

    validateField: function(formGroup, validator, message) {
      // run validator for formGroup
      var isValid = validator(formGroup);

      // put message in last help-block
      $('.help-block', formGroup).last().text((!isValid) ? message : '');

      // toggle error states
      formGroup.parents('fieldset').find('legend').toggleClass('has-error', !isValid);
      formGroup.toggleClass('has-error', !isValid);
      return isValid;
    },


    validateForm: function() {
      var isValid = true;

      isValid = this.validateField($('.form-group.segment_by'), this.validateSegmentBy, 'Campaign type requires custom targeting') && isValid;
      isValid = this.validateField($('.form-group#set-targets'), this.validateTargetList, 'Add a custom target') && isValid;
      isValid = this.validateField($('.form-group.phone_number_set'), this.validateSelected, 'Select a phone number') && isValid;
      
      return isValid;
    },

    submitForm: function(event) {
      event.preventDefault();

      if (this.validateForm()) {
        this.targetListView.serialize();
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();