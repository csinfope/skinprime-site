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
      x.font = '400 250px Belleza,"Bodoni Moda",Didot,serif'; x.strokeStyle = '#fff'; x.lineWidth = 7; x.lineJoin = 'round'; x.fillText('SKIN', w / 2, 250); x.strokeText('SKIN', w / 2, 250); x.lineWidth = 3;
      x.font = '400 62px Belleza,"Bodoni Moda",Didot,serif';
      var t = 'PRIME', sp = 34, tw = 0, i; for (i = 0; i < t.length; i++) tw += x.measureText(t[i]).width + sp;
      var px = w / 2 + 300 - tw; x.textAlign = 'left'; for (i = 0; i < t.length; i++) { x.fillText(t[i], px, 340); x.strokeText(t[i], px, 340); px += x.measureText(t[i]).width + sp; }
    }, 1100, 380, 3.1);
  }

  // seringa de toxina botulinica: agulha, canhao, corpo graduado com liquido, embolo e haste
  function toxin() {
    var a = new Float32Array(N * 3), tz = -.6, c = Math.cos(tz), s = Math.sin(tz);
    for (var i = 0; i < N; i++) {
      var k = rnd(), th = rnd() * Math.PI * 2, u, r;
      if (k < .1) { u = .75 + rnd() * .55; r = .012; }                                   // agulha
      else if (k < .16) { u = .62 + rnd() * .13; r = .1 - (u - .62) / .13 * .07; }       // canhao
      else if (k < .4) { u = -.45 + rnd() * 1.07; r = .17; }                             // corpo
      else if (k < .56) { u = -.45 + Math.round(rnd() * 10) / 10 * 1.07; r = .17; }      // graduacoes
      else if (k < .76) { u = .08 + rnd() * .54; r = Math.sqrt(rnd()) * .15; }           // liquido
      else if (k < .81) { u = .05 + rnd() * .04; r = Math.sqrt(rnd()) * .16; }           // embolo
      else if (k < .87) { u = -.45; r = .17 + rnd() * .16; }                             // aba
      else if (k < .95) { u = -1.05 + rnd() * 1.1; r = .045; }                           // haste
      else if (k < .985) { u = -1.07 + rnd() * .03; r = Math.sqrt(rnd()) * .21; }        // apoio do polegar
      else { u = 1.34 + rnd() * .22; r = rnd() * .02; }                                  // gota
      var x = r * Math.cos(th) + gauss() * .004, z = r * Math.sin(th) + gauss() * .004, y = (u - .12) * .9; x *= .9; z *= .9;
      a[i * 3] = x * c - y * s; a[i * 3 + 1] = x * s + y * c; a[i * 3 + 2] = z;
    }
    return a;
  }
  // rosto 3D em fatias (estilo malha de escaneamento), em dois estados com os mesmos pontos:
  // t=0 contorno mais caido; t=1 contorno elevado e definido. A varredura alterna entre eles.
  function lerpT(tab, y, t) {
    for (var i = 0; i < tab.length - 1; i++) {
      var p = tab[i], q = tab[i + 1];
      if (y <= p[0] && y >= q[0]) {
        var f = (p[0] - y) / (p[0] - q[0]); f = (1 - Math.cos(f * Math.PI)) / 2;
        var va = p[1] + (p[2] - p[1]) * t, vb = q[1] + (q[2] - q[1]) * t; return va + (vb - va) * f;
      }
    }
    var e = y > tab[0][0] ? tab[0] : tab[tab.length - 1]; return e[1] + (e[2] - e[1]) * t;
  }
  var FW = [[1.1, 0, 0], [1.0, .3, .3], [.8, .54, .54], [.5, .63, .63], [.2, .62, .62], [0, .6, .61], [-.25, .58, .55], [-.45, .54, .46], [-.62, .42, .32], [-.78, .3, .2], [-.9, .27, .24], [-1.15, .3, .28]];
  var FF = [[1.1, 0, 0], [.95, .36, .36], [.7, .57, .57], [.42, .63, .64], [.28, .58, .58], [0, .6, .6], [-.18, .62, .62], [-.3, .62, .63], [-.43, .56, .55], [-.6, .58, .6], [-.72, .54, .46], [-.84, .4, .2], [-.95, .26, .2], [-1.15, .24, .22]];
  var FB = [[1.1, 0, 0], [.9, -.5, -.5], [.5, -.76, -.76], [.1, -.74, -.74], [-.3, -.58, -.58], [-.7, -.36, -.36], [-1.15, -.33, -.33]];
  function g(v, c, s) { v = (v - c) / s; return Math.exp(-v * v); }
  function facePt(y, th, t, out, o) {
    var w = lerpT(FW, y, t), cs = Math.cos(th), sn = Math.sin(th), at = Math.abs(th), lift = t * .03;
    var x = w * sn, z = cs > 0 ? lerpT(FF, y, t) * cs : lerpT(FB, y, t) * cs * -1;
    if (cs > 0) {
      var ny = y > -.02 ? Math.max(0, 1 - (y + .02) / .32) : Math.max(0, 1 + (y + .02) / .1);
      z += .3 * ny * g(th, 0, .16 + .12 * ny);                                           // nariz
      z -= .1 * g(at, .5, .2) * g(y, .2 + lift, .085);                                   // olhos
      z += .035 * g(at, .45, .3) * g(y, .34 + lift, .05);                                // sobrancelha
      z += (.03 + .035 * t) * g(th, 0, .42) * (g(y, -.25, .045) + g(y, -.345, .05));     // labios
      z -= .03 * g(th, 0, .5) * g(y, -.297, .018);
      var ck = (.01 + .06 * t) * g(at, .85, .32) * g(y, .02 + lift, .2);                 // macas do rosto
      z += ck; x *= 1 + ck;
      z -= (1 - t) * .035 * g(at, .42, .1) * g(y, -.17, .13);                            // sulco nasolabial
      z += (1 - t) * .03 * g(at, .75, .25) * g(y, -.55, .12);                            // flacidez na mandibula
    }
    out[o] = x; out[o + 1] = y * .95 + .02; out[o + 2] = z - .05;
  }
  function faces() {
    var A = new Float32Array(N * 3), B = new Float32Array(N * 3), HP = Math.PI / 2;
    for (var i = 0; i < N; i++) {
      var k = rnd(), y, th, jy = 0, jt = 0, br = 0;
      if (k < .7) { y = 1.1 - Math.round(rnd() * 36) / 36 * 2.25; th = (rnd() * 2 - 1) * Math.PI; }
      else if (k < .91) { y = 1.1 - rnd() * 2.25; th = (Math.round(rnd() * 22) / 22 * 2 - 1) * Math.PI; }
      else {
        var f = rnd(), sgn = rnd() < .5 ? -1 : 1, u = rnd() * 2 - 1, an = rnd() * Math.PI * 2;
        if (f < .34) { th = sgn * (.5 + Math.cos(an) * .17); y = .2 + Math.sin(an) * .034 * (1 - .5 * Math.cos(an) * Math.cos(an)); br = 1; }           // contorno dos olhos
        else if (f < .56) { th = sgn * (.5 + u * .26); y = .335 - u * u * .03; br = 1; }                      // sobrancelhas
        else if (f < .86) { th = u * .32; var lp = Math.pow(1 - u * u, .8); y = rnd() < .5 ? -.297 + .05 * lp : -.297 - .06 * lp; } // labios
        else { th = u * .32; y = -.297; }                                        // base do nariz
      }
      if (k >= .7 && k < .91) jt = gauss() * .004;
      facePt(y + jy, th + jt, 0, A, i * 3); facePt(y + jy + br * 0, th + jt, 1, B, i * 3);
    }
    return [A, B];
  }
  var fc = null, SF = window.SPFACE;
  if (SF && SF.a) { // rosto real: malha facial amostrada de uma foto (gerado por build/gen_face.py)
    var dec = function (b64) { var bin = atob(b64), u8 = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); return new Int16Array(u8.buffer); };
    var toF = function (i16, n) { var f = new Float32Array(n); for (var i = 0; i < n; i++) f[i] = i16[i % i16.length] / SF.s; return f; };
    try { fc = [toF(dec(SF.a), N * 3), toF(dec(SF.b), N * 3)]; } catch (e) { fc = null; }
  }
  if (!fc) fc = faces();
  var shapes = { helix: helix(), skin: skin(), cell: cell(), ring: ring(), toxin: toxin(), face: fc[0], face2: fc[1] };
  shapes.logo = shapes.ring;
  // giro: positivo = rotacao continua; negativo = vai e volta (amplitude em radianos)
  var spin = { logo: 0, helix: 1, skin: .25, cell: 1, ring: 0, toxin: -.7, face: -.36, face2: -.36 };
  var pair = { face: 'face2', face2: 'face' };

  // ---------- GL
  var VS = 'attribute vec3 aA;attribute vec3 aB;attribute float aS;uniform float uMix,uT,uAsp,uDpr,uSpinA,uSpinB,uScale,uFade,uMode,uSm;uniform vec2 uMouse,uOff,uTilt;varying float vA;varying float vS;' +
    'float ang(float s){return s<0.?sin(uT*.45)*(-s):uT*.16*s;}' +
    'vec3 ry(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x*c+p.z*s,p.y,-p.x*s+p.z*c);}' +
    'vec3 rx(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x,p.y*c-p.z*s,p.y*s+p.z*c);}' +
    'void main(){float d=aS*.45;float m=clamp((uMix-d)/(1.-.45),0.,1.);m=m*m*(3.-2.*m);float glow=0.;' +
    'if(uMode>.5){float dd=aB.y-mix(1.45,-1.45,uMix);m=smoothstep(-.1,.1,dd);glow=exp(-dd*dd*110.);}' +
    'vec3 a=ry(aA,ang(uSpinA)),b=ry(aB,ang(uSpinB));vec3 p=mix(a,b,m);' +
    'float burst=sin(m*3.14159)*(1.-uMode);p+=burst*.55*vec3(sin(aS*91.),cos(aS*57.),sin(aS*33.));p.xz*=1.+glow*.05;' +
    'p+=.012*vec3(sin(uT*1.3+aS*40.),cos(uT*1.1+aS*70.),sin(uT*.9+aS*20.));' +
    'p=rx(ry(p,uTilt.x),uTilt.y);p*=uScale;float z=3.2-p.z;vec2 q=p.xy/z*2.1;q.x/=uAsp;q+=uOff;' +
    'vec2 dm=q-uMouse;dm.x*=uAsp;float dl=length(dm);float push=exp(-dl*dl*26.)*.085;q+=normalize(dm+1e-5)*push*vec2(1./uAsp,1.);' +
    'gl_Position=vec4(q,0.,1.);gl_PointSize=(1.7+fract(aS*7.)*2.6)*uDpr*(3.2/z)*(1.+push*7.)*(1.+glow*.7)*uSm;' +
    'vA=(.55+.45*fract(aS*13.))*uFade*clamp(1.9-z*.3,.35,1.)*(1.+push*6.)*(1.+glow*1.3);vS=aS;}';
  var FS = 'precision mediump float;varying float vA;varying float vS;void main(){vec2 c=gl_PointCoord-.5;float d=length(c);if(d>.5)discard;' +
    'float a=smoothstep(.5,.05,d);vec3 aq=vec3(.643,.824,.859),ro=vec3(.902,.733,.71),wh=vec3(.97,.97,.97);' +
    'vec3 col=fract(vS*3.7)<.14?ro:(fract(vS*5.3)<.3?wh:aq);gl_FragColor=vec4(col,a*vA);}';
  function sh(t, s) { var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; }
  var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { cv.remove(); return; }
  gl.useProgram(pr);
  var U = {}; ['uMix', 'uT', 'uAsp', 'uDpr', 'uSpinA', 'uSpinB', 'uScale', 'uFade', 'uMode', 'uSm', 'uMouse', 'uOff', 'uTilt'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
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

  // ---------- foto do rosto em relevo 3D (desenhada atras das particulas quando a forma e o rosto)
  var ph = null;
  if (SF && SF.g) (function () {
    var VS2 = 'attribute vec3 aP;attribute vec3 aDv;attribute vec2 aUV;uniform float uT,uAsp,uScale,uSpin,uScan,uFrom,uTo,uSweep;uniform vec2 uOff,uTilt;varying vec2 vUV;varying float vG;' +
      'vec3 ry(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x*c+p.z*s,p.y,-p.x*s+p.z*c);}' +
      'vec3 rx(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x,p.y*c-p.z*s,p.y*s+p.z*c);}' +
      'float ang(float s){return s<0.?sin(uT*.45)*(-s):uT*.16*s;}' +
      'void main(){float dd=aP.y-uScan;float m=smoothstep(-.1,.1,dd);float st=mix(uFrom,uTo,m);vG=exp(-dd*dd*520.)*uSweep;' +
      'vec3 p=aP+aDv*(1.-st);p=ry(p,ang(uSpin));p=rx(ry(p,uTilt.x),uTilt.y);p*=uScale;float z=3.2-p.z;vec2 q=p.xy/z*2.1;q.x/=uAsp;q+=uOff;' +
      'gl_Position=vec4(q*z,(z-3.2)*.25*z,z);vUV=aUV;}';
    var FS2 = 'precision mediump float;uniform sampler2D uTex;uniform float uAlpha;varying vec2 vUV;varying float vG;' +
      'void main(){vec4 c=texture2D(uTex,vUV);vec3 k=c.rgb*vec3(.95,.98,1.)+vec3(.643,.824,.859)*vG*.4;gl_FragColor=vec4(k,c.a*uAlpha);}';
    var p2 = gl.createProgram(); gl.attachShader(p2, sh(gl.VERTEX_SHADER, VS2)); gl.attachShader(p2, sh(gl.FRAGMENT_SHADER, FS2)); gl.linkProgram(p2);
    if (!gl.getProgramParameter(p2, gl.LINK_STATUS)) return;
    var g = dec(SF.g), gx = SF.gx, gy = SF.gy, nv = gx * gy, v = new Float32Array(nv * 8), i, j, n = 0;
    for (j = 0; j < gy; j++) for (i = 0; i < gx; i++) {
      var o = (j * gx + i) * 6;
      for (var c = 0; c < 6; c++) v[n++] = g[o + c] / SF.s;
      v[n++] = i / (gx - 1); v[n++] = j / (gy - 1);
    }
    var idx = new Uint16Array((gx - 1) * (gy - 1) * 6); n = 0;
    for (j = 0; j < gy - 1; j++) for (i = 0; i < gx - 1; i++) { var a = j * gx + i, b = a + 1, c2 = a + gx, e = c2 + 1; idx[n++] = a; idx[n++] = c2; idx[n++] = b; idx[n++] = b; idx[n++] = c2; idx[n++] = e; }
    var vb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vb); gl.bufferData(gl.ARRAY_BUFFER, v, gl.STATIC_DRAW);
    var ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, idx, gl.STATIC_DRAW);
    var tx = gl.createTexture(), U2 = {};
    ['uT', 'uAsp', 'uScale', 'uSpin', 'uScan', 'uFrom', 'uTo', 'uSweep', 'uOff', 'uTilt', 'uTex', 'uAlpha'].forEach(function (k) { U2[k] = gl.getUniformLocation(p2, k); });
    ph = { p: p2, vb: vb, ib: ib, n: idx.length, tx: tx, U: U2, ok: false, a: 0, lp: gl.getAttribLocation(p2, 'aP'), ld: gl.getAttribLocation(p2, 'aDv'), lu: gl.getAttribLocation(p2, 'aUV') };
    var im = new Image(), mp = window.SPMAP;
    im.onload = function () {
      gl.bindTexture(gl.TEXTURE_2D, tx); gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      ph.ok = true;
    };
    im.src = (mp && mp[SF.tex]) || (R + SF.tex);
  })();
  var stateOf = { face: 0, face2: 1 };
  function drawPhoto(now, dt) {
    if (!ph) return;
    var want = pair[to] ? (mode === 1 ? 1 : Math.max(0, Math.min(1, (mix - .45) * 2.5))) : 0;
    ph.a += (want - ph.a) * Math.min(1, dt * (want ? 3 : 7)); if (still) ph.a = want;
    if (!ph.ok || ph.a < .004) return;
    var isF = !!pair[to], sp = isF ? spin[to] : spin[from], f, t2, scan, sweep = 0;
    if (mode === 1) { f = stateOf[from]; t2 = stateOf[to]; scan = 1.45 - 2.9 * mix; sweep = 1; }
    else { f = t2 = isF ? stateOf[to] : (stateOf[from] || 0); scan = 9; }
    gl.useProgram(ph.p); gl.enable(gl.DEPTH_TEST);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.bindBuffer(gl.ARRAY_BUFFER, ph.vb);
    gl.enableVertexAttribArray(ph.lp); gl.vertexAttribPointer(ph.lp, 3, gl.FLOAT, false, 32, 0);
    gl.enableVertexAttribArray(ph.ld); gl.vertexAttribPointer(ph.ld, 3, gl.FLOAT, false, 32, 12);
    gl.enableVertexAttribArray(ph.lu); gl.vertexAttribPointer(ph.lu, 2, gl.FLOAT, false, 32, 24);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ph.ib);
    var u = ph.U;
    gl.uniform1f(u.uT, (now - t0) / 1000); gl.uniform1f(u.uAsp, W / H); gl.uniform1f(u.uScale, st.sc * (W < 760 ? .62 : 1)); gl.uniform1f(u.uSpin, sp || 0);
    gl.uniform1f(u.uScan, scan); gl.uniform1f(u.uFrom, f); gl.uniform1f(u.uTo, t2); gl.uniform1f(u.uSweep, sweep);
    gl.uniform2f(u.uOff, st.ox, st.oy); gl.uniform2f(u.uTilt, tilt.x, tilt.y);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, ph.tx); gl.uniform1i(u.uTex, 0);
    gl.uniform1f(u.uAlpha, ph.a * Math.min(1, st.fade * 1.15));
    gl.drawElements(gl.TRIANGLES, ph.n, gl.UNSIGNED_SHORT, 0);
    // volta ao programa das particulas
    gl.disable(gl.DEPTH_TEST); gl.blendFunc(gl.SRC_ALPHA, gl.ONE); gl.useProgram(pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, bS); gl.vertexAttribPointer(lS, 1, gl.FLOAT, false, 0, 0);
    bind(lA, from); bind(lB, to);
  }

  var from = 'cell', to = cv.getAttribute('data-shape') || 'logo', mix = 0, mixT = 1;
  if (!shapes[to]) to = 'helix';
  bind(lA, from); bind(lB, to);
  var st = { ox: 0, oy: 0, sc: 1, fade: 1 }, tg = { ox: 0, oy: 0, sc: 1, fade: 1 };
  var mouse = { x: 9, y: 9, tx: 9, ty: 9 }, tilt = { x: 0, y: 0, tx: 0, ty: 0 };
  var W = 0, H = 0, dpr = 1;

  var mode = 0, hold = 0; // mode 1 = varredura continua entre os dois estados do rosto
  function go(name) {
    if (!shapes[name] || name === to || (pair[name] && pair[to])) return;
    if (mode === 1) { from = mix > .5 ? to : from; mode = 0; } else from = to;
    to = name; mix = 0; bind(lA, from); bind(lB, to);
    window.dispatchEvent(new CustomEvent('fx:shape', { detail: name }));
  }
  function place(o) { // o: {x,y,scale,fade}
    tg.ox = o.x || 0; tg.oy = o.y || 0; tg.sc = o.scale || 1; tg.fade = o.fade == null ? 1 : o.fade;
  }
  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5); W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr; gl.viewport(0, 0, cv.width, cv.height);
  }
  size(); window.addEventListener('resize', size);
  window.addEventListener('pointermove', function (e) {
    mouse.tx = e.clientX / W * 2 - 1; mouse.ty = -(e.clientY / H * 2 - 1);
    tilt.tx = (e.clientX / W - .5) * .5; tilt.ty = (e.clientY / H - .5) * .3;
  }, { passive: true });
  window.addEventListener('pointerleave', function () { mouse.tx = 9; mouse.ty = 9; });

  var t0 = performance.now(), vis = !document.hidden, last = 0, raf = 0, lost = false;
  // um unico ciclo de animacao: nunca agenda um quadro se ja houver um pendente
  function kick() { if (!raf && vis && !lost) raf = requestAnimationFrame(frame); }
  document.addEventListener('visibilitychange', function () { vis = !document.hidden; if (vis) { last = 0; kick(); } });
  cv.addEventListener('webglcontextlost', function (e) { e.preventDefault(); lost = true; cv.style.opacity = 0; });
  cv.addEventListener('webglcontextrestored', function () {
    var again = false; try { again = !sessionStorage.getItem('sp-glr'); sessionStorage.setItem('sp-glr', '1'); } catch (e) { }
    if (again) location.reload();
  });
  function frame(now) {
    raf = 0;
    if (!vis || lost) return;
    try {
    var dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    if (mode === 0) {
      mix += (mixT - mix) * Math.min(1, dt * 1.5); if (mixT - mix < .002) mix = 1;
      if (mix === 1 && pair[to] && !still) { mode = 1; from = to; to = pair[to]; mix = 0; hold = 1.2; bind(lA, from); bind(lB, to); }
    } else if (hold > 0) hold -= dt;
    else {
      mix += dt / 3.4;
      if (mix >= 1) { from = to; to = pair[to]; mix = 0; hold = 1.8; bind(lA, from); bind(lB, to); }
    }
    gl.uniform1f(U.uMode, mode);
    ['ox', 'oy', 'sc', 'fade'].forEach(function (k) { st[k] += (tg[k] - st[k]) * Math.min(1, dt * 3); });
    mouse.x += (mouse.tx - mouse.x) * .2; mouse.y += (mouse.ty - mouse.y) * .2;
    tilt.x += (tilt.tx - tilt.x) * .05; tilt.y += (tilt.ty - tilt.y) * .05;
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    drawPhoto(now, dt);
    gl.uniform1f(U.uSm, ph ? 1 - .5 * ph.a : 1);
    gl.uniform1f(U.uMix, mix); gl.uniform1f(U.uT, (now - t0) / 1000); gl.uniform1f(U.uAsp, W / H); gl.uniform1f(U.uDpr, dpr);
    gl.uniform1f(U.uSpinA, spin[from] || 0); gl.uniform1f(U.uSpinB, spin[to] || 0);
    gl.uniform1f(U.uScale, st.sc * (W < 760 ? .62 : 1)); gl.uniform1f(U.uFade, st.fade);
    gl.uniform2f(U.uMouse, mouse.x, mouse.y); gl.uniform2f(U.uOff, st.ox, st.oy); gl.uniform2f(U.uTilt, tilt.x, tilt.y);
    gl.drawArrays(gl.POINTS, 0, N);
    } catch (e) { }
    if (!still) kick();
  }
  if (still) { mix = 1; st = tg; }
  kick();

  // a marca \u00e9 amostrada depois que a fonte carrega
  function setLogo(a) {
    if (!a) return;
    shapes.logo = a; if (bufs.logo) { gl.deleteBuffer(bufs.logo); delete bufs.logo; }
    if (to === 'logo') { bind(lB, 'logo'); } if (from === 'logo') bind(lA, 'logo');
  }
  function logoText() { var a = null; try { a = wordmark(); } catch (e) { } setLogo(a); }
  (function () { // amostra o logo real; se a imagem nao puder ser lida, desenha o nome com a fonte
    var im = new Image(), mp = window.SPMAP, src = 'assets/img/brand/logo-bone.png';
    im.onload = function () {
      var a = null;
      try { a = fromCanvas(function (x, w, h) { var k = Math.min(w / im.naturalWidth, h / im.naturalHeight) * .96, dw = im.naturalWidth * k, dh = im.naturalHeight * k; x.drawImage(im, (w - dw) / 2, (h - dh) / 2, dw, dh); }, 1000, 470, 2.05); } catch (e) { }
      if (a) setLogo(a); else logoText();
    };
    im.onerror = logoText;
    im.src = (mp && mp[src]) || (R + src);
  })();

  window.SPFX = { go: go, place: place, count: N, names: Object.keys(shapes) };
  window.dispatchEvent(new Event('fx:ready'));
})();
