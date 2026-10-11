/* The story "مغامرة قطّورة والأبواب الثلاثة" (Qattoura and the three doors), Grade 3 science, water cycle.
   Strategy: immersive storytelling. The pupil helps Qattoura through three doors:
     right door  -> the sea: evaporation
     left door   -> the sky: condensation
     middle door -> comparing the two (similarities and differences)
   Needs parts.js. The story has no sound at all: it is told by the text panels.
   All lines and cards are in the tables at the top of this file. */
(function () {
  'use strict';

  /* ---------------------------------------------------------------- wording */
  var SPEAKERS = {
    qattoura: { name: 'قطّورة', accent: '#0b6fb8', border: '#5aa9e6' },
    friends: { name: 'القطرات', accent: '#0b8f6a', border: '#63c888' },
    cloud: { name: 'الغيمة', accent: '#5b6f8a', border: '#b7c6d8' },
    door: { name: 'الباب', accent: '#8a5a2b', border: '#d9a441' }
  };
  var LINES = {
    H1a: ['qattoura', 'أهلًا بك يا بطل! أنا قطّورة.'],
    H1b: ['qattoura', 'أضعتُ صديقاتي القطرات. هل تساعدني؟'],
    H1c: ['qattoura', 'اضغط الباب الأيمن لنبحث عنهنّ.'],
    notNow: ['qattoura', 'ليس الآن! اضغط الباب الذي يلمع.'],
    S1a: ['qattoura', 'هذا هو البحر! صديقاتي هنا.'],
    S1b: ['qattoura', 'انظر حولك، واضغط كل قطرة تجدها.'],
    S2a: ['qattoura', 'لماذا أنتنّ منزعجات؟'],
    S2b: ['friends', 'حرارة الشمس تسخّننا!'],
    S3a: ['qattoura', 'اضغط الشمس لترى ماذا تفعل حرارتها.'],
    S3b: ['qattoura', 'نحن نتحول إلى بخار ماء!'],
    S3c: ['qattoura', 'بخار الماء غاز لا تراه العين! سنضيء لك نجمة صغيرة لتتابعنا.'],
    S3d: ['qattoura', 'بخار الماء يصعد إلى أعلى!'],
    H2: ['qattoura', 'رائع! والآن اضغط الباب الأيسر لنعرف ماذا يحدث في الأعلى.'],
    K1a: ['door', 'أهلًا بكم في السماء الباردة!'],
    K1b: ['qattoura', 'ما أبرد الجو هنا! ما زلنا بخار ماء لا تراه العين.'],
    K1c: ['qattoura', 'اضغط كل نجمة لترى ماذا تفعل البرودة.'],
    K2: ['qattoura', 'بردتُ فصرتُ قطرة ماء سائلة!'],
    K3a: ['cloud', 'برد بخار الماء، فتحوّل إلى قطرات ماء سائلة.'],
    K3b: ['cloud', 'ثم تجمّعت القطرات، فتكوّنت غيمة.'],
    K3c: ['cloud', 'هذا هو التكثف!'],
    H3a: ['door', 'لن أُفتح حتى تساعدوني!'],
    H3b: ['door', 'قارنوا بين التبخر والتكثف في دورة الماء.'],
    H3c: ['door', 'ضع كل بطاقة في مكانها: التبخر، أو التكثف، أو التشابه بينهما.'],
    C2: ['qattoura', 'أحسنت يا بطل! عرفتَ كيف نقارن بين التبخر والتكثف.']
  };
  var SEA_BOARD = { title: 'التبخر', rows: ['حرارة الشمس تسخّن ماء البحر.', 'يتحول الماء السائل إلى بخار ماء.', 'يصعد بخار الماء إلى أعلى.'] };

  /* Comparison cards. target: E = evaporation, C = condensation, S = similarity. why: shown after a wrong choice. */
  var CARDS = {
    e1: { target: 'E', text: 'المكان: عند سطح البحر', why: 'في دورة الماء يتبخر الماء عند سطح البحر. هذا يخص التبخر.' },
    e2: { target: 'E', text: 'السبب: التسخين بحرارة الشمس', why: 'حرارة الشمس تسخّن الماء فيتبخر. هذا يخص التبخر.' },
    e3: { target: 'E', text: 'التحول: من حالة سائلة إلى حالة غازية', why: 'الماء السائل يصير بخار ماء في التبخر.' },
    e4: { target: 'E', text: 'بعدها: يصعد بخار الماء إلى أعلى', why: 'في دورة الماء يصعد بخار الماء بعد التبخر. هذا يخص التبخر.' },
    c1: { target: 'C', text: 'المكان: في الأعلى، في السماء', why: 'في دورة الماء يتكثف بخار الماء في الأعلى، في السماء.' },
    c2: { target: 'C', text: 'السبب: التبريد ببرودة الجو', why: 'بخار الماء يبرد في الأعلى فيتكثف. هذا يخص التكثف.' },
    c3: { target: 'C', text: 'التحول: من حالة غازية إلى حالة سائلة', why: 'بخار الماء يصير ماء سائلًا في التكثف.' },
    c4: { target: 'C', text: 'بعدها: تتشكل الغيوم', why: 'في دورة الماء تتشكل الغيوم بعد التكثف. هذا يخص التكثف.' },
    s1: { target: 'S', text: 'مرحلة من مراحل دورة الماء', why: 'التبخر والتكثف كلاهما من مراحل دورة الماء. هذا تشابه.' },
    s2: { target: 'S', text: 'تتغير فيها حالة الماء', why: 'في التبخر وفي التكثف تتغير حالة الماء. هذا تشابه.' }
  };
  var CARD_ORDER = ['e2', 'c2', 'e3', 'c3', 's1', 's2', 'e1', 'c1', 'e4', 'c4'];
  var BOARDS = {
    E: { title: 'التبخر في دورة الماء', accent: '#c9620a', border: '#ff9d3d', min: 4 },
    C: { title: 'التكثف في دورة الماء', accent: '#0b6fb8', border: '#5aa9e6', min: 4 },
    S: { title: 'التشابه', accent: '#1f8a4d', border: '#63c888', min: 2 }
  };

  /* ---------------------------------------------------------------- places (tuned by eye in the browser)
     yaw: the direction of the photograph that is put straight ahead. sun: where the sun is in the photograph. */
  var ENV = {
    hub: { file: 'env/hub.jpg', yaw: -6, light: { at: { x: 1.5, y: 5, z: 6 }, power: 1.25 }, env: 1.7 },
    sea: { file: 'env/sea.jpg', yaw: 6, sun: { yaw: 50.5, pitch: 32.5 }, light: { yaw: 50.5, pitch: 32.5, power: 1.15 }, env: 1.0 },
    sky: { file: 'env/sky.jpg', yaw: -42, sun: { yaw: 33.5, pitch: 49.5 }, light: { yaw: 33.5, pitch: 49.5, power: 1.0 }, env: 1.15 }
  };
  var EYE = 1.6;
  var DOORS = [
    { key: 'evaporation', yaw: 31, dist: 5.6, open: 1.2, tall: 2.35, portal: 'env/portal-sea.jpg', leaves: [['leaf', -1]] },
    { key: 'compare', yaw: 0, dist: 5.4, open: 2.1, tall: 2.55, portal: null, leaves: [['leaf_R', -1], ['leaf_L', 1]] },
    { key: 'condensation', yaw: -31, dist: 5.6, open: 1.15, tall: 2.6, portal: 'env/portal-sky.jpg', leaves: [['leaf', -1]] }
  ];
  var DOOR_STEP = 0.24, DROP = 0.42;                     // height of the stone steps; size of Qattoura
  var MODELS = ['drop', 'drop-sad', 'arrow-heat', 'arrow-up', 'door-evaporation', 'door-condensation', 'door-compare'];
  var PICTURES = ['env/hub.jpg', 'env/sea.jpg', 'env/sky.jpg', 'env/portal-sea.jpg', 'env/portal-sky.jpg',
    'textures/cloud-1.png', 'textures/cloud-2.png', 'textures/cloud-3.png', 'textures/cloud-4.png'];

  /* ---------------------------------------------------------------- small helpers */
  var D2R = Math.PI / 180;
  function $(id) { return document.getElementById(id); }
  function words(text) { return text.split(/\s+/).length; }
  /* a point on the ground circle round the viewer: yaw in degrees (0 = straight ahead, positive to the right) */
  function polar(yaw, dist, y) { return { x: Math.sin(yaw * D2R) * dist, y: y || 0, z: -Math.cos(yaw * D2R) * dist }; }
  /* a direction given in the photograph of the current place, as a point at the given distance from the eye */
  function photoPoint(place, yaw, pitch, dist) {
    var a = (yaw - ENV[place].yaw) * D2R, p = pitch * D2R;
    return { x: Math.cos(p) * Math.sin(a) * dist, y: EYE + Math.sin(p) * dist, z: -Math.cos(p) * Math.cos(a) * dist };
  }
  function vec(p) { return p.x + ' ' + p.y + ' ' + p.z; }
  function mk(parent, attrs, tag) {
    var e = document.createElement(tag || 'a-entity');
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    parent.appendChild(e);
    return e;
  }
  function easeInOut(k) { return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; }
  function easeOut(k) { return 1 - Math.pow(1 - k, 3); }
  function easeBack(k) { var c = 1.70158; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); }

  /* ---------------------------------------------------------------- engine: clock, tweens, waits, taps
     Time comes from the render loop, not from setTimeout, so the story runs the same in a hidden test tab.
     A restart rejects everything that is waiting with STALE; the scene functions simply stop. */
  var STALE = { stale: true };
  var S = {
    scene: null, stage: null, world: null, sky: null, speech: null,
    clock: 0, tweens: [], timers: [], waiting: [], expect: null, skipLine: null,
    state: 'start', remaining: [], done: {}, drops: [], riseSnapshot: null, cloudStage: 0, stars: [], rows: null
  };

  function pending(executor) {
    return new Promise(function (res, rej) {
      var entry = { rej: rej };
      S.waiting.push(entry);
      function settle() { var i = S.waiting.indexOf(entry); if (i !== -1) { S.waiting.splice(i, 1); } }
      executor(function (v) { settle(); res(v); }, function (e) { settle(); rej(e); });
    });
  }
  function wait(seconds) {
    return pending(function (res) { S.timers.push({ at: S.clock + seconds, res: res }); });
  }
  /* fn(k) is called every frame with k going from 0 to 1 */
  function tween(seconds, fn, ease) {
    return pending(function (res) { fn(0); S.tweens.push({ t0: S.clock, dur: Math.max(0.001, seconds), fn: fn, ease: ease || easeInOut, res: res }); });
  }
  function moveTo(el, to, seconds, ease) {
    var o = el.object3D, from = o.position.clone(), end = new THREE.Vector3(to.x, to.y, to.z);
    return tween(seconds, function (k) { o.position.lerpVectors(from, end, k); }, ease);
  }
  function scaleTo(el, to, seconds, ease) {
    var o = el.object3D, from = o.scale.x;
    return tween(seconds, function (k) { var s = from + (to - from) * k; o.scale.set(s, s, s); }, ease);
  }
  function fadeAttr(el, component, to, seconds) {
    var data = el.getAttribute(component), from = data && data.opacity !== undefined ? data.opacity : 1;
    return tween(seconds, function (k) { el.setAttribute(component, 'opacity', from + (to - from) * k); });
  }
  function waitTap(ids) {
    return pending(function (res) { S.expect = { ids: ids, res: res }; });
  }
  function engineTick(dt) {
    S.clock += Math.min(dt, 100) / 1000;
    var i;
    for (i = S.tweens.length - 1; i >= 0; i--) {
      var tw = S.tweens[i], k = Math.min(1, (S.clock - tw.t0) / tw.dur);
      tw.fn(tw.ease(k));
      if (k >= 1) { S.tweens.splice(i, 1); tw.res(); }
    }
    for (i = S.timers.length - 1; i >= 0; i--) {
      if (S.clock >= S.timers[i].at) { var tm = S.timers[i]; S.timers.splice(i, 1); tm.res(); }
    }
  }
  function dropEverything() {
    var waiting = S.waiting;
    S.waiting = []; S.tweens = []; S.timers = []; S.expect = null; S.skipLine = null;
    waiting.forEach(function (w) { w.rej(STALE); });
  }

  /* One tap, from a real click or from the test hook. */
  function tap(id) {
    if (S.expect && S.expect.ids.indexOf(id) !== -1) {
      var e = S.expect; S.expect = null; e.res(id);
      return true;
    }
    if (id.indexOf('door-') === 0 && S.expect && S.expect.ids.some(function (x) { return x.indexOf('door-') === 0; }) && !S.busyHint) {
      S.busyHint = true;                                   // a door that is not open for use yet

      hint(LINES.notNow).then(function () { S.busyHint = false; }, function () { S.busyHint = false; });
    }
    return false;
  }
  function hit(parent, id, geometry, position) {
    var e = mk(parent, { geometry: geometry, material: 'shader: flat; opacity: 0; transparent: true; depthWrite: false', position: position || '0 0 0' });
    e.classList.add('clickable');
    e.addEventListener('click', function () { tap(id); });
    return e;
  }

  /* ---------------------------------------------------------------- speech panel */
  var anchorOf = {};                                       // speaker -> function returning the world position to speak from
  var tmp = new THREE.Vector3(), camPos = new THREE.Vector3();
  var READ_AT = 3.3;                                       // metres from the eye: the same letter size wherever the speaker is
  var VIEW_LIMIT = 16 * D2R, SPEAKER_LIMIT = 33 * D2R, CUE_FROM = 36 * D2R, UP_LIMIT = 17 * D2R, DOWN_LIMIT = -13 * D2R;
  var look = new THREE.Vector3(), want = new THREE.Vector3();
  function wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); }
  function clamp(v, limit) { return Math.max(-limit, Math.min(limit, v)); }
  /* Where the speech panel belongs right now. It starts in the direction of its speaker and is drawn towards the middle
     of the pupil's view, but never further than 33 degrees from the speaker. When that leaves it outside the view,
     a chevron at the edge of the screen shows which way to turn. Called every frame while a line is shown. */
  function placeSpeech(who, snap) {
    var get = anchorOf[who] || anchorOf.qattoura, p = get ? get() : new THREE.Vector3(0, 2.2, -3.5);
    S.scene.camera.getWorldPosition(camPos);
    S.scene.camera.getWorldDirection(look);
    tmp.copy(p).sub(camPos);
    var far = tmp.length(), dist = Math.min(READ_AT, Math.max(1.6, far - 0.5));
    var yawView = Math.atan2(look.x, -look.z), yawSpeaker = Math.atan2(tmp.x, -tmp.z);
    var yaw = yawView + clamp(wrap(yawSpeaker - yawView), VIEW_LIMIT);          // as near to the middle of the view as 16 degrees
    yaw = yawSpeaker + clamp(wrap(yaw - yawSpeaker), SPEAKER_LIMIT);            // but within 33 degrees of the speaker
    var pitch = Math.max(DOWN_LIMIT, Math.min(UP_LIMIT, Math.atan2(tmp.y, Math.sqrt(tmp.x * tmp.x + tmp.z * tmp.z))));
    want.set(camPos.x + Math.cos(pitch) * Math.sin(yaw) * dist, camPos.y + Math.sin(pitch) * dist, camPos.z - Math.cos(pitch) * Math.cos(yaw) * dist);
    if (snap) { S.speech.object3D.position.copy(want); } else { S.speech.object3D.position.lerp(want, 0.14); }
    var aside = wrap(yaw - yawView);
    cue(aside > CUE_FROM ? 1 : aside < -CUE_FROM ? -1 : 0);
  }
  function cue(side) {
    if (S.cueSide === side) { return; }
    S.cueSide = side;
    $('cueRight').object3D.visible = side > 0;
    $('cueLeft').object3D.visible = side < 0;
  }
  function speechTick() {
    var d = S.speaker && S.speech.getAttribute('ar-text');
    if (d && d.opacity > 0.01) { placeSpeech(S.speaker, false); } else { cue(0); }
  }
  function showLine(who, text) {
    var sp = SPEAKERS[who];
    S.speaker = who;
    placeSpeech(who, true);
    S.lineSeq = (S.lineSeq || 0) + 1;
    S.speech.setAttribute('ar-text', { title: sp.name, value: text, accent: sp.accent, border: sp.border, opacity: 1 });
    S.speech.object3D.visible = true;
  }
  function hideLine() { S.lineSeq = (S.lineSeq || 0) + 1; S.speech.setAttribute('ar-text', 'opacity', 0); }

  /* Shows one line. It ends when its reading time is over (2.5 seconds plus 0.45 for every word), or when skipped. */
  function say(line, opts) {
    var who = line[0], text = line[1];
    opts = opts || {};
    showLine(who, text);
    var time = opts.seconds || (2.5 + 0.45 * words(text));
    var skipped = pending(function (res) { S.skipLine = res; });
    var seq = S.lineSeq;
    return Promise.race([wait(time), skipped]).then(function () {
      if (S.skipLine) { var r = S.skipLine; S.skipLine = null; r(); }
      if (!opts.keep && S.lineSeq === seq) { hideLine(); }
    });
  }
  /* An instruction: the line stays on screen and the pupil may tap at once, without waiting for the reading time. */
  function ask(line, ids) {
    showLine(line[0], line[1]);
    return waitTap(ids);
  }
  /* A side remark that does not belong to the main thread of the story (the "not now" line). */
  function hint(line) {
    var before = S.speech.getAttribute('ar-text'), was = { title: before.title, value: before.value, accent: before.accent, border: before.border, opacity: before.opacity };
    var speaker = S.speaker;
    showLine(line[0], line[1]);
    var seq = S.lineSeq;
    return wait(2.6).then(function () {
      if (S.lineSeq !== seq) { return; }                   // the story has moved on meanwhile: leave its line alone
      S.speaker = speaker;
      S.speech.setAttribute('ar-text', was);
    });
  }
  function skip() {
    if (S.skipLine) { var r = S.skipLine; S.skipLine = null; r(); return true; }
    return false;
  }

  /* ---------------------------------------------------------------- scene changes */
  function fade(to, seconds) {
    var mesh = $('fade').getObject3D('mesh');
    var from = mesh.material.opacity;
    mesh.visible = true;
    return tween(seconds, function (k) { mesh.material.opacity = from + (to - from) * k; }).then(function () { mesh.visible = to > 0.003; });
  }
  function clearWorld() {
    while (S.world.firstChild) { S.world.removeChild(S.world.firstChild); }
    S.drops = []; S.stars = []; anchorOf = {};
    hideLine();
  }
  /* Turn the whole stage so that "straight ahead" of the new place is where the pupil is looking now. */
  function faceThePupil() {
    var d = new THREE.Vector3();
    S.scene.camera.getWorldDirection(d);
    S.stage.object3D.rotation.y = -Math.atan2(d.x, -d.z);
    S.stage.object3D.updateMatrixWorld(true);
  }
  /* Resolves when the entity shows its model. A model that fails, or is still missing after 5 seconds, is a fault:
     the promise rejects and the story stops with the on-screen message instead of going on without an actor. */
  function modelReady(el) {
    if (el.getObject3D('mesh')) { return Promise.resolve(); }
    var shown = pending(function (res, rej) {
      el.addEventListener('model-loaded', function () { res(); }, { once: true });
      el.addEventListener('model-error', function () { rej(new Error('model ' + el.getAttribute('q-model'))); }, { once: true });
    });
    var late = wait(5).then(function () {
      if (!el.getObject3D('mesh')) { throw new Error('model late ' + el.getAttribute('q-model')); }
    });
    return Promise.race([shown, late]);
  }
  function modelsReady(root) {
    return Promise.all(Array.prototype.slice.call(root.querySelectorAll('[q-model]')).map(modelReady));
  }
  function setLight(place) {
    var l = ENV[place].light, p = l.at || photoPoint(place, l.yaw, l.pitch, 30);     // hub: lit from the pupil's side
    var sun = $('sunlight');
    sun.object3D.position.set(p.x, p.y, p.z);
    sun.setAttribute('light', 'intensity', l.power);
  }
  /* White out, swap the photograph and the actors, white in. build(group) creates the actors of the new place. */
  function goTo(place, build) {
    return fade(1, 0.7).then(function () {
      clearWorld();
      faceThePupil();
      setLight(place);
      return pending(function (res, rej) { S.sky.components['photo-sky'].show(ENV[place].file, ENV[place].yaw).then(res, rej); });
    }).then(function () {
      var group = mk(S.world, {});
      build(group);
      return modelsReady(group).then(function () { return group; });
    }).then(function (group) {
      return fade(0, 0.9).then(function () { return group; });
    });
  }

  /* ---------------------------------------------------------------- actors */
  function addDrop(parent, id, pos, opts) {
    opts = opts || {};
    var size = (opts.size || 1) * DROP;
    var holder = mk(parent, { position: vec(pos), 'face-camera': 'upright: true' });
    var model = mk(holder, { 'q-model': opts.sad ? 'drop-sad' : 'drop', 'animation-mixer': 'clip: *; loop: repeat',
      'model-look': { opacity: opts.opacity === undefined ? 1 : opts.opacity, tint: opts.tint || '#ffffff', env: 0.7 },
      scale: size + ' ' + size + ' ' + size, position: '0 ' + (1.24 * size) + ' 0' });
    var drop = { id: id, holder: holder, model: model, size: size };
    S.drops.push(drop);
    return drop;
  }
  function dropOpacity(drop, to, seconds) {
    var from = drop.model.getAttribute('model-look').opacity;
    if (to > 0) { drop.holder.object3D.visible = true; }
    return tween(seconds, function (k) { drop.model.setAttribute('model-look', 'opacity', from + (to - from) * k); })
      .then(function () { if (to <= 0.003) { drop.holder.object3D.visible = false; } });
  }
  function headOf(drop) {
    return function () { var v = new THREE.Vector3(); drop.holder.object3D.getWorldPosition(v); v.y += 2.6 * drop.size + 0.85; return v; };
  }
  /* The marker for water vapour: vapour is an invisible gas, so a small star shows the pupil where it is. */
  function addStar(parent, id, pos) {
    var el = mk(parent, { position: vec(pos), 'face-camera': '', bob: 'height: 0.1; speed: 1.9; phase: ' + (S.stars.length * 1.7) });
    var pic = mk(el, { 'soft-picture': 'kind: star; size: 0.9; add: true; opacity: 0', pulse: 'amount: 0.22; speed: 4.2' });
    var star = { id: id, el: el, pic: pic };
    S.stars.push(star);
    return star;
  }
  function starOpacity(star, to, seconds) { return fadeAttr(star.pic, 'soft-picture', to, seconds); }
  function ring(parent, pos, size) {
    return mk(parent, { position: vec(pos), 'face-camera': '', 'soft-picture': 'kind: ring; size: ' + size + '; add: true; opacity: 0.95', pulse: 'amount: 0.16; speed: 4' });
  }
  function board(parent, kind, pos, width, rows) {
    var b = BOARDS[kind];
    return mk(parent, { position: vec(pos), 'face-camera': '',
      'ar-text': { title: b.title, value: (rows || []).join('|'), rows: true, minLines: b.min, width: width, size: 58, accent: b.accent, border: b.border } });
  }

  /* ---------------------------------------------------------------- the hub with the three doors */
  var hub = null;
  function buildHub(group, active) {
    hub = { doors: {}, group: group };
    DOORS.forEach(function (d) {
      var p = polar(d.yaw, d.dist, 0);
      var holder = mk(group, { position: vec(p), rotation: '0 ' + (-d.yaw) + ' 0' });
      var model = mk(holder, { 'q-model': 'door-' + d.key, 'model-look': { env: ENV.hub.env } });
      mk(holder, { position: '0 0.03 0.25', 'soft-picture': 'kind: shadow; size: ' + (d.open * 2.6) + '; flat: true; opacity: 0.8' });
      var midY = DOOR_STEP + d.tall / 2;
      if (d.portal) {                                      // what is seen through the door once it is open
        mk(holder, { position: '0 ' + midY + ' -0.1', picture: { src: d.portal, width: d.open + 0.5, height: d.tall + 0.9, opacity: 1, order: 1 } });
      } else {
        mk(holder, { position: '0 ' + midY + ' -0.1', scale: (d.open + 0.4) + ' ' + (d.tall + 0.7) + ' 1', 'soft-picture': 'kind: gold; size: 1; opacity: 1' });
      }
      hit(holder, 'door-' + d.key, 'primitive: box; width: ' + (d.open + 0.9) + '; height: ' + (d.tall + 1) + '; depth: 0.5', '0 ' + (midY + 0.2) + ' 0.1');
      var entry = { def: d, holder: holder, model: model, ring: null, opened: false };
      hub.doors[d.key] = entry;
      if (S.done[d.key]) {
        mk(holder, { position: (d.open / 2 + 0.3) + ' ' + (DOOR_STEP + d.tall + 0.95) + ' 0.45', 'face-camera': '', 'soft-picture': 'kind: medal; size: 0.62; opacity: 1' });
        model.addEventListener('model-loaded', function () { setLeaves(entry, 1); }, { once: true });
        if (model.getObject3D('mesh')) { setLeaves(entry, 1); }
      }
      if (d.key === active) { entry.ring = ring(holder, { x: 0, y: midY, z: 0.75 }, d.open * 0.95); }
    });
    anchorOf.door = function () { var v = new THREE.Vector3(); hub.doors.compare.holder.object3D.getWorldPosition(v); v.y = 3.3; v.z += 0; return v; };
  }
  function setLeaves(entry, k) {
    var root = entry.model.getObject3D('mesh');
    if (!root) { return; }
    entry.def.leaves.forEach(function (lf) {
      var node = root.getObjectByName(lf[0]);
      if (node) { node.rotation.y = lf[1] * 1.72 * k; }
    });
    entry.opened = k > 0.5;
  }
  function openDoor(entry, seconds) {

    if (entry.ring) { entry.ring.parentNode.removeChild(entry.ring); entry.ring = null; }
    return tween(seconds || 1.5, function (k) { setLeaves(entry, k); }, easeInOut);
  }
  function hubDoorIds() { return DOORS.map(function (d) { return 'door-' + d.key; }); }

  /* H1 and H2: Qattoura sends the pupil to one door */
  function hubStep(stateId, lines, doorKey) {
    S.state = stateId;
    return goTo('hub', function (group) {
      buildHub(group, doorKey);
      var q = addDrop(group, 'qattoura', polar(0, 3.1, 0));
      anchorOf.qattoura = headOf(q);
    }).then(function () {
      return lines.slice(0, -1).reduce(function (p, id) {
        return p.then(function () { return say(LINES[id]); });
      }, Promise.resolve());
    }).then(function () {
      return ask(LINES[lines[lines.length - 1]], ['door-' + doorKey]);
    }).then(function () {
      hideLine();
      return openDoor(hub.doors[doorKey]);
    }).then(function () { return wait(0.5); });
  }

  /* ---------------------------------------------------------------- the sea: evaporation */
  function seaScene() {
    var q, friends = [], sunPos, glow, sunRing, heat, up, gather = polar(0, 5.6, 0.12);
    return goTo('sea', function (group) {
      q = addDrop(group, 'qattoura', polar(-15, 3.0, 0));
      anchorOf.qattoura = headOf(q);
      [[-36, 6.8, '#bfe6ff'], [9, 7.4, '#d9d2ff'], [36, 6.0, '#bff5e6']].forEach(function (f, i) {
        var d = addDrop(group, 'friend-' + (i + 1), polar(f[0], f[1], 0.12), { sad: true, size: 0.9, tint: f[2] });
        d.holder.setAttribute('bob', 'height: 0.07; speed: 1.5; phase: ' + i * 2);
        d.hit = hit(d.holder, 'friend-' + (i + 1), 'primitive: sphere; radius: 0.85', '0 0.5 0');
        d.ring = ring(d.holder, { x: 0, y: 0.5, z: 0.5 }, 1.5);
        friends.push(d);
      });
      anchorOf.friends = headOf(friends[1]);
      var s = ENV.sea.sun;
      sunPos = photoPoint('sea', s.yaw, s.pitch, 40);
      glow = mk(group, { position: vec(sunPos), 'face-camera': '', 'soft-picture': 'kind: glow; size: 13; add: true; opacity: 0.55' });
      var from = photoPoint('sea', s.yaw, s.pitch, 13), to = { x: gather.x + 0.3, y: 0.9, z: gather.z };
      heat = mk(group, { 'flow-arrows': { model: 'arrow-heat', from: from, to: to, count: 6, length: 2.0, thick: 2.3, speed: 0.2, spread: 0.8, glow: '#a82400', strength: 0 } });
      up = mk(group, { 'flow-arrows': { model: 'arrow-up', from: { x: gather.x, y: 1.2, z: gather.z }, to: { x: gather.x, y: 9.5, z: gather.z }, count: 5, length: 1.7, thick: 2.7, speed: 0.24, spread: 1.25, glow: '#0a3f8f', strength: 0 } });
    }).then(function () {
      S.state = 'S1';
      return say(LINES.S1a);
    }).then(function () {
      showLine(LINES.S1b[0], LINES.S1b[1]);
    }).then(function findAll() {
      var left = friends.filter(function (f) { return !f.found; });
      if (!left.length) { return null; }
      return waitTap(left.map(function (f) { return f.id; })).then(function (id) {
        var f = friends.filter(function (x) { return x.id === id; })[0];
        f.found = true;

        f.ring.parentNode.removeChild(f.ring); f.hit.parentNode.removeChild(f.hit);
        var k = friends.indexOf(f), slot = { x: gather.x + (k - 1) * 1.05, y: 0.12, z: gather.z + (k === 1 ? -0.5 : 0.1) };
        moveTo(f.holder, slot, 1.5, easeInOut);
        return findAll();
      });
    }).then(function () {
      S.state = 'S2';
      hideLine();
      return moveTo(q.holder, { x: gather.x - 0.25, y: 0.12, z: gather.z + 0.95 }, 1.6);
    }).then(function () {
      return say(LINES.S2a);
    }).then(function () {
      return say(LINES.S2b);
    }).then(function () {
      S.state = 'S3';
      sunRing = ring(S.world.firstChild, photoPoint('sea', ENV.sea.sun.yaw, ENV.sea.sun.pitch, 30), 7.5);
      hit(S.world.firstChild, 'sun', 'primitive: sphere; radius: 5.5', vec(photoPoint('sea', ENV.sea.sun.yaw, ENV.sea.sun.pitch, 30)));
      return ask(LINES.S3a, ['sun']);
    }).then(function () {
      hideLine();
      sunRing.parentNode.removeChild(sunRing);

      glow.setAttribute('pulse', 'amount: 0.25; speed: 5');
      fadeAttr(glow, 'soft-picture', 0.95, 1.2);
      return tween(1.4, function (k) { heat.setAttribute('flow-arrows', 'strength', k); });
    }).then(function () {
      return wait(2.2);
    }).then(function () {
      // the water turns into vapour: every drop fades away completely, and a star marker takes its place
      var all = [q].concat(friends);
      all.forEach(function (d, i) {
        var p = d.holder.object3D.position;
        d.star = addStar(S.world.firstChild, 'vapour-' + i, { x: p.x, y: p.y + 1.25 * d.size + 0.2, z: p.z });
      });
      return Promise.all(all.map(function (d) { return dropOpacity(d, 0, 2.6); })
        .concat(all.map(function (d) { return starOpacity(d.star, 1, 2.6); }), [say(LINES.S3b, { seconds: 3.4 })]))
        .then(function () { return all; });
    }).then(function (all) {
      anchorOf.qattoura = function () { var v = new THREE.Vector3(); all[0].star.el.object3D.getWorldPosition(v); v.y += 0.9; return v; };
      return wait(0.4).then(function () { return say(LINES.S3c); }).then(function () { return all; });
    }).then(function (all) {
      // only the stars rise
      tween(1.0, function (k) { heat.setAttribute('flow-arrows', 'strength', 1 - k); });
      tween(1.0, function (k) { up.setAttribute('flow-arrows', 'strength', k); });

      S.riseSnapshot = snapshotDrops();
      var rising = all.map(function (d, i) {
        var p = d.star.el.object3D.position;
        return moveTo(d.star.el, { x: p.x * 0.9, y: p.y + 7.5 + i * 0.4, z: p.z }, 5.2, easeInOut);
      });
      return Promise.all(rising.concat([say(LINES.S3d, { seconds: 4.2 })]));
    }).then(function () {
      S.state = 'S4';
      hideLine();
      tween(1.2, function (k) { up.setAttribute('flow-arrows', 'strength', 1 - k); });
      var b = mk(S.world.firstChild, { position: '0 2.15 -4.3', 'face-camera': '',
        'ar-text': { title: SEA_BOARD.title, value: SEA_BOARD.rows.join('|'), rows: true, width: 3.3, size: 56, accent: '#c9620a', border: '#ff9d3d', opacity: 0 } });

      var skipped = pending(function (res) { S.skipLine = res; });
      return fadeAttr(b, 'ar-text', 1, 0.6).then(function () { return Promise.race([wait(8), skipped]); });
    }).then(function () {
      S.skipLine = null;
      S.done.evaporation = true;
    });
  }

  /* ---------------------------------------------------------------- the sky: condensation */
  var CLOUD_AT = { x: 0, y: 3.35, z: -8.2 }, CLOUD_W = 14;
  function skyScene() {
    var clouds = [], slots = [], group0;
    return goTo('sky', function (group) {
      group0 = group;
      S.cloudStage = 0;
      for (var n = 1; n <= 4; n++) {
        clouds.push(mk(group, { position: CLOUD_AT.x + ' ' + CLOUD_AT.y + ' ' + (CLOUD_AT.z - n * 0.01), 'face-camera': '',
          picture: { src: 'textures/cloud-' + n + '.png', width: CLOUD_W, height: CLOUD_W * 1024 / 1536, opacity: 0, order: 3 + n } }));
      }
      [[-30, 6.4, 2.9], [-10, 6.8, 2.0], [11, 6.5, 2.7], [31, 6.6, 2.1]].forEach(function (s, i) {
        var star = addStar(group, 'star-' + (i + 1), polar(s[0], s[1], s[2]));
        star.pic.setAttribute('soft-picture', 'opacity', 1);
        star.hit = hit(star.el, 'star-' + (i + 1), 'primitive: sphere; radius: 0.8');
        star.ring = mk(star.el, { 'soft-picture': 'kind: ring; size: 1.5; add: true; opacity: 0.9', pulse: 'amount: 0.16; speed: 4' });
        slots.push({ x: (i - 1.5) * 1.3, y: 1.75 + (i % 2) * 0.3, z: -6.4 });
      });
      anchorOf.door = function () { return new THREE.Vector3(0, 3.3, -5).applyMatrix4(S.stage.object3D.matrixWorld); };
      anchorOf.qattoura = function () { return new THREE.Vector3(0, 3.5, -5).applyMatrix4(S.stage.object3D.matrixWorld); };
      anchorOf.cloud = function () { return new THREE.Vector3(0, 0.95, -4.2).applyMatrix4(S.stage.object3D.matrixWorld); };
    }).then(function () {
      S.state = 'K1';
      return say(LINES.K1a);
    }).then(function () {
      return say(LINES.K1b);
    }).then(function () {
      showLine(LINES.K1c[0], LINES.K1c[1]);
    }).then(function coolAll() {
      var left = S.stars.filter(function (s) { return !s.gone; });
      if (!left.length) { return null; }
      return waitTap(left.map(function (s) { return s.id; })).then(function (id) {
        S.state = 'K2';
        var star = S.stars.filter(function (s) { return s.id === id; })[0], i = S.stars.indexOf(star);
        star.gone = true;
        hideLine();

        star.ring.parentNode.removeChild(star.ring); star.hit.parentNode.removeChild(star.hit);
        // the cold: a snow crystal flashes, the star goes out, and a visible drop of liquid water appears
        var p = star.el.object3D.position.clone();
        var flake = mk(group0, { position: vec(p), 'face-camera': '', 'soft-picture': 'kind: flake; size: 0.4; add: true; opacity: 1' });
        tween(0.9, function (k) { flake.setAttribute('soft-picture', { size: 0.4 + 1.5 * k, opacity: 1 - k }); }).then(function () { flake.parentNode.removeChild(flake); }, function () {});
        starOpacity(star, 0, 0.5);
        var count = S.stars.filter(function (s) { return s.gone; }).length;
        var drop = addDrop(group0, 'drop-' + (i + 1), { x: p.x, y: p.y - 0.55, z: p.z },
          { size: count === 1 ? 1.15 : 0.95, tint: ['#ffffff', '#bfe6ff', '#d9d2ff', '#bff5e6'][count - 1], opacity: 0 });
        return modelReady(drop.model)
          .then(function () { return dropOpacity(drop, 1, 0.5); })
          .then(function () {
            if (count === 1) { return say(LINES.K2, { seconds: 3 }); }
            return null;
          })
          .then(function () {
            return moveTo(drop.holder, slots[i], 1.3);        // the drop joins the others ...
          })
          .then(function () {

            S.cloudStage = count;
            var show = clouds[count - 1], old = count > 1 ? clouds[count - 2] : null;
            return fadeAttr(show, 'picture', 1, 1.2).then(function () { if (old) { old.setAttribute('picture', 'opacity', 0); } });
          })
          .then(coolAll);
      });
    }).then(function () {
      S.state = 'K3';
      return wait(0.6);
    }).then(function () {
      return say(LINES.K3a);
    }).then(function () {
      return say(LINES.K3b);
    }).then(function () {

      return say(LINES.K3c);
    }).then(function () {
      S.done.condensation = true;
    });
  }

  /* ---------------------------------------------------------------- the middle door: comparing */
  var CARD_AT = { x: 0, y: 1.34, z: -2.9 };
  function compareScene() {
    var panels = {}, cardEl, group0, qe, qc;
    S.state = 'H3';
    S.rows = { E: [], C: [], S: [] };
    S.remaining = CARD_ORDER.slice();
    function redraw(kind) { panels[kind].setAttribute('ar-text', 'value', S.rows[kind].join('|')); }
    return goTo('hub', function (group) {
      group0 = group;
      buildHub(group, null);
      qe = addDrop(group, 'qattoura-evaporation', polar(33, 3.5, 0), { tint: '#ffd9b8' });
      qc = addDrop(group, 'qattoura-condensation', polar(-33, 3.5, 0), { tint: '#c9e6ff' });
      panels.E = board(group, 'E', polar(22.5, 3.9, 2.6), 2.4);
      panels.C = board(group, 'C', polar(-22.5, 3.9, 2.6), 2.4);
      panels.S = board(group, 'S', { x: 0, y: 0.38, z: -3.3 }, 2.1);
      hit(qe.holder, 'target-E', 'primitive: sphere; radius: 0.7', '0 0.55 0');
      hit(qc.holder, 'target-C', 'primitive: sphere; radius: 0.7', '0 0.55 0');
      hit(panels.E, 'target-E', 'primitive: plane; width: 2.4; height: 1.8');
      hit(panels.C, 'target-C', 'primitive: plane; width: 2.4; height: 1.8');
      hit(panels.S, 'target-S', 'primitive: plane; width: 2.1; height: 1');
      hit(hub.doors.compare.holder, 'target-S', 'primitive: box; width: 2.6; height: 3; depth: 0.6', '0 1.9 0.2');
      anchorOf.qattoura = function () { return new THREE.Vector3(0, CARD_AT.y, CARD_AT.z).applyMatrix4(S.stage.object3D.matrixWorld); };
      cardEl = mk(group, { position: vec(CARD_AT), 'face-camera': '', scale: '0.001 0.001 0.001',
        'ar-text': { title: '', value: '', width: 1.6, size: 80, color: '#3b2600', bg: 'rgba(255,243,191,0.98)', border: '#ffb400' } });
      anchorOf.door = function () { return new THREE.Vector3(0, 2.6, -3.2).applyMatrix4(S.stage.object3D.matrixWorld); };
    }).then(function () {
      return say(LINES.H3a);
    }).then(function () {
      return say(LINES.H3b);
    }).then(function () {
      return say(LINES.H3c);
    }).then(function nextCard() {
      S.state = 'C1';
      if (!S.remaining.length) { return null; }
      var id = S.remaining[0], card = CARDS[id];
      cardEl.setAttribute('ar-text', 'value', card.text);
      cardEl.object3D.position.set(CARD_AT.x, CARD_AT.y, CARD_AT.z);

      return scaleTo(cardEl, 1, 0.35, easeBack).then(function choose() {
        return waitTap(['target-E', 'target-C', 'target-S']).then(function (t) {
          var kind = t.slice(-1);
          if (kind !== card.target) {                      // corrective feedback, then the same card again

            var x0 = cardEl.object3D.position.x;
            tween(0.4, function (k) { cardEl.object3D.position.x = x0 + Math.sin(k * Math.PI * 5) * 0.09 * (1 - k); });
            return say(['door', card.why], { seconds: 4 }).then(choose);
          }

          var to = new THREE.Vector3();
          panels[kind].object3D.getWorldPosition(to);
          S.stage.object3D.worldToLocal(to);
          return Promise.all([moveTo(cardEl, to, 0.55, easeInOut), scaleTo(cardEl, 0.15, 0.55)]).then(function () {
            cardEl.object3D.scale.set(0.001, 0.001, 0.001);
            S.rows[kind].push(card.text);
            S.remaining.shift();
            redraw(kind);
            return wait(0.35);
          }).then(nextCard);
        });
      });
    }).then(function () {
      // the door is satisfied: the lock falls, both leaves swing open, and the three boards line up
      S.state = 'C2';
      S.done.compare = true;
      var entry = hub.doors.compare, lock = entry.model.getObject3D('mesh') && entry.model.getObject3D('mesh').getObjectByName('lock');

      var y0 = lock ? lock.position.y : 0;
      return tween(0.9, function (k) { if (lock) { lock.position.y = y0 - 1.3 * k * k; lock.rotation.z = 1.4 * k; } }, function (k) { return k; })
        .then(function () { if (lock) { lock.visible = false; } return openDoor(entry, 2.0); });
    }).then(function () {

      var d = hub.doors.compare.def;
      mk(hub.doors.compare.holder, { position: (d.open / 2 + 0.75) + ' ' + (DOOR_STEP + d.tall + 0.95) + ' 0.5', 'face-camera': '', 'soft-picture': 'kind: medal; size: 0.62; opacity: 1' });
      // the final board: three columns with their tops in line, read from the right: evaporation, the similarities, condensation
      var top = 3.02, columns = { E: 29, S: 0, C: -29 };
      var head = mk(group0, { position: '0 ' + (top + 0.4) + ' -3.9', 'face-camera': '', 'ar-text': { value: 'في دورة الماء', width: 1.7, size: 96, color: '#ffffff', bg: 'rgba(11,61,107,0.92)', border: '#ffc928', opacity: 0 } });
      fadeAttr(head, 'ar-text', 1, 0.8);
      return Promise.all(Object.keys(columns).map(function (kind) {
        panels[kind].setAttribute('ar-text', 'width', 1.95);
        var tall = panels[kind].components['ar-text'].height;
        return moveTo(panels[kind], polar(columns[kind], 3.9, top - tall / 2), 1.2);
      }));
    }).then(function () {
      return say(LINES.C2);
    }).then(function () {
      var again = mk(group0, { position: vec(CARD_AT), 'face-camera': '', pulse: 'amount: 0.07; speed: 4',
        'ar-text': { value: '🔄 العب مرة أخرى', width: 1.6, size: 92, color: '#ffffff', bg: 'rgba(255,138,31,0.97)', border: '#ffffff' } });
      hit(again, 'replay', 'primitive: plane; width: 1.6; height: 0.45');
      return waitTap(['replay']);
    }).then(function () {
      restart();
      return Promise.reject(STALE);
    });
  }

  /* ---------------------------------------------------------------- the whole story */
  function story() {
    return hubStep('H1', ['H1a', 'H1b', 'H1c'], 'evaporation')
      .then(seaScene)
      .then(function () { return hubStep('H2', ['H2'], 'condensation'); })
      .then(skyScene)
      .then(compareScene);
  }
  /* Anything that is not a restart is a real fault, for example a photograph that did not arrive: say so on screen. */
  function failed(e) {
    if (e === STALE) { return; }
    console.error(e);
    dropEverything();
    $('problem').hidden = false;
  }
  function begin() {
    story().catch(failed);
  }
  function restart() {
    dropEverything();
    S.done = {}; S.remaining = CARD_ORDER.slice(); S.riseSnapshot = null; S.cloudStage = 0; S.rows = null; S.busyHint = false;
    S.state = 'start';
    setTimeout(begin, 0);
  }
  function snapshotDrops() {
    return S.drops.map(function (d) {
      var look = d.model.getAttribute('model-look');
      return { id: d.id, visible: !!(d.holder.parentNode && d.holder.object3D.visible), opacity: look ? look.opacity : 1 };
    });
  }

  /* ---------------------------------------------------------------- start-up */
  AFRAME.registerComponent('story', {
    init: function () {
      var scene = this.el, startBtn = $('startBtn'), msg = $('loadMsg'), loadFailed = false;
      S.scene = scene; S.stage = $('stage'); S.world = $('world'); S.sky = $('sky'); S.speech = $('speech');

      var veil = new THREE.Mesh(new THREE.SphereGeometry(0.4, 16, 12),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.BackSide, transparent: true, opacity: 1, depthTest: false, depthWrite: false, toneMapped: false }));
      veil.renderOrder = 999;
      $('fade').setObject3D('mesh', veil);

      function broken() {
        loadFailed = true;
        clearTimeout(deadline);
        startBtn.disabled = true;
        msg.textContent = 'تعذّر تحميل المغامرة. تأكد من الاتصال بالإنترنت ثم أعد تحميل الصفحة.';
      }
      var deadline = setTimeout(broken, 60000);            // something never answered
      // every picture the story needs must have arrived before the start button works
      var pictures = Promise.all(PICTURES.map(function (src) {
        return new Promise(function (ok, bad) {
          var im = new Image();
          im.onload = function () { ok(); };
          im.onerror = function () { bad(new Error('picture ' + src)); };
          im.src = src;
        });
      }));
      // every model must have been downloaded and decoded: a damaged file fails here, not in the middle of the story
      var models = QParts.loadModels(MODELS.map(function (id) { return { id: id, src: 'models/' + id + '.glb' }; }));
      var sceneReady = new Promise(function (ok) { if (scene.hasLoaded) { ok(); } else { scene.addEventListener('loaded', function () { ok(); }); } });
      Promise.all([pictures, models, sceneReady]).then(function () {
        if (loadFailed) { return; }
        clearTimeout(deadline);
        msg.textContent = '';
        startBtn.disabled = false;
      }, broken);

      startBtn.addEventListener('click', function () {
        if (startBtn.disabled) { return; }
        $('start').style.display = 'none';
        QParts.fontReady.then(begin);
      });

      // a headset has no finger: there the pupil looks at a thing for a moment to choose it
      var gaze = $('gaze');
      scene.addEventListener('enter-vr', function () {
        if (AFRAME.utils.device.checkHeadsetConnected() || AFRAME.utils.device.isMobileVR()) {
          gaze.setAttribute('raycaster', 'enabled', true); gaze.object3D.visible = true;
        }
      });
      scene.addEventListener('exit-vr', function () { gaze.setAttribute('raycaster', 'enabled', false); gaze.object3D.visible = false; });
    },
    tick: function (t, dt) { engineTick(dt); speechTick(); }
  });

  /* small handle for checking the story from the console */
  window.__vr = {
    get state() { return S.state; },
    get cards() { return S.remaining.slice(); },
    get cloudStage() { return S.cloudStage; },
    get riseSnapshot() { return S.riseSnapshot; },
    get expecting() { return S.expect ? S.expect.ids.slice() : []; },
    get rows() { return S.rows ? { E: S.rows.E.slice(), C: S.rows.C.slice(), S: S.rows.S.slice() } : null; },
    get line() { var d = S.speech.getAttribute('ar-text'); return d && d.opacity > 0 ? d.value : ''; },
    stars: function () { return S.stars.map(function (s) { return { id: s.id, visible: s.pic.getAttribute('soft-picture').opacity > 0.05 }; }); },
    skip: skip,
    tap: tap,
    /* start again from one place: 'sea', 'sky' or 'compare' (for checking a single scene) */
    jump: function (to) {
      dropEverything();
      S.done = { evaporation: to !== 'sea', condensation: to === 'compare' };
      S.riseSnapshot = null; S.cloudStage = 0; S.busyHint = false;
      var rest = to === 'sea' ? seaScene().then(function () { return hubStep('H2', ['H2'], 'condensation'); }).then(skyScene).then(compareScene)
        : to === 'sky' ? skyScene().then(compareScene) : compareScene();
      rest.catch(failed);
    },
    drops: snapshotDrops,
    calls: function () { return S.scene.renderer.info.render.calls; }
  };
}());
