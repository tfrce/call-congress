{% include "api/CallPowerForm.js" with context %}

var main = function() {
  callPowerForm = new CallPowerForm('{{campaign.embed.get("form_sel","#call_form")}}', jQuery);
  {% if campaign.embed.get('script_display') == 'overlay' %}
    jQuery.getScript("{{ url_for('static', filename='embed/overlay.js', _external=True) }}");
    jQuery('head').append('<link rel="stylesheet" href="{{ url_for("static", filename="embed/overlay.css", _external=True) }}" />');
  {% endif %}
}

if (typeof jQuery == 'undefined') {
  var scriptElement = document.createElement("script");
  scriptElement.src = '//cdnjs.cloudflare.com/ajax/libs/jquery/1.11.3/jquery.min.js';
  scriptElement.type = "text/javascript";
  var head = document.getElementsByTagName("head")[0] || document.documentElement;
  head.appendChild(scriptElement);
  scriptElement.onload = main;
} else {
  // use in-page jQuery

  // fallbacks for old versions
  if ($.proxy === undefined) {
    $.proxy = function( fn, context ) {
      return function() {
        return fn.apply( context || this, arguments );
      };
    };
  }
  if ($.fn.on === undefined) {
    $.fn.on = $.fn.bind;
  }

  jQuery(document).ready(main);
}
