/*global CallPower, Backbone */

(function () {
  CallPower.Views.TargetSearch = Backbone.View.extend({
    el: $('div#target-search'),

    events: {
      // target search
      'keydown input[name="target-search"]': 'searchKey',
      'focusout input[name="target-search"]': 'searchTab',
      'click .search': 'doTargetSearch',
      'click .search-results .result': 'selectSearchResult',
      'click .search-results .close': 'closeSearch',
    },

    initialize: function() { },

    searchKey: function(event) {
      if(event.which === 13) { // enter key
        event.preventDefault();
        this.doTargetSearch();
      }
    },

    searchTab: function(event) {
      // TODO, if there's only one result add it
      // otherwise, let user select one
    },

    doTargetSearch: function(event) {
      var self = this;
      // search the Sunlight API for the named target
      var query = $('input[name="target-search"]').val();

      var campaign_type = $('select[name="campaign_type"]').val();
      var campaign_state = $('select[name="campaign_state"]').val();
      var chamber = $('select[name="campaign_subtype"]').val();

      if (campaign_type === 'congress') {
        // hit Sunlight OpenCongress v3

        //convert generic chamber names to House / Senate
        if (chamber === 'lower') {
          chamber = 'house';
        }
        if (chamber === 'upper') {
          chamber = 'senate';
        }
        if (chamber === 'both') {
          chamber = '';
        }

        $.ajax({
          url: CallPower.Config.SUNLIGHT_CONGRESS_URL,
          data: {
            apikey: CallPower.Config.SUNLIGHT_API_KEY,
            in_office: true,
            chamber: chamber,
            query: query
          },
          beforeSend: function(jqXHR, settings) { console.log(settings.url); },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }

      if (campaign_type === 'state' && chamber === 'exec') {
        // search scraped us_governors_contact, pass full json to search on client
        $.ajax({
          url: 'https://raw.githubusercontent.com/spacedogXYZ/us_governors_contact/master/data.json',
          dataType: 'json',
          success: _.bind(self.clientSideSearch, self),
          error: self.errorSearchResults,
        });

      } else {
        // hit Sunlight OpenStates

        // TODO, request state metadata
        // display latest_json_date to user

        $.ajax({
          url: CallPower.Config.SUNLIGHT_STATES_URL,
          data: {
            apikey: CallPower.Config.SUNLIGHT_API_KEY,
            state: campaign_state,
            in_office: true,
            chamber: chamber,
            last_name: query // NB, we can't do generic query for OpenStates, let user select field?
          },
          success: self.renderSearchResults,
          error: self.errorSearchResults,
        });
      }
    },

    clientSideSearch: function(response) {
      var query = $('input[name="target-search"]').val();

      results = _.filter(response, function(item) {
        // simple case insensitive OR search on first, last or state name
        if (item.first_name.toLowerCase().includes(query.toLowerCase()) ||
            item.last_name.toLowerCase().includes(query.toLowerCase()) ||
            item.state_name.toLowerCase().includes(query.toLowerCase())
           ) {
          return true;
        }
      });
      return this.renderSearchResults(results);
    },

    renderSearchResults: function(response) {
      var results;
      if (response.results) {
        results = response.results;
      } else {
        // openstates doesn't paginate
        results = response;
      }

      var dropdownMenu = renderTemplate("#search-results-dropdown-tmpl");
      if (results.length === 0) {
        dropdownMenu.append('<li class="result close"><a>No results</a></li>');
      }

      _.each(results, function(person) {
        // standardize office titles
        if (person.title === 'Sen')  { person.title = 'Senator'; }
        if (person.title === 'Rep')  { person.title = 'Representative'; }

        if (person.bioguide_id) {
          person.uid = 'us:bioguide:'+person.bioguide_id;
        } else if (person.leg_id) {
          person.uid = 'us_state:openstates:'+person.leg_id;
        } else if (person.title === 'Governor') {
          person.uid = 'us_state:governor:'+person.state
        }

        // if person has multiple phones, use only the first office
        if (person.phone === undefined && person.offices) {
          if (person.offices) {
            person.phone = person.offices[0].phone;
          }
        }

        // render display
        var li = renderTemplate("#search-results-item-tmpl", person);
        dropdownMenu.append(li);
      });
      $('.input-group .search-results').append(dropdownMenu);
    },

    errorSearchResults: function(response) {
      // TODO: show bootstrap warning panel
      console.log(response);
    },

    closeSearch: function() {
      var dropdownMenu = $('.search-results .dropdown-menu').remove();
    },

    selectSearchResult: function(event) {
      // pull json data out of data-object attr
      var obj = $(event.target).data('object');
      
      // add it to the targetListView collection
      CallPower.campaignForm.targetListView.collection.add(obj);

      // if only one result, closeSearch
      if ($('.search-results .dropdown-menu').children('.result').length <= 1) {
        this.closeSearch();
      }
    },

  });

})();