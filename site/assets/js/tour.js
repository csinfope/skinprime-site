/* Skin Prime - tour 3D simulado dos ambientes (WebGL puro).
   Cada foto e projetada num "comodo" 3D (parede do fundo, laterais, piso e teto) calculado a partir do
   ponto de fuga da imagem. A camera se desloca dentro desse comodo: olhar em volta e entrar na sala. */
(function () {
  var d = document, W = window;
  var links = [].slice.call(d.querySelectorAll('a[data-tour]'));
  if (!links.length) return;
  var still = W.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // por ambiente: ponto de fuga [u,v] e retangulo da parede do fundo [esq, topo, dir, base] (0..1 na foto)
  var ROOMS = {
    'vista': { vp: [.35, .42], w: [.05, .05, .72, .68] },
    'lounge': { vp: [.5, .42], w: [.15, .05, .9, .6] },
    'recepcao': { vp: [.6, .45], w: [.3, .15, .85, .68] },
    'espera': { vp: [.42, .42], w: [.2, .2, .68, .62] },
    'cafe': { vp: [.6, .45], w: [.36, .08, .92, .72] },
    'consultorio': { vp: [.4, .42], w: [.08, .05, .7, .62] },
    'sala-laser': { vp: [.5, .42], w: [.12, .05, .9, .62] },
    'sala-procedimentos': { vp: [.5, .4], w: [.05, .1, .95, .6] },
    'capilar': { vp: [.5, .4], w: [.12, .05, .9, .55] },
    'detalhe': { vp: [.6, .4], w: [.3, .05, .95, .6] }
  };
  var DEF = { vp: [.5, .45], w: [.2, .15, .8, .65] };
  var F = 1.5, KMAX = 4.5, EXT = .3, NX = 96, NY = 72;

  // lista unica de ambientes (a mesma foto pode aparecer em mais de um link)
  var rooms = [], seen = {};
  links.forEach(function (a) {
    var k = a.getAttribute('data-tour');
    if (!seen[k]) { seen[k] = 1; rooms.push({ k: k, src: a.getAttribute('href'), name: a.getAttribute('data-alt') || k }); }
  });

  var ov = d.createElement('div'); ov.className = 't3'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'Tour 3D simulado');
  ov.innerHTML = '<canvas></canvas><img class="t3__flat" alt="">' +
    '<div class="t3__top"><p class="label"><b>Tour 3D simulado</b><span class="t3__name"></span></p><button type="button" class="t3__x" aria-label="Fechar">Fechar \u2715</button></div>' +
    '<p class="t3__hint">Mova o cursor ou arraste para olhar em volta \u00b7 role ou use o controle para entrar no ambiente</p>' +
    '<div class="t3__bar"><button type="button" data-t3="-1" aria-label="Ambiente anterior">\u2190</button>' +
    '<label class="t3__walk"><span>Entrar</span><input type="range" min="0" max="100" value="0" aria-label="Entrar no ambiente"></label>' +
    '<button type="button" data-t3="1" aria-label="Pr\u00f3ximo ambiente">\u2192</button></div>';
  d.body.appendChild(ov);
  var cv = ov.querySelector('canvas'), flat = ov.querySelector('.t3__flat'), nameEl = ov.querySelector('.t3__name'), range = ov.querySelector('input'), hint = ov.querySelector('.t3__hint');

  var gl = null, pr, U = {}, vbuf, ibuf, nIdx = 0, tex, ready = false, failed = false;
  var VS = 'attribute vec3 aP;attribute vec2 aUV;uniform vec3 uCam;uniform vec2 uRot,uVP,uFit,uPan;uniform float uF;varying vec2 vUV;varying float vZ;' +
    'void main(){vec3 q=vec3(aP.xy-uCam.xy,aP.z-uCam.z);float c=cos(uRot.x),s=sin(uRot.x);q=vec3(q.x*c-q.z*s,q.y,q.x*s+q.z*c);' +
    'c=cos(uRot.y);s=sin(uRot.y);q=vec3(q.x,q.y*c-q.z*s,q.y*s+q.z*c);' +
    'vec2 sc=(uVP-uPan)*q.z+uF*q.xy;gl_Position=vec4(sc*uFit,q.z-.12,q.z);vUV=aUV;vZ=q.z;}';
  var FS = 'precision mediump float;uniform sampler2D uT;uniform float uFade;varying vec2 vUV;varying float vZ;' +
    'void main(){vec2 e=max(-vUV,vUV-1.);float o=max(max(e.x,e.y),0.);vec3 c=texture2D(uT,clamp(vUV,0.,1.)).rgb;c*=1.-smoothstep(0.,.14,o)*.93;' +
    'c*=mix(.82,1.,smoothstep(.15,.7,vZ));gl_FragColor=vec4(c*uFade,1.);}';

  function initGL() {
    if (gl || failed) return;
    gl = cv.getContext('webgl', { antialias: true, alpha: false });
    if (!gl) { failed = true; return; }
    function sh(t, s) { var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; }
    pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { failed = true; gl = null; return; }
    gl.useProgram(pr);
    ['uCam', 'uRot', 'uVP', 'uFit', 'uPan', 'uF', 'uT', 'uFade'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
    vbuf = gl.createBuffer(); ibuf = gl.createBuffer(); tex = gl.createTexture();
    gl.enable(gl.DEPTH_TEST); gl.clearColor(.012, .03, .04, 1);
  }

  var A = 1.5, VP = [0, 0];
  function mesh(room, aspect) {
    var p = ROOMS[room.k] || DEF; A = aspect;
    var vx = (p.vp[0] * 2 - 1) * A, vy = 1 - 2 * p.vp[1]; VP = [vx, vy];
    var L = (p.w[0] * 2 - 1) * A - vx, Rr = (p.w[2] * 2 - 1) * A - vx, T = (1 - 2 * p.w[1]) - vy, B = (1 - 2 * p.w[3]) - vy;
    var xs = [], ys = [], i, j;
    for (i = 0; i <= NX; i++) xs.push(-EXT + (1 + 2 * EXT) * i / NX);
    for (j = 0; j <= NY; j++) ys.push(-EXT + (1 + 2 * EXT) * j / NY);
    xs.push(p.w[0], p.w[2]); ys.push(p.w[1], p.w[3]);
    xs.sort(function (a, b) { return a - b; }); ys.sort(function (a, b) { return a - b; });
    var nx = xs.length, ny = ys.length, v = new Float32Array(nx * ny * 5), n = 0;
    for (j = 0; j < ny; j++) for (i = 0; i < nx; i++) {
      var x = (xs[i] * 2 - 1) * A, y = 1 - 2 * ys[j], dx = x - vx, dy = y - vy;
      var k = Math.max(1, dx > 0 ? dx / Rr : dx / L, dy > 0 ? dy / T : dy / B);
      var z = 1 / Math.min(k, KMAX);
      v[n++] = dx * z / F; v[n++] = dy * z / F; v[n++] = z; v[n++] = xs[i]; v[n++] = ys[j];
    }
    var idx = new Uint16Array((nx - 1) * (ny - 1) * 6); n = 0;
    for (j = 0; j < ny - 1; j++) for (i = 0; i < nx - 1; i++) {
      var a = j * nx + i, b = a + 1, c = a + nx, e = c + 1;
      idx[n++] = a; idx[n++] = c; idx[n++] = b; idx[n++] = b; idx[n++] = c; idx[n++] = e;
    }
    nIdx = idx.length;
    gl.bindBuffer(gl.ARRAY_BUFFER, vbuf); gl.bufferData(gl.ARRAY_BUFFER, v, gl.STATIC_DRAW);
    var lp = gl.getAttribLocation(pr, 'aP'), lu = gl.getAttribLocation(pr, 'aUV');
    gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 3, gl.FLOAT, false, 20, 0);
    gl.enableVertexAttribArray(lu); gl.vertexAttribPointer(lu, 2, gl.FLOAT, false, 20, 12);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibuf); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, idx, gl.STATIC_DRAW);
  }

  var cur = 0, open = false, raf = 0, fade = 0, fadeT = 1;
  var st = { x: 0, y: 0, w: 0, pan: 0 }, tg = { x: 0, y: 0, w: 0, pan: 0 }, lastInput = 0, t0 = 0, last = null;
  function load(i) {
    cur = (i + rooms.length) % rooms.length; var r = rooms[cur];
    nameEl.textContent = r.name + ' \u00b7 ' + (cur + 1) + ' / ' + rooms.length;
    tg.x = tg.y = tg.pan = 0; tg.w = 0; range.value = 0; fadeT = 0; ready = false;
    var im = new Image();
    im.onload = function () {
      if (rooms[cur] !== r) return;
      if (failed || !gl) { flat.src = r.src; flat.alt = r.name; ov.classList.add('t3--flat'); return; }
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
      var src = im, mx = Math.min(gl.getParameter(gl.MAX_TEXTURE_SIZE), 2048);
      if (im.naturalWidth > mx || im.naturalHeight > mx) {
        var c2 = d.createElement('canvas'), s = mx / Math.max(im.naturalWidth, im.naturalHeight);
        c2.width = Math.round(im.naturalWidth * s); c2.height = Math.round(im.naturalHeight * s); c2.getContext('2d').drawImage(im, 0, 0, c2.width, c2.height); src = c2;
      }
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, src);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      mesh(r, im.naturalWidth / im.naturalHeight);
      st.x = st.y = st.pan = 0; st.w = 0; fade = 0; fadeT = 1; ready = true;
      tg.w = .16; range.value = 16; lastInput = performance.now() - 1800; // pequeno avanco inicial revela a profundidade
    };
    im.src = r.src;
  }
  function size() {
    var dpr = Math.min(W.devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    if (gl) gl.viewport(0, 0, cv.width, cv.height);
  }
  function frame(now) {
    if (!open) return;
    raf = requestAnimationFrame(frame);
    if (!gl || !ready && fade <= 0) { if (gl) { size(); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT); } return; }
    var dt = Math.min(.05, last == null ? .016 : (now - last) / 1000); last = now; size();
    var ax = tg.x, ay = tg.y;
    if (!still && now - lastInput > 2500) { var t = (now - t0) / 1000; ax += Math.sin(t * .55) * .22; ay += Math.sin(t * .37) * .08; }
    var kk = Math.min(1, dt * 4.5);
    st.x += (ax - st.x) * kk; st.y += (ay - st.y) * kk; st.w += (tg.w - st.w) * Math.min(1, dt * 3); st.pan += (tg.pan - st.pan) * kk;
    fade += (fadeT - fade) * Math.min(1, dt * 5);
    var ca = cv.width / cv.height, zoom = 1.12, s = Math.max(1, ca / A) * zoom;
    var half = ca / s, maxPan = Math.max(0, A - half);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.uniform3f(U.uCam, st.x * .11, -st.y * .05, st.w * .42);
    gl.uniform2f(U.uRot, st.x * .14, st.y * .07);
    gl.uniform2f(U.uVP, VP[0], VP[1]); gl.uniform2f(U.uPan, st.pan * maxPan, 0);
    gl.uniform2f(U.uFit, s / ca, s); gl.uniform1f(U.uF, F); gl.uniform1f(U.uFade, fade); gl.uniform1i(U.uT, 0);
    gl.drawElements(gl.TRIANGLES, nIdx, gl.UNSIGNED_SHORT, 0);
  }
  var opener = null;
  function show(i) {
    opener = d.activeElement; initGL(); ov.classList.remove('t3--flat'); ov.classList.add('on'); d.documentElement.classList.add('t3-open');
    open = true; t0 = performance.now(); last = null; load(i); cancelAnimationFrame(raf); raf = requestAnimationFrame(frame);
    ov.querySelector('.t3__x').focus(); hint.classList.remove('off'); setTimeout(function () { hint.classList.add('off'); }, 6000);
  }
  function hide() { open = false; ov.classList.remove('on'); d.documentElement.classList.remove('t3-open'); cancelAnimationFrame(raf); if (opener && opener.focus) opener.focus(); }
  function input() { lastInput = performance.now(); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  links.forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault(); var k = a.getAttribute('data-tour');
      for (var i = 0; i < rooms.length; i++) if (rooms[i].k === k) { show(i); break; }
    });
  });
  ov.querySelector('.t3__x').addEventListener('click', hide);
  [].slice.call(ov.querySelectorAll('[data-t3]')).forEach(function (b) { b.addEventListener('click', function () { load(cur + (+b.getAttribute('data-t3'))); }); });
  range.addEventListener('input', function () { tg.w = range.value / 100; input(); });
  var drag = null;
  cv.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, y: e.clientY, tx: tg.x, ty: tg.y, pan: tg.pan }; try { cv.setPointerCapture(e.pointerId); } catch (x) { } input(); });
  cv.addEventListener('pointermove', function (e) {
    var w = cv.clientWidth, h = cv.clientHeight;
    if (drag) { var dx = (e.clientX - drag.x) / w, dy = (e.clientY - drag.y) / h; tg.x = clamp(drag.tx - dx * 2.2, -1, 1); tg.y = clamp(drag.ty - dy * 2.2, -1, 1); tg.pan = clamp(drag.pan - dx * 2.5, -1, 1); }
    else if (e.pointerType === 'mouse') { tg.x = (e.clientX / w - .5) * 2; tg.y = (e.clientY / h - .5) * 2; }
    input();
  });
  function up() { drag = null; }
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  ov.addEventListener('wheel', function (e) { e.preventDefault(); tg.w = clamp(tg.w - e.deltaY * .0012, 0, 1); range.value = Math.round(tg.w * 100); input(); }, { passive: false });
  d.addEventListener('keydown', function (e) {
    if (!open) return;
    if (e.key === 'Escape') hide();
    else if (e.key === 'ArrowRight') load(cur + 1); else if (e.key === 'ArrowLeft') load(cur - 1);
    else if (e.key === 'ArrowUp' || e.key === '+') { tg.w = clamp(tg.w + .1, 0, 1); range.value = Math.round(tg.w * 100); input(); }
    else if (e.key === 'ArrowDown' || e.key === '-') { tg.w = clamp(tg.w - .1, 0, 1); range.value = Math.round(tg.w * 100); input(); }
  });
  W.SPTOUR = { show: show, hide: hide, state: function () { return { open: open, ready: ready, failed: failed, cur: cur, n: rooms.length }; }, set: function (x, y, w) { tg.x = x; tg.y = y; tg.w = w; range.value = Math.round(w * 100); lastInput = performance.now() + 1e7; } };
})();
