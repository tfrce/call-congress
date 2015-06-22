/*global CallPower, Backbone */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'change select.source': 'setSource',
      'click .record': 'onRecord',
      'click .play': 'onPlay',
      'click .reset': 'onReset',
      'submit': 'onSave'
    },

    initialize: function() {
      this.template = _.template($('#microphone-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'setup', 'destroy', 'getSources');
    },

    render: function(modal) {
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);

      var self = this;
      this.$el.on('shown.bs.modal', this.setup);
      this.$el.on('hidden.bs.modal', this.destroy);
      this.$el.modal('show');

      return this;
    },

    setup: function() {
      // get available sources (Chrome only)
      if (MediaStreamTrack.getSources !== undefined) {
        MediaStreamTrack.getSources( this.getSources );
      } else {
        this.setSource();
      }
    },

    destroy: function() {
      this.meter.destroy();
    },

    getSources: function(sourceInfos) {
      // fill in source info in selector
      sourceSelect = $('select.source', this.$el);
      sourceSelect.empty();

      for (var i = 0; i !== sourceInfos.length; ++i) {
        var sourceInfo = sourceInfos[i];
        var option = $('<option></option>');
        option.val(sourceInfo.id);
        if (sourceInfo.kind === 'audio') {
          option.text(sourceInfo.label || 'Microphone ' + (sourceSelect.children('option').length + 1));
          sourceSelect.append(option);
        }
      }
      this.setSource();
    },

    setSource: function() {
      var selectedSourceId = $('select.source', this.$el).children('option:selected').val();

      // create and render meter
      this.meter = new CallPower.Views.AudioMeter(selectedSourceId);
      this.meter.render();
    },

    onRecord: function() {
      
    },

    onPlay: function() {

    },

    onReset: function() {

    },

    onSave: function() {

    },


  });

})();