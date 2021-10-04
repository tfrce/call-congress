/*global CallPower, Backbone */

(function () {
  CallPower.Views.CampaignForm = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      // generic
      'click a.clear': 'clearRadioChoices',

      // campaign targets
      'change select#campaign_type':  'changeCampaignType',
      'change select#campaign_subtype':  'changeCampaignSubtype',
      'change input[name="segment_by"]': 'changeSegmentBy',

      // call limit
      'change input[name="call_limit"]': 'changeCallLimit',

      // phone numbers
      'change select#phone_number_set': 'checkForCallInCollisions',
      'change input#allow_call_in': 'checkForCallInCollisions',

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

      if ($('input[name="call_maximum"]').val()) {
        $('input[name="call_limit"]').attr('checked', 'checked');
      }

      // load existing items from hidden inputs
      this.targetListView.loadExistingItems();

      $("#phone_number_set").parents(".controls").after(
        $('<div id="call_in_collisions" class="panel alert-warning col-sm-4 hidden">').append(
          "<p>This will override call in settings for these campaigns:</p>",
          $("<ul>")
        )
      );

      this.checkForCallInCollisions();
    },

    changeCampaignType: function() {
      // updates campaign_subtype with available choices from data-attr
      var field = $('select#campaign_type');
      var val = field.val();

      var nested_field = $('select#campaign_subtype');
      var nested_choices = nested_field.data('nested-choices');
      var nested_val = nested_field.data('nested-selected');
      nested_field.empty();

      // fill in new choices from data attr
      // - handle weird obj layout from constants
      var avail = _.find(nested_choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v) {
        var option = $('<option value="'+v[0]+'">'+v[1]+'</option>');
        nested_field.append(option);
      });
      var nested_avail = _.find(avail, function(v) { return v[0] === nested_val; });

      // reset initial choice if still valid
      if (nested_avail) {
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

      // state: show/hide campaign_state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
      }

      // local or custom: no segment, location or search, show custom target_set
      if (val === "custom" || val === "local" || val === "executive") {
        // set default values
        $('.form-group.locate_by input[name="locate_by"][value=""]').click();
        $('.form-group.segment_by input[name="segment_by"][value="custom"]').click();
        // hide fields
        $('.form-group.segment_by').hide();
        $('.form-group.locate_by').hide();
        $('#target-search').hide();
        // show custom target search
        $('#set-targets').show();
      } else {
        $('.form-group.segment_by').show();
        $('.form-group.locate_by').show();
        $('#target-search').show();

        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is custom
        if (segment_by.val() !== 'custom') {
          $('#set-targets').hide();
        }
      }

      this.changeCampaignSubtype();
    },

    changeCampaignSubtype: function(event) {
      var type = $('select#campaign_type').val();
      var subtype = $('select#campaign_subtype').val();

      // state
      if (type === 'state') {
        if (subtype === 'exec') {
          $('#target-search input[name="target-search"]').attr('placeholder', 'search US NGA');
        } else {
          $('#target-search input[name="target-search"]').attr('placeholder', 'search OpenStates');
        }
      }

      // congress: show/hide target_ordering values upper_first and lower_first
      if ((type === 'congress' && subtype === 'both') ||
          (type === 'state' && subtype === 'both')) {
        $('input[name="target_ordering"][value="upper-first"]').parent('label').show();
        $('input[name="target_ordering"][value="lower-first"]').parent('label').show();
      } else {
        $('input[name="target_ordering"][value="upper-first"]').parent('label').hide();
        $('input[name="target_ordering"][value="lower-first"]').parent('label').hide();
      }

    },

    clearRadioChoices: function(event) {
      var buttons = $(event.target).parent().find('input[type="radio"]');
      buttons.attr('checked',false).trigger('change'); //TODO, debounce this?
    },

    changeSegmentBy: function() {
      var selected = $('input[name="segment_by"]:checked');

      if (selected.val() === 'location') {
        $('.form-group.locate_by').show();
      } else {
        $('.form-group.locate_by').hide();
      }

      if (selected.val() === 'custom') {
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

    checkForCallInCollisions: function(event) {
      var collisions = [];
      var taken = $("select#phone_number_set").data("call_in_map");
      $("select#phone_number_set option:selected").each(function() {
        if (taken[this.value] && collisions.indexOf(taken[this.value]) == -1)
          collisions.push(taken[this.value]);
      });

      var list = $("#call_in_collisions ul").empty();
      list.append($.map(collisions, function(name) { return $("<li>").text(name) }));

      if ($("#allow_call_in").is(":checked") && collisions.length)
        $("#call_in_collisions").removeClass("hidden");
      else
        $("#call_in_collisions").addClass("hidden");
    },

    validateNestedSelect: function(formGroup) {
      if ($('select.nested:visible').length) {
        return !!$('select.nested option:selected').val();
      } else {
        return true;
      }
    },

    validateState: function(formGroup) {
      var campaignType = $('select#campaign_type').val();
      var campaignSubtype = $('select#campaign_subtype').val();
      if (campaignType === "state") {
        if (campaignSubtype === "exec") {
          // governor campaigns can cross states
          return true;
        } else {
          // other types require a state to be selected
          return !!$('select[name="campaign_state"] option:selected').val();
        }
      } else {
        return true;
      }
    },

    validateSegmentBy: function(formGroup) {
      // if campaignType is custom or local, set segmentBy to custom and uncheck locate_by
      var campaignType = $('select#campaign_type').val();
      if (campaignType === "custom" || campaignType === "local") {
        $('input[name="segment_by"][value="custom"]').click();
        $('input[name="locate_by"]').attr('checked', false);
      }
      return true;
    },

    validateLocateBy: function(formGroup) {
      // if segmentBy is location, locateBy must have value
      var segmentBy = $('input[name="segment_by"]:checked').val();
      if (segmentBy === "location") {
        return !!$('input[name="locate_by"]:checked').val();
      } else {
        return true;
      }
    },

    validateTargetList: function(f) {
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
      if (!isValid) {
        $('.help-block', formGroup).last().text(message).addClass('has-error');
      }

      // toggle error states
      formGroup.parents('fieldset').find('legend').toggleClass('has-error', !isValid);
      formGroup.toggleClass('has-error', !isValid);
      return isValid;
    },


    validateForm: function() {
      var isValid = true;

      // campaign type
      isValid = this.validateField($('.form-group.campaign_type'), this.validateState, 'Select a state') && isValid;
      isValid = this.validateField($('.form-group.campaign_type'), this.validateNestedSelect, 'Select a sub-type') && isValid;

      // campaign segmentation
      isValid = this.validateField($('.form-group.segment_by'), this.validateSegmentBy, 'Campaign type requires custom targeting') && isValid;
      isValid = this.validateField($('.form-group.locate_by'), this.validateLocateBy, 'Please pick a location attribute') && isValid;
      
      // campaign targets
      isValid = this.validateField($('.form-group#set-targets'), this.validateTargetList, 'Add a custom target') && isValid;

      // phone numbers
      isValid = this.validateField($('.form-group.phone_number_set'), this.validateSelected, 'Select a phone number') && isValid;
      
      return isValid;
    },

    submitForm: function(event) {
      if (this.validateForm()) {
        this.targetListView.serialize();
        $(this.$el).unbind('submit').submit();
        return true;
      }
      return false;
    }

  });

})();
