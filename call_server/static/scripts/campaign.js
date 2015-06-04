$(function(){

  var CallPowerApp = {
    Views: {},
    initialize: function () {
        console.log('Call Power');

        this.SUNLIGHT_API_KEY = $('meta[name="SUNLIGHT_API_KEY"]').attr('content');
        this.SUNLIGHT_CONGRESS_URL = "https://congress.api.sunlightfoundation.com/legislators/";
        this.SUNLIGHT_STATES_URL = "http://openstates.org/api/v1/legislators/";

        this.campaignForm = new CampaignFormView();
    },
  };

  var renderTemplate = function(name, context) {
    var template = _.template($('script[type="text/template"][name="'+name+'"]').html(), { 'variable': 'data' });
    return $(template(context));
  };

  var TargetView = Backbone.View.extend({

  });

  var PhoneNumberView = Backbone.View.extend({

  });

  var CampaignFormView = Backbone.View.extend({
    el: $('form#campaign'),

    events: {
      'change select#campaign_type':  'updateCampaignTypeChoices',
      'click a.radio-inline.clear': 'clearRadioChoices',
      
      'change input[name="target_by"]': 'targetBy',
      'keydown input[name="target_search"]': 'searchKey',
      'focusout input[name="target_search"]': 'searchTab',
      'click .input-group#target_search button': 'targetSearch',
      'click .search-results .result': 'selectResult',
      'click .search-results .btn.close': 'closeSearch',
      'click .target-list .list-group-item span.remove': 'removeTargetItem',
      
      'change input[name="call_limit"]': 'callLimit',

      'submit form': 'validateForm'
    },

    initialize: function() {
      console.log('campaign form');

      // clear nested choices until updated by client
      if (!$('select.nested').val()) { $('select.nested').empty(); }

      // display targeting fields
      this.targetBy();

      // 
      this.updateCampaignTypeChoices();

      // make target_set options sortable
      $('select[name="target_set"]').sortable({
        items: 'li' ,
        placeholder : '<li></li>'
      });
    },

    updateCampaignTypeChoices: function() {
      // updates campaign_subtype with available choices from data-attr
      var field = $('select#campaign_type');
      var nested_field = $('select#campaign_subtype');
      nested_field.empty();

      var choices = nested_field.data('nested-choices');
      var val = field.val();

      // handle weird obj layout from constants
      var avail = _.find(choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v) {
        var option = $('<option value="'+v[0]+'">'+v[1]+'</option>');
        nested_field.append(option);
      });

      // special case, show/hide state select
      if (val === 'state') {
        $('select[name="campaign_state"]').show();
      } else {
        $('select[name="campaign_state"]').hide();
      }

      // disable field if no choices present
      if (avail.length === 0) {
        nested_field.prop('disabled', true);
      } else {
        nested_field.prop('disabled', false);
      }
    },

    clearRadioChoices: function(event) {
      var buttons = $(event.target).parent().find('input[type="radio"]');
      buttons.attr('checked',false).trigger('change'); //TODO, debounce this?
    },

    targetBy: function() {
      var selected = $('input[name="target_by"]:checked');
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
        var li = renderTemplate("search-results-item", i);
        if (i.phone === undefined && i.offices) {
          // put the first office phone in
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

    selectResult: function(event) {
      var obj = $(event.target).data('object');
      // pull json data out of data-object attr

      // save to display list
      var targetList = $('ol.target-list');
      var listItem = renderTemplate("target-list-item", obj);
      targetList.append(listItem);
      targetList.sortable('reload'); // reset sortable
      targetList.show();

      // also to hidden input set
      var targetSet = $('.hidden-target-set');
      var hiddenItem = $("<input type='hidden' name='target_set[]' value='"+JSON.stringify(obj)+"' />");
      targetSet.append(hiddenItem);

      // if only one result, closeSearch
      if ($('.search-results ul.dropdown-menu').children('.result').length <= 1) {
        this.closeSearch();
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

    CallPowerApp.initialize();
});