/* Skin Prime \u2014 campo de part\u00edculas 3D (WebGL puro, sem bibliotecas).
   As part\u00edculas assumem formas (marca, DNA, camadas da pele, c\u00e9lula) e reagem ao ponteiro e \u00e0 rolagem. */
(function () {
  var cv = document.getElementById('fx');
  if (!cv) return;
  var gl = cv.getContext('webgl', { alpha: true, antialias: false, premultipliedAlpha: false });
  if (!gl) { cv.remove(); return; }
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = Math.min(window.innerWidth, window.innerHeight) < 700;
  var N = small ? 7000 : 15000;
  var R = document.documentElement.getAttribute('data-root') || '';

  function rnd() { return Math.random(); }
  function gauss() { return (rnd() + rnd() + rnd() - 1.5) / 1.5; }

  // ---------- formas
  function helix() {
    var a = new Float32Array(N * 3), tilt = .45, c = Math.cos(tilt), s = Math.sin(tilt);
    for (var i = 0; i < N; i++) {
      var t = rnd() * 2 - 1, th = t * Math.PI * 2.6, r = .42, x, y = t * 1.35, z, k = rnd();
      if (k < .38) { x = r * Math.cos(th); z = r * Math.sin(th); }
      else if (k < .76) { x = r * Math.cos(th + Math.PI); z = r * Math.sin(th + Math.PI); }
      else { // degraus
        var q = Math.round(t * 16) / 16, tq = q * Math.PI * 2.6, u = rnd() * 2 - 1;
        x = r * Math.cos(tq) * u; z = r * Math.sin(tq) * u; y = q * 1.35;
      }
      x += gauss() * .018; y += gauss() * .018; z += gauss() * .018;
      a[i * 3] = x * c - y * s; a[i * 3 + 1] = x * s + y * c; a[i * 3 + 2] = z;
    }
    return a;
  }
  function skin() { // tr\u00eas camadas onduladas: epiderme, derme, hipoderme
    var a = new Float32Array(N * 3), rx = -1.05, c = Math.cos(rx), s = Math.sin(rx);
    for (var i = 0; i < N; i++) {
      var k = rnd(), L = k < .55 ? 0 : k < .85 ? 1 : 2;
      var x = (rnd() * 2 - 1) * 1.5, z = (rnd() * 2 - 1) * 1.05;
      var y = .16 * Math.sin(x * 3.1 + L) * Math.cos(z * 2.7 - L * .7) + .05 * Math.sin(x * 9 + z * 7) - L * .36 + .3;
      if (L === 0 && rnd() < .06) y += rnd() * .25; // "pelos"/poros
      a[i * 3] = x; a[i * 3 + 1] = y * c - z * s; a[i * 3 + 2] = y * s + z * c;
    }
    return a;
  }
  function cell() {
    var a = new Float32Array(N * 3);
    for (var i = 0; i < N; i++) {
      var u = rnd() * 2 - 1, th = rnd() * Math.PI * 2, q = Math.sqrt(1 - u * u), k = rnd();
      var r = k < .62 ? 1.02 + gauss() * .012 : k < .8 ? .36 + gauss() * .03 : Math.cbrt(rnd()) * .95;
      a[i * 3] = r * q * Math.cos(th); a[i * 3 + 1] = r * u; a[i * 3 + 2] = r * q * Math.sin(th);
    }
    return a;
  }
  function ring() { // lente / ret\u00edculo
    var a = new Float32Array(N * 3);
    for (var i = 0; i < N; i++) {
      var th = rnd() * Math.PI * 2, k = rnd(), r = k < .5 ? 1.05 : k < .75 ? .78 : k < .9 ? .3 : rnd() * 1.05;
      r += gauss() * .01;
      a[i * 3] = r * Math.cos(th); a[i * 3 + 1] = r * Math.sin(th); a[i * 3 + 2] = gauss() * .04;
    }
    return a;
  }
  function fromCanvas(draw, w, h, width3d) {
    var c = document.createElement('canvas'); c.width = w; c.height = h;
    var x = c.getContext('2d', { willReadFrequently: true }); draw(x, w, h);
    var d = x.getImageData(0, 0, w, h).data, pts = [];
    for (var j = 0; j < h; j += 2) for (var i = 0; i < w; i += 2) if (d[(j * w + i) * 4 + 3] > 120) pts.push(i, j);
    if (pts.length < 200) return null;
    var a = new Float32Array(N * 3), n = pts.length / 2, sc = width3d / w;
    for (var k = 0; k < N; k++) {
      var p = (Math.random() * n | 0) * 2;
      a[k * 3] = (pts[p] - w / 2 + Math.random() * 2) * sc; a[k * 3 + 1] = -(pts[p + 1] - h / 2 + Math.random() * 2) * sc; a[k * 3 + 2] = gauss() * .03;
    }
    return a;
  }
  function wordmark() {
    return fromCanvas(function (x, w, h) {
      x.fillStyle = '#fff'; x.textAlign = 'center'; x.textBaseline = 'alphabetic';
      x.font = '400 250px "Bodoni Moda",Didot,"Times New Roman",serif'; x.strokeStyle = '#fff'; x.lineWidth = 7; x.lineJoin = 'round'; x.fillText('SKIN', w / 2, 250); x.strokeText('SKIN', w / 2, 250); x.lineWidth = 3;
      x.font = '400 62px "Bodoni Moda",Didot,"Times New Roman",serif';
      var t = 'PRIME', sp = 34, tw = 0, i; for (i = 0; i < t.length; i++) tw += x.measureText(t[i]).width + sp;
      var px = w / 2 + 300 - tw; x.textAlign = 'left'; for (i = 0; i < t.length; i++) { x.fillText(t[i], px, 340); x.strokeText(t[i], px, 340); px += x.measureText(t[i]).width + sp; }
    }, 1100, 380, 3.1);
  }

  var shapes = { helix: helix(), skin: skin(), cell: cell(), ring: ring() };
  shapes.logo = shapes.ring;
  var spin = { logo: 0, helix: 1, skin: .25, cell: 1, ring: 0 };

  // ---------- GL
  var VS = 'attribute vec3 aA;attribute vec3 aB;attribute float aS;uniform float uMix,uT,uAsp,uDpr,uSpinA,uSpinB,uScale,uFade;uniform vec2 uMouse,uOff,uTilt;varying float vA;varying float vS;' +
    'vec3 ry(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x*c+p.z*s,p.y,-p.x*s+p.z*c);}' +
    'vec3 rx(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x,p.y*c-p.z*s,p.y*s+p.z*c);}' +
    'void main(){float d=aS*.45;float m=clamp((uMix-d)/(1.-.45),0.,1.);m=m*m*(3.-2.*m);' +
    'vec3 a=ry(aA,uT*.16*uSpinA),b=ry(aB,uT*.16*uSpinB);vec3 p=mix(a,b,m);' +
    'float burst=sin(m*3.14159);p+=burst*.55*vec3(sin(aS*91.),cos(aS*57.),sin(aS*33.));' +
    'p+=.012*vec3(sin(uT*1.3+aS*40.),cos(uT*1.1+aS*70.),sin(uT*.9+aS*20.));' +
    'p=rx(ry(p,uTilt.x),uTilt.y);p*=uScale;float z=3.2-p.z;vec2 q=p.xy/z*2.1;q.x/=uAsp;q+=uOff;' +
    'vec2 dm=q-uMouse;dm.x*=uAsp;float dl=length(dm);float push=exp(-dl*dl*26.)*.085;q+=normalize(dm+1e-5)*push*vec2(1./uAsp,1.);' +
    'gl_Position=vec4(q,0.,1.);gl_PointSize=(1.7+fract(aS*7.)*2.6)*uDpr*(3.2/z)*(1.+push*7.);' +
    'vA=(.55+.45*fract(aS*13.))*uFade*clamp(1.9-z*.3,.35,1.)*(1.+push*6.);vS=aS;}';
  var FS = 'precision mediump float;varying float vA;varying float vS;void main(){vec2 c=gl_PointCoord-.5;float d=length(c);if(d>.5)discard;' +
    'float a=smoothstep(.5,.05,d);vec3 aq=vec3(.44,.89,.94),ro=vec3(.94,.66,.58),wh=vec3(.93,.97,.98);' +
    'vec3 col=fract(vS*3.7)<.14?ro:(fract(vS*5.3)<.3?wh:aq);gl_FragColor=vec4(col,a*vA);}';
  function sh(t, s) { var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; }
  var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { cv.remove(); return; }
  gl.useProgram(pr);
  var U = {}; ['uMix', 'uT', 'uAsp', 'uDpr', 'uSpinA', 'uSpinB', 'uScale', 'uFade', 'uMouse', 'uOff', 'uTilt'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
  var seeds = new Float32Array(N); for (var i = 0; i < N; i++) seeds[i] = Math.random();
  var bS = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bS); gl.bufferData(gl.ARRAY_BUFFER, seeds, gl.STATIC_DRAW);
  var lS = gl.getAttribLocation(pr, 'aS'); gl.enableVertexAttribArray(lS); gl.vertexAttribPointer(lS, 1, gl.FLOAT, false, 0, 0);
  var bufs = {};
  function buf(name) {
    if (!bufs[name]) { bufs[name] = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bufs[name]); gl.bufferData(gl.ARRAY_BUFFER, shapes[name], gl.STATIC_DRAW); }
    return bufs[name];
  }
  var lA = gl.getAttribLocation(pr, 'aA'), lB = gl.getAttribLocation(pr, 'aB');
  gl.enableVertexAttribArray(lA); gl.enableVertexAttribArray(lB);
  function bind(loc, name) { gl.bindBuffer(gl.ARRAY_BUFFER, buf(name)); gl.vertexAttribPointer(loc, 3, gl.FLOAT, false, 0, 0); }
  gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE); gl.clearColor(0, 0, 0, 0);

  var from = 'cell', to = cv.getAttribute('data-shape') || 'logo', mix = 0, mixT = 1;
  if (!shapes[to]) to = 'helix';
  bind(lA, from); bind(lB, to);
  var st = { ox: 0, oy: 0, sc: 1, fade: 1 }, tg = { ox: 0, oy: 0, sc: 1, fade: 1 };
  var mouse = { x: 9, y: 9, tx: 9, ty: 9 }, tilt = { x: 0, y: 0, tx: 0, ty: 0 };
  var W = 0, H = 0, dpr = 1;

  function go(name) {
    if (!shapes[name] || name === to) return;
    if (mix < .98) { from = to; } else from = to;
    to = name; mix = 0; bind(lA, from); bind(lB, to);
    window.dispatchEvent(new CustomEvent('fx:shape', { detail: name }));
  }
  function place(o) { // o: {x,y,scale,fade}
    tg.ox = o.x || 0; tg.oy = o.y || 0; tg.sc = o.scale || 1; tg.fade = o.fade == null ? 1 : o.fade;
  }
  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 2); W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr; gl.viewport(0, 0, cv.width, cv.height);
  }
  size(); window.addEventListener('resize', size);
  window.addEventListener('pointermove', function (e) {
    mouse.tx = e.clientX / W * 2 - 1; mouse.ty = -(e.clientY / H * 2 - 1);
    tilt.tx = (e.clientX / W - .5) * .5; tilt.ty = (e.clientY / H - .5) * .3;
  }, { passive: true });
  window.addEventListener('pointerleave', function () { mouse.tx = 9; mouse.ty = 9; });

  var t0 = performance.now(), vis = true, last = 0;
  document.addEventListener('visibilitychange', function () { vis = !document.hidden; if (vis) requestAnimationFrame(frame); });
  function frame(now) {
    if (!vis) return;
    var dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    mix += (mixT - mix) * Math.min(1, dt * 1.5); if (mixT - mix < .002) mix = 1;
    ['ox', 'oy', 'sc', 'fade'].forEach(function (k) { st[k] += (tg[k] - st[k]) * Math.min(1, dt * 3); });
    mouse.x += (mouse.tx - mouse.x) * .2; mouse.y += (mouse.ty - mouse.y) * .2;
    tilt.x += (tilt.tx - tilt.x) * .05; tilt.y += (tilt.ty - tilt.y) * .05;
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(U.uMix, mix); gl.uniform1f(U.uT, (now - t0) / 1000); gl.uniform1f(U.uAsp, W / H); gl.uniform1f(U.uDpr, dpr);
    gl.uniform1f(U.uSpinA, spin[from] || 0); gl.uniform1f(U.uSpinB, spin[to] || 0);
    gl.uniform1f(U.uScale, st.sc * (W < 760 ? .62 : 1)); gl.uniform1f(U.uFade, st.fade);
    gl.uniform2f(U.uMouse, mouse.x, mouse.y); gl.uniform2f(U.uOff, st.ox, st.oy); gl.uniform2f(U.uTilt, tilt.x, tilt.y);
    gl.drawArrays(gl.POINTS, 0, N);
    if (!still) requestAnimationFrame(frame);
  }
  if (still) { mix = 1; st = tg; }
  requestAnimationFrame(frame);

  // a marca \u00e9 amostrada depois que a fonte carrega
  function logoReady() {
    var a = null; try { a = wordmark(); } catch (e) { }
    if (a) {
      shapes.logo = a; if (bufs.logo) { gl.deleteBuffer(bufs.logo); delete bufs.logo; }
      if (to === 'logo') { bind(lB, 'logo'); } if (from === 'logo') bind(lA, 'logo');
    }
  }
  if (document.fonts && document.fonts.load) document.fonts.load('400 250px "Bodoni Moda"').then(logoReady, logoReady); else logoReady();

  window.SPFX = { go: go, place: place, count: N, names: Object.keys(shapes) };
  window.dispatchEvent(new Event('fx:ready'));
})();
