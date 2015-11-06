{% include "api/CallPowerForm.js" with context %}

var main = function() {
  callPowerForm = new CallPowerForm('{{campaign.embed.get("form_sel","#call_form")}}', jQuery);
  {% if campaign.embed.get('script_display') == 'overlay' %}
    jQuery.getScript("{{ url_for('static', filename='embed/overlay.js', _external=True) }}");
    jQuery('head').append('<link rel="stylesheet" href="{{ url_for("static", filename="embed/overlay.css", _external=True) }}" />');
  {% endif %}
}

// from substack/semver-compare
// license MIT
function versionCmp (a, b) {
    var pa = a.split('.');
    var pb = b.split('.');
    for (var i = 0; i < 3; i++) {
        var na = Number(pa[i]);
        var nb = Number(pb[i]);
        if (na > nb) return 1;
        if (nb > na) return -1;
        if (!isNaN(na) && isNaN(nb)) return 1;
        if (isNaN(na) && !isNaN(nb)) return -1;
    }
    return 0;
};

if ((typeof jQuery == 'undefined') || (versionCmp(jQuery.fn.jquery, '1.5.0') < 0)) {
  var scriptElement = document.createElement("script");
  scriptElement.src = '//cdnjs.cloudflare.com/ajax/libs/jquery/1.11.3/jquery.min.js';
  scriptElement.type = "text/javascript";
  var head = document.getElementsByTagName("head")[0] || document.documentElement;
  head.appendChild(scriptElement);
  scriptElement.onload = main;
} else {
  // use in-page jQuery

  if ($.fn.on === undefined) {
    $.fn.on = $.fn.bind;
  }

  jQuery(document).ready(main);
}
