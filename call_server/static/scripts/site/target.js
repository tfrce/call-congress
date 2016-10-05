/*global CallPower, Backbone */

(function () {
  CallPower.Models.Target = Backbone.Model.extend({
    defaults: {
      id: null,
      uid: null,
      title: null,
      name: null,
      number: null,
      order: null
    },

  });

  CallPower.Collections.TargetList = Backbone.Collection.extend({
    model: CallPower.Models.Target,
    comparator: 'order'
  });

  CallPower.Views.TargetItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'list-group-item target',

    initialize: function() {
      this.template = _.template($('#target-item-tmpl').html(), { 'variable': 'data' });
    },

    render: function() {
      var html = this.template(this.model.toJSON());
      this.$el.attr('id', 'target_set-'+this.model.get('order'));
      this.$el.html(html);
      return this;
    },

    events: {
      'keydown [contenteditable]': 'onEdit',
      'blur [contenteditable]': 'onSave',
      'click .remove': 'onRemove',
    },

    onEdit: function(event) {
      var target = $(event.target);
      var esc = event.which == 27,
          nl = event.which == 13,
          tab = event.which == 9;


      if (esc) {
        document.execCommand('undo');
        target.blur();
      } else if (nl) {
        event.preventDefault(); // stop user from creating multi-line spans
        target.blur();
      } else if (tab) {
        event.preventDefault(); // prevent focus from going back to first field
        target.next('[contenteditable]').focus(); // send it to next editable
      } else if (target.text() === target.attr('placeholder')) {
        target.text(''); // overwrite placeholder text
        target.removeClass('placeholder');
      }
    },

    onSave: function(event) {
      var field = $(event.target);

      if (field.text() === '') {
        // empty, reset to placeholder
        field.text(field.attr('placeholder'));
      }
      if (field.text() === field.attr('placeholder')) {
        field.addClass('placeholder');
        return;
      }

      var fieldName =field.data('field');
      this.model.set(fieldName, field.text());
      field.removeClass('placeholder');
    },

    onRemove: function(event) {
      // clear related inputs
      var sel = 'input[name^="target_set-'+this.model.get('order')+'"]';
      this.$el.remove(sel);

      // and destroy the model
      this.model.destroy();
    },

  });

  CallPower.Views.TargetList = Backbone.View.extend({
    el: '#set-targets',

    events: {
      'click .add': 'onAdd',
    },

    initialize: function() {
      this.collection = new CallPower.Collections.TargetList();
      // bind to future render events
      this.listenTo(this.collection, 'add remove sort reset', this.render);
      this.listenTo(this.collection, 'add', this.recalculateOrder);

      // make target-list items sortable
      $('.target-list.sortable').sortable({
         items: 'li',
         handle: '.handle',
      }).bind('sortupdate', this.onSortUpdate);
    },

    loadExistingItems: function() {
      // check for items in serialized inputs
      if(this.$el.find('input[name="target_set_length"]').val()) {
        this.deserialize();
        this.recalculateOrder(this);
      }
    },

    render: function() {
      var $list = this.$('ol.target-list').empty().show();

      var rendered_items = [];
      this.collection.each(function(model) {
        var item = new CallPower.Views.TargetItemView({
          model: model,
          attributes: {'data-cid': model.cid}
        });
        var $el = item.render().$el;

        _.each(model.attributes, function(val, key) {
          if (val === null) {
            // set text of $el, without triggering blur
            var sel = 'span[data-field="'+key+'"]';
            var span = $el.children(sel);
            var pl = span.attr('placeholder');
            span.text(pl).addClass('placeholder');
          }
        });

        rendered_items.push($el);
      }, this);
      $list.append(rendered_items);

      var target_set_errors = this.$el.find('input[name^="target_set-"]').filter('[name$="-error"]');
      target_set_errors.each(function(error) {
        var id = $(this).attr('name').replace('-error','');
        var item = $('#'+id);
        item.addClass('error');

        var message = $(this).val();
        item.append('<span class="message">'+message+'</span>');
      });

      $('.target-list.sortable').sortable('update');

      return this;
    },

    serialize: function() {
      // write collection to hidden inputs in format WTForms expects
      var target_set = this.$el.find('#target-set');

      // clear any existing target_set-N inputs
      target_set.find('input').remove('[name^="target_set-"]');

      this.collection.each(function(model, index) {
        // create new hidden inputs named target_set-N-FIELD
        var fields = ['order','title','name','number','uid'];
        _.each(fields, function(field) {
          var input = $('<input name="target_set-'+index+'-'+field+'" type="hidden" />');
          input.val(model.get(field));

          // append to target-set div
          target_set.append(input);
        });
      });
    },

    deserialize: function() {
      // destructive operation, create models from data in inputs
      var self = this;

      // clear rendered targets
      var $list = this.$('ol.target-list').empty();

      // figure out how many items we have
      var target_set_length = this.$el.find('input[name="target_set_length"]').val();

      // iterate over total
      var items = [];
      _(target_set_length).times(function(n) {
        var model = new CallPower.Models.Target();
        var fields = ['order','title','name','number','uid'];
        _.each(fields, function(field) {
          // pull field values out of each input
          var sel = 'input[name="target_set-'+n+'-'+field+'"]';
          var val = self.$el.find(sel).val();
          model.set(field, val);
        });
        items.push(model);
      });
      self.collection.reset(items);
    },

    shortRandomString: function(prefix, length) {
      // generate a random string, with optional prefix
      // should be good enough for use as uid
      if (length === undefined) { length = 6; }
      var randstr = ((Math.random()*Math.pow(36,length) << 0).toString(36)).slice(-1*length);
      if (prefix !== undefined) { return prefix+randstr; }
      return randstr;
    },

    onAdd: function() {
      // create new empty item
      var item = this.collection.add({
        uid: this.shortRandomString('custom:', 6)
      });
      this.recalculateOrder(this);
    },

    onSortUpdate: function() {
      // because this event is bound by jQuery, 'this' is the element, not the parent view
      var view = CallPower.campaignForm.targetListView; // get a reference to it manually
      return view.recalculateOrder(); // pass it to the backbone view
    },

    recalculateOrder: function() {
      var self = this;
      // iterate over DOM objects to set item order
      $('.target-list .list-group-item').each(function(index) {
        var elem = $(this); // in jquery.each, 'this' is the element
        var cid = elem.data('cid');
        var item = self.collection.get(cid);
        if(item) { item.set('order', index); }
      });
    },

  });

})();