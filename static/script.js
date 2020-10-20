'use strict'

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

let log = console.log.bind(console),
  id = val => document.getElementById(val),
  ul = id('ul'),
  gUMbtn = id('gUMbtn'),
  usernameInput = id('usernameInput'),
  start = id('start'),
  stop = id('stop'),
  recordAnimation = id('recording-indicator'),
  stream,
  recorder,
  counter = 1,
  chunks,
  media;

gUMbtn.onclick = e => {
  let mv = id('mediaVideo'),
    mediaOptions = {
      audio: {
        tag: 'audio',
        type: 'audio/wav',
        ext: '.wav',
        gUM: { audio: true }
      }
    };
  media = mediaOptions.audio;
  if (media == null) {
    alert("Could not connect to audio recorder");
  }
  navigator.mediaDevices.getUserMedia(media.gUM).then(_stream => {
    stream = _stream;
    id('btns').style.display = 'inherit';
    start.removeAttribute('disabled');
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => {
      chunks.push(e.data);
      if (recorder.state == 'inactive') makeLink();
    };
    log('got media successfully');
  }).catch(log);
  gUMbtn.style.display = 'none';

}

start.onclick = e => {
  recordAnimation.style.display = 'inline';
  start.disabled = true;
  stop.removeAttribute('disabled');
  chunks = [];
  recorder.start();
}


stop.onclick = e => {
  stop.disabled = true;
  recordAnimation.style.display = 'none';
  recorder.stop();
  start.removeAttribute('disabled');
}



function makeLink() {
  let uploadButton = document.createElement("BUTTON");
  uploadButton.style.marginLeft = "13px"
  let downloadButton = document.createElement("BUTTON");
  downloadButton.style.marginLeft = "13px"
  let blob = new Blob(chunks, { type: media.type })
    , url = URL.createObjectURL(blob)
    , li = document.createElement('li')
    , mt = document.createElement(media.tag)
    , hf = document.createElement('a')

    ;
  mt.controls = true;
  mt.style.display = 'block';
  mt.style.marginTop = "15px"

  mt.src = url;
  hf.href = url;
  hf.download = `${counter++}${media.ext}`;
  hf.appendChild(downloadButton)
  downloadButton.innerHTML = `Download ${hf.download}`;

  uploadButton.innerHTML = "Upload Recording";
  uploadButton.onclick = e => {
    const data = new FormData()
    const temp = window.location.href.split('/')
    const itemValue = temp[temp.length - 1]
    const userName = getCookie("midas-username")
    log("username: ", userName);
    data.append('file', blob, `${itemValue},${userName}`)

    axios({
      method: 'post',
      url: "/receive",
      data: data,
      headers: {
        'Content-Type': `multipart/form-data; boundary=${data._boundary}`,
      }
    })
  }

  li.appendChild(mt);
  li.appendChild(hf);
  li.appendChild(uploadButton);
  ul.appendChild(li);
}
