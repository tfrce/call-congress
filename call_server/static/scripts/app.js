/*global $, _*/

window.CallPower = _.extend(window.CallPower, {
    Models: {},
    Collections: {},
    Views: {},
    init: function () {
        console.log('Call Power');

        this.campaignForm = new CallPower.Views.CampaignForm();
    }
});

window.renderTemplate = function(selector, context) {
    var template = _.template($('script[type="text/template"]'+selector).html(), { 'variable': 'data' });
    return $(template(context));
};

$(document).ready(function () {
    CallPower.init();
});
