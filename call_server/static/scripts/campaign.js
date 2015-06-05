/*global CallPower, Backbone */

CallPower.Views = CallPower.Views || {};

(function () {
  CallPower.Views.CampaignForm = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      // generic
      'click a.radio-inline.clear': 'clearRadioChoices',

      // campaign type
      'change select#campaign_type':  'changeCampaignType',
      'change input[name="segment_by"]': 'changeSegmentBy',

      // target search
      'keydown input[name="target_search"]': 'searchKey',
      'focusout input[name="target_search"]': 'searchTab',
      'click .input-group#target_search .search': 'targetSearch',
      'click .search-results .result': 'selectSearchResult',
      'click .search-results .close': 'closeSearch',
      'click .target-list .list-group-item .remove': 'removeTargetItem',

      // target set edit
      'click .set-target .add': 'addTargetItem',
      'focus .set-target [contenteditable]': 'editTargetItem',
      'keydown .set-target [contenteditable]': 'keyTargetItem',
      'blur .set-target [contenteditable]': 'saveTargetItem',
      // sortupdate
      // sortend ?
      
      'change input[name="call_limit"]': 'callLimit',

      'submit form': 'validateForm'
    },

    initialize: function() {
      // clear nested choices until updated by client
      if (!$('select.nested').val()) { $('select.nested').empty(); }

      // trigger change to targeting fields
      // so defaults show properly
      this.changeCampaignType();
      this.changeSegmentBy();

      // make target-list items sortable
      $('.target-list.sortable').sortable({
        items: 'li',
        handle: '.handle',
      });
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
        $('#target_search input[name="target_search"]').attr('placeholder', 'search OpenStates');
      } else {
        $('select[name="campaign_state"]').hide();
        $('#target_search input[name="target_search"]').attr('placeholder', 'search Sunlight');
      }

      // local or custom: no search, show custom target_set
      if (val === "custom" || val === "local") {
        $('#target_search input[name="target_search"]').attr('disabled', true);
        $('#target_search button.search').attr('disabled', true);
        $('.set-target').show();
      } else {
        $('#target_search input[name="target_search"]').attr('disabled', false);
        $('#target_search button.search').attr('disabled', false);
        var segment_by = $('input[name="segment_by"]:checked');
        // unless segment_by is also custom
        if (segment_by.val() !== 'custom') {
          $('.set-target').hide();
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
        $('.set-target').hide();
      } else {
        $('.set-target').show();
      }
    },

    searchKey: function(event) {
      if(event.which === 13) { // enter key
        event.preventDefault();
        this.targetSearch();
      }
    },

    searchTab: function(event) {
      // TODO, if there's only one result add it
      // otherwise, let iterate through the results and let user select one
    },

    targetSearch: function(event) {
      var self = this;
      // search the Sunlight API for the named target
      var query = $('input[name="target_search"]').val();
      console.log('search '+query);

      var campaign_type = $('select[name="campaign_type"]').val();
      var campaign_state = $('select[name="campaign_state"]').val();
      var chamber = $('select[name="campaign_subtype"]').val();

      if (campaign_type === 'congress') {
        // hit Sunlight OpenCongress v3

        $.ajax({
          url: CallPowerApp.SUNLIGHT_CONGRESS_URL,
          data: {
            apikey: CallPowerApp.SUNLIGHT_API_KEY,
            in_office: true,
            chamber: chamber,
            query: query
          },
          beforeSend: function(jqXHR, settings) { console.log(settings.url); },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }

      if (campaign_type === 'state') {
        // hit Sunlight OpenStates

        // TODO, request state metadata
        // display latest_json_date to user

        $.ajax({
          url: CallPowerApp.SUNLIGHT_STATES_URL,
          data: {
            apikey: CallPowerApp.SUNLIGHT_API_KEY,
            state: campaign_state,
            in_office: true,
            chamber: chamber,
            last_name: query // NB, we can't do generic query for OpenStates, let user select field?
          },
          beforeSend: function(jqXHR, settings) { console.log(settings.url); },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }
    },

    renderSearchResults: function(response) {
      var results;
      if (response.results) {
        results = response.results;
      } else {
        // openstates doesn't paginate
        results = response;
      }

      var dropdownMenu = renderTemplate("search-results-dropdown");
      if (results.length === 0) {
        dropdownMenu.append('<li class="result close"><a>No results</a></li>');
      }

      _.each(results, function(i) {
        // standardize office titles
        if (i.title === 'Sen')  { i.title = 'Senator'; }
        if (i.title === 'Rep')  { i.title = 'Representative'; }

        // render display
        var li = renderTemplate("search-results-item", i);

        // if multiple phones, use the first office
        if (i.phone === undefined && i.offices) {
          if (i.offices) { li.find('span.phone').html(i.offices[0].phone); }
        }
        dropdownMenu.append(li);
      });
      $('.input-group .search-results').append(dropdownMenu);
    },

    errorSearchResults: function(response) {
      // TODO: show bootstrap warning panel
      console.log(response);
    },

    closeSearch: function() {
      var dropdownMenu = $('.search-results ul.dropdown-menu').remove();
    },

    selectSearchResult: function(event) {
      // pull json data out of data-object attr
      var obj = $(event.target).data('object');
      
      // add it to the list
      this.addTargetItem(null, obj);

      // if only one result, closeSearch
      if ($('.search-results ul.dropdown-menu').children('.result').length <= 1) {
        this.closeSearch();
      }
    },

    addTargetItem: function(event, obj) {
      if (obj === undefined) {
        obj = {'title': 'Title', 'name': 'Name', 'number': '202-555-1234'};
        var placeholder = true;
      }

      // save to display list
      var targetList = $('ol.target-list');
      var listItem = renderTemplate("target-list-item", obj);
      targetList.append(listItem);
      targetList.sortable('reload').show(); // reset sortable;

      // if placeholder, adjust css
      if (placeholder) {
        listItem.children('[contenteditable]').addClass('placeholder');
      }

      // also to hidden input set
      var targetSet = $('.hidden-target-set');
      var hiddenItem = $("<input type='hidden' name='target_set[]' value='"+JSON.stringify(obj)+"' />");
      targetSet.append(hiddenItem);
    },

    editTargetItem: function(event) {
      var target = $(event.target);
      console.log('edit '+target.data('field'));

      if (target.hasClass('placeholder')) {
        target.removeClass('placeholder');
      }
    },

    keyTargetItem: function(event) {
      var target = $(event.target);

      var esc = event.which == 27,
          nl = event.which == 13;

      if (esc) {
        document.execCommand('undo');
        el.blur();
      } else if (nl) {
        this.saveTargetItem(event);
      } else if (target.text() === target.attr('placeholder')) {
        target.text(''); // overwrite
      }
    },

    saveTargetItem: function(event) {
      var target = $(event.target);
      console.log('save '+target.data('field'));

      if (target.text() === '') {
        // empty, reset to placeholder
        target.text(target.attr('placeholder'));
      }
      if (target.text() === target.attr('placeholder')) {
        target.addClass('placeholder');
      }

    },

    removeTargetItem: function(event) {
      $(event.target).parents('li.list-group-item').remove();

      // TODO, also find and remove it from hidden-target-set
    },

    callLimit: function(event) {
      var callMaxGroup = $('input[name="call_maximum"]').parents('.form-group');
      if ($(event.target).prop('checked')) {
        callMaxGroup.show();
      } else {
        callMaxGroup.hide();
        $('input[name="call_maximum"]').val('');
      }
    },

    validateForm: function(event) {
      event.preventDefault();
      //TODO, validate form
      return false;
    }

  });
})();