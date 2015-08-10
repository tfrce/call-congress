/*global CallPower, Backbone */

(function () {
  CallPower.Views.SystemForm = Backbone.View.extend({
    el: $('#system'),

    events: {
      'click .reveal': 'toggleSecret',
    },

    toggleSecret: function(event) {
      var input = $(event.target).parent().siblings('input');
        if (input.prop('type') === 'password') {
            input.prop('type','text');
        } else {
            input.prop('type','password');
        }
    }

  });

})();