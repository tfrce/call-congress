/*!
  * domready (c) Dustin Diaz 2014 - License MIT
  */
!function (name, definition) {
  if (typeof module != 'undefined') module.exports = definition();
  else if (typeof define == 'function' && typeof define.amd == 'object') define(definition);
  else this[name] = definition();
}('domready', function () {
  var fns = [], listener
    , doc = document
    , hack = doc.documentElement.doScroll
    , domContentLoaded = 'DOMContentLoaded'
    , loaded = (hack ? /^loaded|^c/ : /^loaded|^i|^c/).test(doc.readyState);

  if (!loaded)
  doc.addEventListener(domContentLoaded, listener = function () {
    doc.removeEventListener(domContentLoaded, listener);
    loaded = 1;
    while (listener = fns.shift()) listener();
  });

  return function (fn) {
    loaded ? fn() : fns.push(fn);
  };
});

/*!
  * Call Power embed javascript
  Renders new form via iframe, or attaches post-submit callback to existing form
  * AGPLv3
  */
(function() {
  call_power_embed = window['call_power_embed'] || {};

  var iframe_tag = document.createElement('iframe');
  function receiveMessage(event){
    if(event.origin == "{{request.host_url}}"){
      var window_height = event.data;
      iframe_tag.height = window_height + "px";
    }
  }
  window.addEventListener("message", receiveMessage, false);

  domready(function(){
    var widget = document.getElementById("call-power-widget");
    var width = 500;

    {% if request.widget %}
    if(typeof widget !== "undefined"){
      {# /* render embed-iframe */ #}
      var embed_url_parts = widget.getAttribute("href").split('?');
      var embed_url = embed_url_parts[0] + "/embed_iframe?" + embed_url_parts[1];

      {# /* get custom overrides defined in call_power_embed global */ #}
      if("width" in call_power_embed){
        width = call_power_embed.width;
      }
      if("css" in call_power_embed){
        embed_url += "&css=" + encodeURIComponent(call_power_embed.css);
      }

      iframe_tag.setAttribute("src",embed_url);
      iframe_tag.setAttribute("frameborder",0);
      iframe_tag.setAttribute("width",width);
    
      widget.parentNode.insertBefore(iframe_tag, widget);

      widget.remove();
    }
    {% else %}
      {# /* no widget requested, attach callback to existing form */ #}
      var fields = ['form_id', 'phone_id', 'location_id'];
      for (var i=0; i<fields.length; i++) {
        var fn = fields[i];
        var fv = fn.replace('_id', '');
        if (call_power_embed.hasOwnProperty(fn)) {
          call_power_embed[fv] = document.getElementById(call_power_embed[fn]);
        } else {
          if (fv = 'form') {
            call_power_embed[fv] = document.getElementsByTagName(fv)[0];
          } else {
            call_power_embed[fv] = document.getElementsByName(fv)[0];
          }
        }
      }
  
      // create new event for secondary submit
      var custom_event = document.createEvent('Event');
      custom_event.initEvent('secondary_submit', true, true);
      call_power_embed.form.addEventListener('submit', function (e) {
        call_power_embed.form.dispatchEvent(custom_event);
      });

      var ajax = new XMLHttpRequest();
      ajax.onreadystatechange = function() {
          if (ajax.readyState != XMLHttpRequest.DONE || ajax.status != 200) return;
          call_power_embed.form.removeEventListener('secondary_submit') ;
        };

      call_power_embed.form.addEventListener('secondary_submit', function(event){
        var url = "{{url_for('call.create', campaignId=campaign.id, _external=True)}}";
        ajax.open("GET", url+"&userPhone="+call_power_embed.phone.value, false);
        ajax.send();
      });
    {% endif %}

  });
})();