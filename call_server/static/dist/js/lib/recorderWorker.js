var recLength = 0,
  recBuffersL = [],
  recBuffersR = [],
  bits        = 16,
  sampleRate,
    recordAsMP3 = false,
    recordAsOGG = false;


var recBufferMP3 =[];


var mp3Encoder;
var vorbisEncoder;

var mp3defaultConfig = { mode : 3,  channels:1};



vorbisdefaultConfig = {
  channels:1,
      quality: 1.0,
    sampleRate: sampleRate
};




this.onmessage = function(e){
  switch(e.data.command){
    case 'init':
      init(e.data.config);
      break;
    case 'record':
      record(e.data.buffer);
      break;
    case 'exportWAV':
      exportWAV(e.data.type);
      break;
    case 'getBuffer':
      getBuffer();
      break;

    case 'exportMP3':
      exportMP3();
      break;

    case 'exportOGG':
      exportOGG();
      break;
    case 'clear':
      clear();
      break;
  }
};

function init(config){
  sampleRate = config.sampleRate;
  mp3Encoder = new MP3Encoder({ mp3LibPath: config.mp3LibPath});
  vorbisEncoder = new VorbisEncoder({vorbisLibPath: config.vorbisLibPath})
  recordAsMP3 = config.recordAsMP3 || false;
  recordAsOGG = false;   // This has been giving me some problems



  if(recordAsMP3) mp3Encoder.init(mp3defaultConfig);
  if(recordAsOGG) {

    vorbisEncoder.init(vorbisdefaultConfig);
    vorbisEncoder.writeHeaders();

  }

}

function record(inputBuffer){
  recBuffersL.push(inputBuffer[0]);
  //recBuffersR.push(inputBuffer[1]);
  recLength += inputBuffer[0].length;


  if(recordAsMP3){


    var chunk = mp3Encoder.encode(inputBuffer[0]);



    if(chunk.length > 0){

      recBufferMP3.push(chunk);

    }



  }

  if(recordAsOGG){

    vorbisEncoder.encode([inputBuffer[0]]);
    vorbisEncoder.flush();
  }


}

function exportWAV(type){
  var bufferL = mergeBuffers(recBuffersL, recLength);
  //var bufferR = mergeBuffers(recBuffersR, recLength);
  //var interleaved = interleave(bufferL, bufferR);
  //var dataview = encodeWAV(interleaved);
  var dataview = encodeWAV(bufferL);
  var audioBlob = new Blob([dataview], { type: type });

  this.postMessage(audioBlob);
}

function exportMP3(){

  var mp3Blob;

  if(recordAsMP3){
    mp3Blob = mp3Encoder.getMP3();
  } else{
    var bufferL = mergeBuffers(recBuffersL, recLength);
    mp3Blob = mp3Encoder.toFile(bufferL, mp3defaultConfig);
  }


   this.postMessage(mp3Blob);


}


function exportOGG(){

  var oggBlob;

  if(recordAsOGG){
    oggBlob =vorbisEncoder.getOGG();

  } else{
    var bufferL = mergeBuffers(recBuffersL, recLength);
    oggBlob = vorbisEncoder.toFile([bufferL], vorbisdefaultConfig);
  }


  this.postMessage(oggBlob);


}


function getBuffer() {
  var buffers = [];
  buffers.push( mergeBuffers(recBuffersL, recLength) );
  buffers.push( mergeBuffers(recBuffersR, recLength) );
  this.postMessage(buffers);
}

function clear(){
  recLength = 0;
  recBuffersL = [];
  recBuffersR = [];
  recBufferMP3 = [];

}

function mergeBuffers(recBuffers, recLength){
  var result = new Float32Array(recLength);
  var offset = 0;
  for (var i = 0; i < recBuffers.length; i++){
    result.set(recBuffers[i], offset);
    offset += recBuffers[i].length;
  }
  return result;
}

function interleave(inputL, inputR){
  var length = inputL.length + inputR.length;
  var result = new Float32Array(length);

  var index = 0,
    inputIndex = 0;

  while (index < length){
    result[index++] = inputL[inputIndex];
    result[index++] = inputR[inputIndex];
    inputIndex++;
  }
  return result;
}

