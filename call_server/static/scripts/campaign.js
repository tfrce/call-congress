$(function(){

  var TargetView = Backbone.View.extend({

  });

  var PhoneNumberView = Backbone.View.extend({

  });

  var FormView = Backbone.View.extend({
    el: $("form#campaign"),

    events: {
      "change #campaign_type":  "updateNestedChoices"
    },

    initialize: function() {
      console.log('campaign form');


    },

    updateNestedChoices: function(event) {
      // updates sibling "nested" field with available choices from data-attr
      var field = $(event.target);
      var nested_field = field.siblings('.nested');
      nested_field.empty();

      var choices = nested_field.data('nested-choices');
      var val = field.val();

      // handle weird obj layout from constants
      var avail = _.find(choices, function(v) { return v[0] == val; })[1];
      _.each(avail, function(v, k) {
        var option = $('<option value="'+k+'">'+v+'</option>');
        nested_field.append(option);
      });

      // disable field if no choices present
      if (avail.length === 0) {
        nested_field.prop('disabled', true);
      } else {
        nested_field.prop('disabled', false);
      }

      
    },

  });

  var CampaignForm = new FormView();
});