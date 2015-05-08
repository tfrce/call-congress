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
      var choices = nested_field.data('nested-choices');
      
      var val = field.val();
      var avail = choices[val];
      
    },

  });

  var CampaignForm = new FormView();
});