function floatTo16BitPCM(output, offset, input){
  for (var i = 0; i < input.length; i++, offset+=2){
    var s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
}

function writeString(view, offset, string){
  for (var i = 0; i < string.length; i++){
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}




function encodeWAV(samples){
  var buffer = new ArrayBuffer(44 + samples.length * 2);
  var view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* file length */
  view.setUint32(4, 32 + samples.length * 2, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw) */
  view.setUint16(20, 1, true);
  /* channel count */
  //view.setUint16(22, 2, true); /*STEREO*/
  view.setUint16(22, 1, true); /*MONO*/
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sample rate * block align) */
  //view.setUint32(28, sampleRate * 4, true); /*STEREO*/
  view.setUint32(28, sampleRate * 2, true); /*MONO*/
  /* block align (channel count * bytes per sample) */
  //view.setUint16(32, 4, true); /*STEREO*/
  view.setUint16(32, 2, true); /*MONO*/
  /* bits per sample */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, samples.length * 2, true);

  floatTo16BitPCM(view, 44, samples);

  return view;
}


var MP3Encoder = function(config){

  config = config ||{};
  var libLamePath = config.mp3LibPath || 'lame.all.js';
  importScripts(libLamePath);


  var lib = new lamejs();

  var mp3encoder;

  function init(config){

    mp3encoder = new lib.Mp3Encoder(config.cannels ||1, config.sampleRate ||  44100, config.bitRate ||128); //mono 44.1khz encode to 128kbps
  }

  function encode(buffer){


    var input = float32ToInt(buffer);

    var output = mp3encoder.encodeBuffer(input);

    return output;
  }


  function float32ToInt(f32){


    var len = f32.length, i = 0;
    var i16 = new Int16Array(len);

    while(i < len)
      i16[i] = convert(f32[i++]);

    function convert(n) {
      var v = n < 0 ? n * 32768 : n * 32767;       // convert in range [-32768, 32767]
      return Math.max(-32768, Math.min(32768, v)); // clamp
    }

    return i16;

  }



  function finish(){
      return mp3encoder.flush();
  }

  function flush(){
    return mp3encoder.flush();
  }

  function toFile(buffer, config){

    init(config);

    var mp3data =  [encode(buffer)];

    mp3data.push(finish());

    var mp3Blob = new Blob(mp3data, {type: 'audio/mp3'});

    return mp3Blob;

  }

  function getMP3(){


    var mp3Blob = new Blob(recBufferMP3, {type: 'audio/mp3'});
    return mp3Blob;
  }


  this.init = init;
  this.encode = encode;
  this.toFile = toFile;
  this.getMP3 = getMP3;
  this.flush = flush;



};



var VorbisEncoder = function(config){

  var state = null;

  var libPath = config.vorbisLibPath || 'libvorbis.module.min.js';

  importScripts(libPath);

  var encoderData = [];

  function init(options){

        flush();
        encoderData = [];

    state = Module.lib.encoder_create_vbr(
        options.channels ||1,
        options.sampleRate || 44100,
        options.quality || 0.7
    );

    if (state === 0) {
        // error handling
    }

  }


  function clear(){
    encoderData = [];
    Module.lib.encoder_clear_data(state);
  }

  function flush(){

    var data = Module.lib.helpers.get_data(state);

    if (data.length === 0) {
      return null;
    }

    Module.lib.encoder_clear_data(state);
    encoderData.push(data);

  }

  function writeHeaders(){

    Module.lib.encoder_write_headers(state);

  }

  function encode(buffers){


    buffers = buffers.map(function (typed) {
      return typed.buffer;
    });

    buffers = buffers.map(function (buffer) {
      return new Float32Array(buffer);
    });

    var samples = buffers[0].length;

    Module.lib.helpers.encode(state, samples, buffers);

  }

  function finish (){
    Module.lib.encoder_finish(state);
    Module.lib.encoder_destroy(state);
  }


  function makeBlob(){

    return new Blob(encoderData, { type: 'audio/ogg' });
  }

  function getOGG(){

    finish();
    flush();

    return makeBlob();

  }



  function toFile (buffers, options){

    init(options);
    writeHeaders();
    encode(buffers);
    finish();
    flush();

    return makeBlob();


  }

  this.init = init;

  this.writeHeaders = writeHeaders;
  this.toFile = toFile;
  this.flush = flush;
  this.encode = encode;

  this.getOGG = getOGG;

};


