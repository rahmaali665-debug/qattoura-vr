/* Building blocks of the VR story "مغامرة قطّورة والأبواب الثلاثة": A-Frame components and small helpers.
   Loaded after aframe.min.js and before story.js. */
(function () {
  'use strict';

  var FONT = '"Baloo Bhaijaan 2", Tahoma, "Segoe UI", Arial, sans-serif';

  /* The web font must be ready before any text is drawn on a canvas; after 3 seconds the fallback font is used. */
  var fontReady = new Promise(function (done) {
    var timer = setTimeout(done, 3000);
    function ok() { clearTimeout(timer); done(); }
    if (document.fonts && document.fonts.load) {
      Promise.all([document.fonts.load('700 48px "Baloo Bhaijaan 2"', 'قطّورة'),
                   document.fonts.load('800 48px "Baloo Bhaijaan 2"', 'قطّورة')]).then(ok, ok);
    } else { ok(); }
  });

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r); ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.closePath();
  }

  function canvasTexture(canvas) {
    var tex = new THREE.CanvasTexture(canvas);
    tex.anisotropy = 8;
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }

  /* ---------- Arabic text on a canvas texture (A-Frame's own text cannot shape Arabic) ----------
     value: lines separated by |   title: a heading line in the accent colour
     rows: when set, the value lines are drawn as separate rows with a thin rule between them (boards). */
  AFRAME.registerComponent('ar-text', {
    schema: {
      value: { type: 'string', default: '' },
      title: { type: 'string', default: '' },
      width: { type: 'number', default: 2.4 },
      size: { type: 'number', default: 60 },
      color: { type: 'string', default: '#0b3d6b' },
      accent: { type: 'string', default: '#c9620a' },
      bg: { type: 'string', default: 'rgba(255,255,255,0.96)' },
      border: { type: 'string', default: '' },
      rows: { type: 'boolean', default: false },
      minLines: { type: 'int', default: 0 },
      opacity: { type: 'number', default: 1 }
    },
    init: function () {
      var self = this;
      this.drawn = false;
      fontReady.then(function () { self.fontOk = true; if (self.el.parentNode) { self.draw(); } });
    },
    update: function (old) {
      var d = this.data, onlyOpacity = this.drawn && old && Object.keys(d).every(function (k) { return k === 'opacity' || d[k] === old[k]; });
      if (onlyOpacity) { this.applyOpacity(); return; }
      this.draw();
    },
    applyOpacity: function () {
      var mesh = this.el.getObject3D('mesh');
      if (mesh) { mesh.material.opacity = this.data.opacity; mesh.visible = this.data.opacity > 0.003; }
    },
    draw: function () {
      var d = this.data, W = 1024, pad = 54;
      var c = document.createElement('canvas'), ctx = c.getContext('2d');
      var lineH = Math.round(d.size * 1.5), titleSize = Math.round(d.size * 1.08), titleH = Math.round(titleSize * 1.75);
      var bodyFont = '700 ' + d.size + 'px ' + FONT;
      ctx.font = bodyFont;
      var lines = [], breaks = [];
      (d.value ? d.value.split('|') : []).forEach(function (para) {
        var cur = '';
        para.trim().split(/\s+/).forEach(function (w) {
          var t = cur ? cur + ' ' + w : w;
          if (ctx.measureText(t).width > W - pad * 2 && cur) { lines.push(cur); cur = w; } else { cur = t; }
        });
        lines.push(cur);
        breaks.push(lines.length);                       // a row ends after this many lines
      });
      var count = Math.max(lines.length, d.minLines);
      var H = pad * 2 + count * lineH + (d.title ? titleH : 0) + (d.rows ? Math.max(0, breaks.length - 1) * 14 : 0);
      c.width = W; c.height = H;
      roundRect(ctx, 6, 6, W - 12, H - 12, 46);
      ctx.fillStyle = d.bg; ctx.fill();
      if (d.border) { ctx.lineWidth = 12; ctx.strokeStyle = d.border; ctx.stroke(); }
      ctx.direction = 'rtl'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      var y = pad;
      if (d.title) {
        ctx.font = '800 ' + titleSize + 'px ' + FONT; ctx.fillStyle = d.accent;
        ctx.fillText(d.title, W / 2, y + titleH / 2 - 10); y += titleH;
      }
      ctx.font = bodyFont; ctx.fillStyle = d.color;
      lines.forEach(function (l, i) {
        ctx.fillText(l, W / 2, y + lineH / 2); y += lineH;
        if (d.rows && breaks.indexOf(i + 1) !== -1 && i + 1 < lines.length) {
          ctx.save(); ctx.strokeStyle = 'rgba(11,61,107,0.22)'; ctx.lineWidth = 4; ctx.setLineDash([14, 12]);
          ctx.beginPath(); ctx.moveTo(pad, y + 7); ctx.lineTo(W - pad, y + 7); ctx.stroke(); ctx.restore();
          y += 14;
        }
      });
      var old = this.el.getObject3D('mesh');
      if (old) { old.geometry.dispose(); old.material.map.dispose(); old.material.dispose(); }
      var mat = new THREE.MeshBasicMaterial({ map: canvasTexture(c), transparent: true, side: THREE.DoubleSide, toneMapped: false, depthWrite: false });
      var mesh = new THREE.Mesh(new THREE.PlaneGeometry(d.width, d.width * H / W), mat);
      mesh.renderOrder = 20;
      this.el.setObject3D('mesh', mesh);
      this.height = d.width * H / W;
      this.drawn = true;
      this.applyOpacity();
    },
    remove: function () {
      var old = this.el.getObject3D('mesh');
      if (old) { old.geometry.dispose(); old.material.map.dispose(); old.material.dispose(); this.el.removeObject3D('mesh'); }
    }
  });

  /* ---------- Always turn towards the camera. upright: turn about the vertical axis only (characters). ---------- */
  AFRAME.registerComponent('face-camera', {
    schema: { upright: { type: 'boolean', default: false } },
    init: function () { this.cam = new THREE.Vector3(); },
    tick: function () {
      var camera = this.el.sceneEl.camera;
      if (!camera) { return; }
      var o = this.el.object3D;
      camera.getWorldPosition(this.cam);
      if (this.data.upright) {
        if (o.parent) { o.parent.worldToLocal(this.cam); }  // the stage may be turned: work in the parent's own space
        o.rotation.set(0, Math.atan2(this.cam.x - o.position.x, this.cam.z - o.position.z), 0);
      } else {
        o.lookAt(this.cam);
      }
    }
  });

  /* ---------- Models: every GLB is downloaded and decoded once, before the start button works ----------
     The decoded originals stay in memory for the whole visit and are never put in the scene. Each entity shows a copy
     that shares the original's geometry and textures, so building a place again costs no new graphics memory.
     The only things an entity owns are the materials that model-look clones for it, and model-look disposes those. */
  var originals = {};
  function loadModels(list) {
    var loader = new THREE.GLTFLoader();
    return Promise.all(list.map(function (m) {
      return new Promise(function (ok, bad) {
        loader.load(m.src, function (gltf) { originals[m.id] = gltf; ok(); }, undefined,
          function () { bad(new Error('model ' + m.src)); });
      });
    }));
  }
  AFRAME.registerComponent('q-model', {
    schema: { type: 'string' },
    update: function () {
      var original = originals[this.data];
      if (this.el.getObject3D('mesh')) { this.el.removeObject3D('mesh'); }
      if (!original) { this.el.emit('model-error', { id: this.data }); return; }
      var copy = original.scene.clone(true);
      copy.animations = original.animations;               // animation-mixer reads the clips from here
      this.el.setObject3D('mesh', copy);
      this.el.emit('model-loaded', { format: 'gltf', model: copy });
    },
    remove: function () { if (this.el.getObject3D('mesh')) { this.el.removeObject3D('mesh'); } }
  });

  /* ---------- Look of a GLB model: opacity, a colour tint and a glow. Materials are cloned once per entity. ---------- */
  AFRAME.registerComponent('model-look', {
    schema: {
      opacity: { type: 'number', default: 1 },
      tint: { type: 'color', default: '#ffffff' },
      glow: { type: 'color', default: '#000000' },
      env: { type: 'number', default: 1 }
    },
    init: function () {
      this.apply = this.apply.bind(this);
      this.root = null;                                   // the model whose materials were cloned
      this.owned = [];                                    // the clones: this component made them, so it disposes them
      this.el.addEventListener('model-loaded', this.apply);
    },
    update: function () { this.apply(); },
    release: function () {
      this.owned.forEach(function (m) { m.dispose(); });
      this.owned = [];
    },
    apply: function () {
      var root = this.el.getObject3D('mesh'), d = this.data, owned = this.owned;
      if (!root) { return; }
      var first = this.root !== root;
      if (first) { this.release(); owned = this.owned; this.root = root; }
      root.traverse(function (n) {
        if (!n.isMesh || !n.material) { return; }
        if (first) { n.material = n.material.clone(); owned.push(n.material); }
        var m = n.material, solid = d.opacity >= 0.999;
        m.color.set(d.tint);
        if (m.emissive) { m.emissive.set(d.glow); }
        if (m.envMapIntensity !== undefined) { m.envMapIntensity = d.env; }
        if (m.transparent === solid) { m.transparent = !solid; m.needsUpdate = true; }
        m.depthWrite = solid;
        m.opacity = d.opacity;
      });
    },
    remove: function () {
      this.el.removeEventListener('model-loaded', this.apply);
      this.release();                                     // shared geometry and textures stay with the original
      this.root = null;
    }
  });

  /* ---------- The photograph all around: an inward-facing sphere whose picture also lights the 3D objects ---------- */
  AFRAME.registerComponent('photo-sky', {
    init: function () {
      var geo = new THREE.SphereGeometry(300, 64, 32);
      geo.scale(-1, 1, 1);                                // seen from inside, not mirrored
      this.mat = new THREE.MeshBasicMaterial({ color: 0x9cc9f0, toneMapped: false, depthWrite: false, fog: false });
      this.mesh = new THREE.Mesh(geo, this.mat);
      this.mesh.renderOrder = -10;
      this.mesh.frustumCulled = false;
      this.el.setObject3D('mesh', this.mesh);
      this.loader = new THREE.TextureLoader();
      this.envTarget = null;
    },
    /* file: equirectangular JPEG. yaw: the direction of the picture (degrees, 0 = picture centre, positive to the right)
       that is put straight ahead. Returns a promise that resolves when the new picture is on screen. */
    show: function (file, yaw) {
      var self = this, scene = this.el.sceneEl;
      return new Promise(function (ok, fail) {
        self.loader.load(file, function (tex) {
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = 4;
          var old = self.mat.map;
          self.mat.map = tex; self.mat.color.set(0xffffff); self.mat.needsUpdate = true;
          self.mesh.rotation.y = -Math.PI / 2 + THREE.MathUtils.degToRad(yaw);
          if (old) { old.dispose(); }                     // only the current photograph stays on the graphics card
          self.light(scene);
          ok();
        }, undefined, function () { fail(new Error('photo ' + file)); });
      });
    },
    /* Image-based lighting: the same photograph, turned the same way, becomes the environment of the scene. */
    light: function (scene) {
      var renderer = scene.renderer;
      if (!renderer) { return; }
      var pmrem = new THREE.PMREMGenerator(renderer);
      var stage = new THREE.Scene();
      var copy = new THREE.Mesh(this.mesh.geometry, this.mat);
      this.mesh.updateWorldMatrix(true, false);
      this.mesh.getWorldQuaternion(copy.quaternion);     // the stage may be turned towards the pupil
      stage.add(copy);
      var target = pmrem.fromScene(stage, 0.02, 1, 600);
      scene.object3D.environment = target.texture;
      if (this.envTarget) { this.envTarget.dispose(); }
      this.envTarget = target;
      pmrem.dispose();
    },
    remove: function () {
      if (this.mat.map) { this.mat.map.dispose(); }
      if (this.envTarget) { this.envTarget.dispose(); }
      this.mesh.geometry.dispose(); this.mat.dispose();
    }
  });

  /* ---------- Soft pictures drawn once on a canvas: glow, star, ring, sparkle, shadow, gold light ---------- */
  var drawings = {
    glow: function (ctx, s) {
      var g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.18, 'rgba(255,250,225,0.85)');
      g.addColorStop(0.45, 'rgba(255,225,150,0.28)'); g.addColorStop(1, 'rgba(255,200,100,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
    },
    star: function (ctx, s) {                             // the marker that stands for invisible water vapour
      var c = s / 2, g = ctx.createRadialGradient(c, c, 0, c, c, c);
      g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.2, 'rgba(210,240,255,0.7)'); g.addColorStop(0.6, 'rgba(150,215,255,0.16)'); g.addColorStop(1, 'rgba(150,215,255,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
      ctx.translate(c, c); ctx.fillStyle = 'rgba(255,255,255,0.98)';
      for (var k = 0; k < 4; k++) {
        ctx.rotate(Math.PI / 2);
        ctx.beginPath(); ctx.moveTo(0, -c * 0.94); ctx.quadraticCurveTo(c * 0.07, -c * 0.07, c * 0.14, 0); ctx.lineTo(-c * 0.14, 0);
        ctx.quadraticCurveTo(-c * 0.07, -c * 0.07, 0, -c * 0.94); ctx.fill();
      }
    },
    ring: function (ctx, s) {
      ctx.strokeStyle = 'rgba(255,255,255,0.98)'; ctx.lineWidth = s * 0.05;
      ctx.beginPath(); ctx.arc(s / 2, s / 2, s * 0.43, 0, Math.PI * 2); ctx.stroke();
      ctx.strokeStyle = 'rgba(255,236,150,0.6)'; ctx.lineWidth = s * 0.02;
      ctx.beginPath(); ctx.arc(s / 2, s / 2, s * 0.36, 0, Math.PI * 2); ctx.stroke();
    },
    flake: function (ctx, s) {                            // a snow crystal: the cold that turns vapour into drops
      ctx.translate(s / 2, s / 2); ctx.strokeStyle = 'rgba(255,255,255,0.98)'; ctx.lineWidth = s * 0.045; ctx.lineCap = 'round';
      for (var k = 0; k < 6; k++) {
        ctx.rotate(Math.PI / 3);
        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -s * 0.42);
        ctx.moveTo(0, -s * 0.25); ctx.lineTo(s * 0.1, -s * 0.34); ctx.moveTo(0, -s * 0.25); ctx.lineTo(-s * 0.1, -s * 0.34); ctx.stroke();
      }
    },
    shadow: function (ctx, s) {
      var g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      g.addColorStop(0, 'rgba(0,0,0,0.62)'); g.addColorStop(0.55, 'rgba(0,0,0,0.3)'); g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
    },
    gold: function (ctx, s) {
      var g = ctx.createRadialGradient(s / 2, s * 0.55, 0, s / 2, s * 0.55, s * 0.7);
      g.addColorStop(0, '#fffbe0'); g.addColorStop(0.45, '#ffe07a'); g.addColorStop(1, '#f2a100');
      ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
    },
    pointer: function (ctx, s) {                          // "turn this way": two chevrons pointing right
      ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      [[0.22, 'rgba(11,61,107,0.9)', 0.2], [0.22, '#ffffff', 0.11]].forEach(function (pass) {
        ctx.strokeStyle = pass[1]; ctx.lineWidth = s * pass[2];
        [0.3, 0.56].forEach(function (x) {
          ctx.beginPath(); ctx.moveTo(s * x, s * 0.24); ctx.lineTo(s * (x + pass[0]), s * 0.5); ctx.lineTo(s * x, s * 0.76); ctx.stroke();
        });
      });
    },
    medal: function (ctx, s) {                            // the gold star on a finished door
      ctx.translate(s / 2, s / 2);
      ctx.beginPath();
      for (var i = 0; i < 10; i++) {
        var r = i % 2 ? s * 0.2 : s * 0.46, a = -Math.PI / 2 + i * Math.PI / 5;
        ctx[i ? 'lineTo' : 'moveTo'](Math.cos(a) * r, Math.sin(a) * r);
      }
      ctx.closePath();
      var g = ctx.createLinearGradient(0, -s / 2, 0, s / 2);
      g.addColorStop(0, '#fff6b0'); g.addColorStop(0.55, '#ffc928'); g.addColorStop(1, '#ff9d1f');
      ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = s * 0.03; ctx.strokeStyle = '#ffffff'; ctx.stroke();
    }
  };
  var drawingCache = {};
  function drawingTexture(kind) {
    if (!drawingCache[kind]) {
      var c = document.createElement('canvas');
      c.width = c.height = 256;
      drawings[kind](c.getContext('2d'), 256);
      drawingCache[kind] = canvasTexture(c);
    }
    return drawingCache[kind];
  }

  /* A flat picture from the list above. It is a plane, not a THREE.Sprite, so the gaze ray of a headset never has to
     test a sprite. Use it together with face-camera when it must look at the viewer. */
  AFRAME.registerComponent('soft-picture', {
    schema: {
      kind: { type: 'string', default: 'glow' },
      size: { type: 'number', default: 1 },
      color: { type: 'color', default: '#ffffff' },
      opacity: { type: 'number', default: 1 },
      add: { type: 'boolean', default: false },           // additive light (glow) or normal paint (shadow, medal)
      flat: { type: 'boolean', default: false }           // lie on the ground
    },
    init: function () {
      var d = this.data;
      this.mat = new THREE.MeshBasicMaterial({ map: drawingTexture(d.kind), transparent: true, depthWrite: false, toneMapped: false,
        blending: d.add ? THREE.AdditiveBlending : THREE.NormalBlending, side: THREE.DoubleSide });
      var mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.mat);
      if (d.flat) { mesh.rotation.x = -Math.PI / 2; }
      mesh.renderOrder = d.add ? 12 : 2;
      this.el.setObject3D('mesh', mesh);
    },
    update: function () {
      var d = this.data, mesh = this.el.getObject3D('mesh');
      this.mat.color.set(d.color);
      this.mat.opacity = d.opacity;
      mesh.scale.set(d.size, d.size, d.size);
      mesh.visible = d.opacity > 0.003;
    },
    remove: function () {
      var mesh = this.el.getObject3D('mesh');
      if (mesh) { mesh.geometry.dispose(); }
      this.mat.dispose();
      this.el.removeObject3D('mesh');
    }
  });

  /* ---------- A picture file on a plane (the cloud stages, the view through an open door) ---------- */
  AFRAME.registerComponent('picture', {
    schema: {
      src: { type: 'string' },
      width: { type: 'number', default: 1 },
      height: { type: 'number', default: 1 },
      opacity: { type: 'number', default: 1 },
      order: { type: 'int', default: 5 }
    },
    init: function () {
      var d = this.data, self = this;
      this.mat = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, toneMapped: false, opacity: 0 });
      var mesh = new THREE.Mesh(new THREE.PlaneGeometry(d.width, d.height), this.mat);
      mesh.renderOrder = d.order;
      this.el.setObject3D('mesh', mesh);
      this.gone = false;
      new THREE.TextureLoader().load(d.src, function (tex) {
        if (self.gone) { tex.dispose(); return; }        // the entity was removed while the picture was on its way
        tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
        self.mat.map = tex; self.mat.needsUpdate = true; self.update();
      });
    },
    update: function () {
      var mesh = this.el.getObject3D('mesh');
      this.mat.opacity = this.mat.map ? this.data.opacity : 0;
      if (mesh) { mesh.visible = this.mat.opacity > 0.003; }
    },
    remove: function () {
      var mesh = this.el.getObject3D('mesh');
      this.gone = true;
      if (mesh) { mesh.geometry.dispose(); }
      if (this.mat.map) { this.mat.map.dispose(); }
      this.mat.dispose();
      this.el.removeObject3D('mesh');
    }
  });

  /* ---------- Breathing: a gentle change of size that says "tap me" ---------- */
  AFRAME.registerComponent('pulse', {
    schema: { amount: { type: 'number', default: 0.14 }, speed: { type: 'number', default: 3.2 }, base: { type: 'number', default: 1 } },
    tick: function (t) {
      var s = this.data.base * (1 + this.data.amount * (0.5 + 0.5 * Math.sin(t / 1000 * this.data.speed)));
      this.el.object3D.scale.set(s, s, s);
    }
  });

  /* ---------- Bobbing up and down (drops on the water, stars in the air) ---------- */
  AFRAME.registerComponent('bob', {
    schema: { height: { type: 'number', default: 0.08 }, speed: { type: 'number', default: 1.6 }, phase: { type: 'number', default: 0 } },
    init: function () { this.child = this.el.object3D; this.off = 0; },
    tick: function (t) {
      var next = this.data.height * Math.sin(t / 1000 * this.data.speed + this.data.phase);
      this.child.position.y += next - this.off;            // added on top of whatever else moves the entity
      this.off = next;
    }
  });

  /* ---------- Arrows that flow from one point to another (heat from the sun, vapour going up) ----------
     Each copy of the arrow model travels along the path, appears at the start and fades at the end. */
  AFRAME.registerComponent('flow-arrows', {
    schema: {
      model: { type: 'string' },
      from: { type: 'vec3' },
      to: { type: 'vec3' },
      count: { type: 'int', default: 4 },
      length: { type: 'number', default: 1.4 },
      thick: { type: 'number', default: 1.4 },
      speed: { type: 'number', default: 0.22 },            // path lengths per second
      spread: { type: 'number', default: 0.5 },
      glow: { type: 'color', default: '#000000' },
      strength: { type: 'number', default: 0 }             // 0 hides the arrows, 1 shows them fully
    },
    init: function () {
      var d = this.data, up = new THREE.Vector3(0, 1, 0);
      this.arrows = [];
      this.a = new THREE.Vector3(d.from.x, d.from.y, d.from.z);
      this.b = new THREE.Vector3(d.to.x, d.to.y, d.to.z);
      var dirn = this.b.clone().sub(this.a).normalize();
      var q = new THREE.Quaternion().setFromUnitVectors(up, dirn);
      var side = new THREE.Vector3().crossVectors(dirn, up);
      if (side.lengthSq() < 1e-4) { side.set(1, 0, 0); }
      side.normalize();
      var side2 = new THREE.Vector3().crossVectors(dirn, side).normalize();
      for (var i = 0; i < d.count; i++) {
        var el = document.createElement('a-entity');
        el.setAttribute('q-model', d.model);
        el.setAttribute('model-look', { opacity: 0, glow: d.glow });
        el.object3D.quaternion.copy(q);
        el.object3D.scale.set(d.thick, d.length, d.thick);
        el.object3D.visible = false;
        this.el.appendChild(el);
        var ang = (i / d.count) * Math.PI * 2;
        this.arrows.push({ el: el, phase: i / d.count, shown: -1,
          off: side.clone().multiplyScalar(Math.cos(ang) * d.spread).add(side2.clone().multiplyScalar(Math.sin(ang) * d.spread)) });
      }
      this.t = 0;
    },
    tick: function (time, dt) {
      var d = this.data;
      if (d.strength <= 0.003) {
        this.arrows.forEach(function (ar) { if (ar.shown !== 0) { ar.el.object3D.visible = false; ar.shown = 0; } });
        return;
      }
      this.t += Math.min(dt, 100) / 1000 * d.speed;
      for (var i = 0; i < this.arrows.length; i++) {
        var ar = this.arrows[i], p = (this.t + ar.phase) % 1;
        var fade = Math.min(1, p / 0.18, (1 - p) / 0.22) * d.strength;
        ar.el.object3D.position.lerpVectors(this.a, this.b, p).add(ar.off);
        ar.el.object3D.visible = true;
        var o = Math.round(fade * 40) / 40;
        if (o !== ar.shown) { ar.el.setAttribute('model-look', 'opacity', o); ar.shown = o; }
      }
    }
  });

  window.QParts = { fontReady: fontReady, drawingTexture: drawingTexture, loadModels: loadModels };
}());
