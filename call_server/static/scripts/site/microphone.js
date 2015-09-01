/*global CallPower, Backbone, audioRecorder */

(function () {
  CallPower.Views.MicrophoneModal = Backbone.View.extend({
    tagName: 'div',
    className: 'microphone modal fade',

    events: {
      'change select.source': 'setSource',
      'click .nav-tabs': 'switchTab',
      'click .btn-record': 'onRecord',
      'change input[type="file"]': 'chooseFile',
      'blur textarea[name="text_to_speech"]': 'validateTextToSpeech',
      'submit': 'onSave'
    },

    initialize: function() {
      this.template = _.template($('#microphone-modal-tmpl').html(), { 'variable': 'modal' });
      _.bindAll(this, 'setup', 'confirmClose', 'destroy', 'getSources', 'streamError', 'connectRecorder', 'dataAvailable');
    },

    render: function(modal) {
      this.modal = modal;
      var html = this.template(modal);
      this.$el.html(html);

      this.$el.on('shown.bs.modal', this.setup);
      this.$el.on('hide.bs.modal', this.confirmClose);
      this.$el.on('hidden.bs.modal', this.destroy);
      this.$el.modal('show');

      return this;
    },

    setup: function() {
      if (this.isRecordingSupported()) {
        $('.nav-tabs a[href="#record"]', this.$el).tab('show');

        // get available sources (Chrome only)
        if (MediaStreamTrack.getSources !== undefined) {
          MediaStreamTrack.getSources( this.getSources );
        } else {
          this.setSource();
        }
      } else {
        // switch to upload tab
        $('.nav-tabs a[href="#upload"]', this.$el).tab('show');

        // disable record tab
        $('.nav-tabs a[href="#record"]', this.$el).parent('li').addClass('disabled')
          .attr('title','Sorry, recording is not supported in this browser.');
      }

      this.playback = $('audio[name="playback"]', this.$el);
    },

    isRecordingSupported: function() {
      return !!(navigator.getUserMedia || navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia || navigator.msGetUserMedia);
    },

    switchTab: function(event) {
      event.preventDefault();
      // set up tab behavior manually instead of relying on data-toggle
      // because we have multiple modals on the page and IDs could conflict

      var tabID = $(event.target).attr('href');
      var tab = $('.nav-tabs a[href="'+tabID+'"]', this.$el);
      if (!tab.parent('li').hasClass('disabled')) {
        tab.tab('show');
      }
      return true;
    },

    confirmClose: function(event) {
      if (this.recorder && this.recorder.state === 'recording') {
        return false;
      }

      if (!!this.playback.attr('src') && !this.saved) {
        // there is audio in the player, but not yet saved
        return confirm('You have recorded unsaved audio. Are you sure you want to close?');
      } else {
        return true;
      }
    },

    destroy: function() {
      if (this.recorder) {
        this.recorder.stop();
        this.meter.destroy();
      }
      this.undelegateEvents();
      this.$el.removeData().unbind();

      this.remove();
      Backbone.View.prototype.remove.call(this);
    },

    streamError: function(e) {
      this.recorder.state = "error";

      var msg = 'Please allow microphone access in the permissions popup.';
      if (window.chrome !== undefined) {
        msg = msg + '<br>You may need to remove this site from your media exceptions at <a href="">chrome://settings/content</a>';
      }
      window.flashMessage(msg, 'warning', true);
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

      var mediaConstraints = { audio: {
            mandatory: {
              // disable chrome filters
              googEchoCancellation: false,
              googAutoGainControl: false,
              googNoiseSuppression: false,
              googHighpassFilter: false
            }
        }
      };

      if (selectedSourceId) {
         // set selected source in config
        mediaConstraints.audio.optional = [{ sourceId: selectedSourceId }];
      } // if not, uses default

      navigator.getUserMedia(mediaConstraints, this.connectRecorder, this.streamError);
    },

    connectRecorder: function(stream) {
      var audioContext = new AudioContext;
      var source = audioContext.createMediaStreamSource(stream);

      var recorderConfig = {
        workerPath: '/static/dist/js/lib/recorderWorker.js',
        mp3LibPath: '/static/dist/js/lib/lame.all.js',
        vorbisLibPath: '/static/dist/js/lib/lame.all.js', // not really, but we only want mp3 recording
        // reuse exisiting path to avoid double downloading large emscripten compiled js
        recordAsMP3: true,
        bitRate: 8,

      };
      this.recorder  = audioRecorder.fromSource(source, recorderConfig);
      this.recorder.context = audioContext;
      this.recorder.source = source;
      this.recorder.state = 'inactive';

       // connect audio meter
      this.meter = new CallPower.Views.AudioMeter(this.recorder);
      this.meter.render();
    },

    onRecord: function(event) {
      event.preventDefault();

       // track custom state beyond what audioRecord.js provides

      if (this.recorder.state === 'error') {
        // reset source
        this.setSource();
      }
      else if (this.recorder.state === 'inactive') {
        // start recording
        this.recorder.record();
        this.recorder.state = 'recording';

        // show audio row and recording indicator
        $('.playback').show();
        $('.playback .status').addClass('active').show();

        // button to stop
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-record').addClass('glyphicon-stop');
        $('button.btn-record .text', this.$el).text('Stop');
      }
      else if (this.recorder.state === 'recording' || this.recorder.recording) {
        // stop recording
        this.recorder.stop();
        this.recorder.state = 'stopped';
        this.recorder.exportMP3(this.dataAvailable);

        $('.playback .status').removeClass('active').hide();

        // button to reset
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-stop').addClass('glyphicon-step-backward');
        $('button.btn-record .text', this.$el).text('Reset');
      }
      else if (this.recorder.state === 'stopped') {
        // clear buffers and restart
        this.recorder.clear();
        this.recorder.state = 'inactive';

        // clear playback
        this.playback.attr('controls', false);
        this.playback.attr('src', '');
        $('.playback').hide();

        // button to record
        $('button.btn-record .glyphicon', this.$el).removeClass('glyphicon-step-backward').addClass('glyphicon-record');
        $('button.btn-record .text', this.$el).text('Record');
      }
      else {
        console.error('recorder in invalid state');
      }
    },

    dataAvailable: function(data) {
      console.log('dataAvailable', this, data);
      this.audioBlob = data;
      this.playback.attr('controls', true);
      this.playback.attr('src',URL.createObjectURL(this.audioBlob));

      // reload media blob when done playing, because Chrome won't do it automatically
      this.playback.on('ended', function() {
        this.load();
      });
    },

    chooseFile: function() {
      this.filename = $('input[type="file"]').val().split(/(\\|\/)/g).pop();
      $('span.filename').text(this.filename);
    },

    validateTextToSpeech: function() {
      // TODO, run through simple jinja-like validator
      // provide auto-completion of available context?

      this.textToSpeech = $('textarea[name="text_to_speech"]').val();
    },

    validateField: function(parentGroup, validator, message) {
      // run validator for parentGroup, if present
      if (!parentGroup.length) {
        return true;
      }

      var isValid = validator(parentGroup);
      
      // put message in last help-block
      $('.help-block', parentGroup).last().text((!isValid) ? message : '');

      // toggle error states
      parentGroup.toggleClass('has-error', !isValid);
      return isValid;
    },


    validateForm: function() {
      var isValid = true;
      var self = this;

      if (!$('.tab-pane#record').hasClass('active')) {
        // if we are not on the recording tab, delete the blob
        delete this.audioBlob;
      }

      isValid = this.validateField($('.tab-pane.active#record'), function() {
        return !!self.playback.attr('src');
      }, 'Please record your message') && isValid;

      isValid = this.validateField($('.tab-pane.active#upload'), function() {
        return !!self.filename;
      }, 'Please select a file to upload') && isValid;

      isValid = this.validateField($('.tab-pane.active#text-to-speech'), function() {
        return !!self.textToSpeech;
      }, 'Please enter text to read') && isValid;

      return isValid;
    },

    onSave: function(event) {
      event.preventDefault();

      // change save button to spinner
      $('.btn.save .glyphicon')
        .removeClass('glyphicon-circle-arrow-down')
        .addClass('glyphicon-refresh')
        .addClass('glyphicon-spin');

      // submit file via ajax with html5 FormData
      // probably will not work in old IE
      var formData = new FormData();
      
      // add inputs individually, so we can control how we add files
      var formItems = $('form.modal-body', this.$el).find('input[type!="file"], select, textarea');
      _.each(formItems, function(item) {
        var $item = $(item);
        if ($item.val()) {
          formData.append($item.attr('name'), $item.val());
        }
      });
      // create file from blob
      if (this.audioBlob) {
        formData.append('file_storage', this.audioBlob);
      } else if (this.filename) {
        formData.append('file_storage', $('input[type="file"]')[0].files[0]);
      }

      var self = this;
      if (this.validateForm()) {
        $(this.$el).unbind('submit').submit();
        $.ajax($('form.modal-body').attr('action'), {
          method: "POST",
          data: formData,
          processData: false, // stop jQuery from munging our carefully constructed FormData
          contentType: false, // or faffing with the content-type
          success: function(response) {
            if (response.success) {
              // build friendly message like "Audio recording uploaded: Introduction version 3"
              var fieldDescription = $('form label[for="'+response.key+'"]').text();
              var msg = response.message + ': '+fieldDescription + ' version ' + response.version;
              // and display to user
              window.flashMessage(msg, 'success');

              // update parent form-group status and description
              var parentFormGroup = $('.form-group.'+response.key);
              parentFormGroup.addClass('valid');
              parentFormGroup.find('.input-group .help-block').text('');
              parentFormGroup.find('.description .status').addClass('glyphicon-check');

              // close the parent modal
              self.saved = true;
              self.$el.modal('hide');
            } else {
              console.error(response);
              window.flashMessage(response.errors, 'error', true);
            }
          },
          error: function(xhr, status, error) {
            console.error(status, error);
            window.flashMessage(response.errors, 'error');
          }
        });
        this.delegateEvents(); // re-bind the submit handler
        return true;
      }
      return false;
    },

  });

})();