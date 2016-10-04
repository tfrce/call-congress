/*global $, _*/

window.CallPower = _.extend(window.CallPower || {}, {
    Models: {},
    Collections: {},
    Views: {},
    Routers: {},
    init: function () {
        console.log('Call Power');

        new this.Routers.Campaign({});
    }
});

window.renderTemplate = function(selector, context) {
    var template = _.template($('script[type="text/template"]'+selector).html(), { 'variable': 'data' });
    return $(template(context));
};

window.flashMessage = function(message, status, global) {
    if (status === undefined) { var status = 'info'; }
    var flash = $('<div class="alert alert-'+status+'">'+
                          '<button type="button" class="close" data-dismiss="alert">×</button>'+
                          message+'</div>');
    if (global) {
        $('#global_message_container').empty().append(flash).show();
    } else {
        $('#flash_message_container').append(flash);
    }
};

$(document).ready(function () {
    var csrftoken = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    CallPower.init();
    Backbone.history.start({pushState: true, root: "/admin/"});
});
