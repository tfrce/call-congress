/*global $, _*/

window.CallPower = _.extend(window.CallPower, {
    init: function () {
        console.log('Call Power');

        this.campaignForm = new CallPower.Views.CampaignForm();
    }
});

window.renderTemplate = function(name, context) {
    var template = _.template($('script[type="text/template"][name="'+name+'"]').html(), { 'variable': 'data' });
    return $(template(context));
};

$(document).ready(function () {
    CallPower.init();
});
