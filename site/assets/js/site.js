/* Skin Prime v2 \u2014 intera\u00e7\u00f5es (sem depend\u00eancias) */
(function () {
  var d = document, root = d.documentElement, W = window;
  var R = root.getAttribute('data-root') || '';
  var WA = '558130364040';
  var fine = W.matchMedia('(hover:hover) and (pointer:fine)').matches;
  var still = W.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SP = W.SP || { posts: [], dis: [], quiz: [], tech: [] };
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return [].slice.call((c || d).querySelectorAll(s)); }
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function U(p) { var m = W.SPMAP; if (!m) return R + p; var k = p.split(/[?#]/)[0]; return (m[k] || k) + p.slice(k.length); }
  function postUrl(p) { return U('tratamentos/' + p[1] + '.html'); }
  function postImg(p) { return p[4] ? U('assets/img/posts/' + p[4] + '-m.jpg') : ''; }

  /* ---------- abertura */
  var boot = $('.boot');
  function booted() { root.classList.add('ready'); if (boot) setTimeout(function () { boot.remove(); }, 900); }
  if (boot && !root.classList.contains('skip-boot') && !still) {
    var bn = $('[data-boot-n]', boot), bi = $('.boot__bar i', boot), t0 = performance.now(), DUR = 1500;
    (function tick(t) {
      var k = Math.min(1, (t - t0) / DUR), e = 1 - Math.pow(1 - k, 3);
      bn.textContent = Math.round(e * 100); bi.style.transform = 'scaleX(' + e + ')';
      if (k < 1) requestAnimationFrame(tick); else { try { sessionStorage.setItem('sp-boot', '1'); } catch (x) { } booted(); }
    })(t0);
  } else booted();

  /* ---------- cabe\u00e7alho, menu, progresso */
  var hdr = $('.hdr'), bar = $('.prog i');
  function onScroll() {
    var y = W.scrollY; if (hdr) hdr.classList.toggle('is-stuck', y > 24);
    if (bar) bar.style.transform = 'scaleX(' + Math.min(1, y / Math.max(1, d.body.scrollHeight - W.innerHeight)) + ')';
  }
  onScroll(); W.addEventListener('scroll', onScroll, { passive: true });
  var burger = $('.burger');
  if (burger) {
    burger.addEventListener('click', function () { burger.setAttribute('aria-expanded', root.classList.toggle('menu-open')); });
    $$('.nav a').forEach(function (a) { a.addEventListener('click', function () { root.classList.remove('menu-open'); }); });
  }

  /* ---------- cursor */
  if (fine && !still) {
    var cur = d.createElement('div'); cur.className = 'cur'; cur.innerHTML = '<i></i><b></b>'; d.body.appendChild(cur);
    var cx = -100, cy = -100, rx = -100, ry = -100, ring = cur.lastChild, dot = cur.firstChild;
    W.addEventListener('pointermove', function (e) { cx = e.clientX; cy = e.clientY; cur.classList.add('on'); }, { passive: true });
    d.addEventListener('pointerover', function (e) {
      var t = e.target.closest ? e.target.closest('a,button,[data-tilt],input,select,textarea,.chip') : null;
      cur.classList.toggle('hot', !!t && !t.matches('input,select,textarea'));
      cur.classList.toggle('txt', !!t && t.matches('input,textarea'));
    });
    d.addEventListener('pointerdown', function () { cur.classList.add('down'); }); d.addEventListener('pointerup', function () { cur.classList.remove('down'); });
    d.documentElement.addEventListener('pointerleave', function () { cur.classList.remove('on'); });
    (function loop() {
      rx += (cx - rx) * .16; ry += (cy - ry) * .16;
      dot.style.transform = 'translate(' + cx + 'px,' + cy + 'px)'; ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px)';
      requestAnimationFrame(loop);
    })();
    root.classList.add('has-cur');
  }

  /* ---------- bot\u00f5es magn\u00e9ticos + brilho que segue o ponteiro + inclina\u00e7\u00e3o 3D */
  if (fine && !still) {
    $$('.btn,.wa').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .22) + 'px,' + ((e.clientY - r.top - r.height / 2) * .32) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }
  d.addEventListener('pointermove', function (e) {
    var g = e.target.closest ? e.target.closest('.glow') : null; if (!g) return;
    var r = g.getBoundingClientRect(); g.style.setProperty('--mx', (e.clientX - r.left) + 'px'); g.style.setProperty('--my', (e.clientY - r.top) + 'px');
    if (fine && !still && g.hasAttribute('data-tilt')) {
      var px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
      g.style.transform = 'perspective(900px) rotateY(' + (px * 7) + 'deg) rotateX(' + (-py * 7) + 'deg) translateZ(0)';
    }
  }, { passive: true });
  $$('[data-tilt]').forEach(function (g) { g.addEventListener('pointerleave', function () { g.style.transform = ''; }); });

  /* ---------- entradas, t\u00edtulos palavra a palavra, contadores */
  $$('.split').forEach(function (h) {
    [].slice.call(h.querySelectorAll('em')).forEach(function (em) { var n = em.nextSibling; if (n && n.nodeType === 3) { var m = n.textContent.match(/^[.,;:!?]+/); if (m) { em.appendChild(d.createTextNode(m[0])); n.textContent = n.textContent.slice(m[0].length); } } });
    var i = 0;
    (function walk(n) {
      [].slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var f = d.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return; if (/^\s+$/.test(w)) { f.appendChild(d.createTextNode(' ')); return; }
            var o = d.createElement('span'); o.className = 'w'; var s = d.createElement('span'); s.textContent = w; s.style.transitionDelay = (i++ * 55) + 'ms'; o.appendChild(s); f.appendChild(o);
          });
          n.replaceChild(f, c);
        } else if (c.nodeType === 1) walk(c);
      });
    })(h);
    h.classList.add('sp');
  });
  function count(el) {
    var to = +el.getAttribute('data-count'), t0 = performance.now();
    (function tick(t) {
      var k = Math.min(1, (t - t0) / 1600), e = 1 - Math.pow(1 - k, 4);
      el.textContent = Math.round(to * e).toLocaleString('pt-BR'); if (k < 1) requestAnimationFrame(tick);
    })(t0);
  }
  var rv = $$('.rv,.split,[data-count]');
  function reveal(el) { if (el.hasAttribute('data-count')) { if (!still) count(el); } el.classList.add('in'); }
  if ('IntersectionObserver' in W) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { reveal(e.target); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -7% 0px' });
    rv.forEach(function (el) { io.observe(el); });
    setTimeout(function () { rv.forEach(function (el) { el.classList.add('in'); }); }, 4500);
  } else rv.forEach(reveal);

  /* ---------- part\u00edculas: forma por se\u00e7\u00e3o + controles */
  function fx() {
    var F = W.SPFX; if (!F) return;
    var secs = $$('[data-fx]'), cur = null, hud = $('[data-hud-shape]'), LAB = { logo: 'Marca', helix: 'DNA', skin: 'Camadas da pele', cell: 'C\u00e9lula', ring: 'Lente', toxin: 'Toxina botul\u00ednica', face: 'Rosto em transforma\u00e7\u00e3o' };
    var hn = $('[data-hud-n]'); if (hn) hn.textContent = F.count.toLocaleString('pt-BR');
    function apply(s, shape) {
      var m = W.innerWidth < 760;
      F.go(shape || s.getAttribute('data-fx'));
      var kw = m ? 1 : Math.max(.7, Math.min(1, W.innerWidth / 1440)); // em janelas estreitas o rosto encolhe e vai para a direita, longe do texto
      F.place({ x: m ? 0 : +(s.getAttribute('data-fx-x') || 0) + (1 - kw) * .62, y: m ? +(s.getAttribute('data-fx-my') || .34) : +(s.getAttribute('data-fx-y') || 0), scale: +(s.getAttribute('data-fx-s') || 1) * kw, fade: +(s.getAttribute('data-fx-f') || (m ? .5 : .8)) });
    }
    function pick() {
      var mid = W.innerHeight * .5, best = null, bd = 1e9;
      secs.forEach(function (s) { var r = s.getBoundingClientRect(); if (r.top < mid + 80 && r.bottom > mid - 80) { var q = Math.abs((r.top + r.bottom) / 2 - mid); if (q < bd) { bd = q; best = s; } } });
      if (best && best !== cur) { cur = best; apply(best); sync(best.getAttribute('data-fx')); }
      else if (!best && cur) { cur = null; F.place({ fade: 0 }); }
    }
    var modes = $$('[data-go]');
    function sync(n) { modes.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-go') === n); }); if (hud) hud.textContent = LAB[n] || n; }
    modes.forEach(function (b) { b.addEventListener('click', function () { auto = false; var n = b.getAttribute('data-go'); apply($('.hero') || secs[0], n); sync(n); }); });
    W.addEventListener('scroll', pick, { passive: true }); W.addEventListener('resize', function () { cur = null; pick(); }); pick();
    // no her\u00f3i, as formas se alternam sozinhas at\u00e9 o visitante escolher uma
    var auto = false, seq = ['logo', 'face', 'helix', 'toxin', 'skin', 'cell'], si = 0;
    if (auto) setInterval(function () { if (!auto || cur !== $('.hero') || d.hidden) return; si = (si + 1) % seq.length; apply(cur, seq[si]); sync(seq[si]); }, 6500);
  }
  if (W.SPFX) fx(); else W.addEventListener('fx:ready', fx);
  var hp = $('[data-hud-p]');
  if (hp) W.addEventListener('pointermove', function (e) { hp.textContent = ('000' + e.clientX).slice(-4) + ' \u00b7 ' + ('000' + e.clientY).slice(-4); }, { passive: true });


  /* ---------- mapa facial interativo */
  var fmap = $('[data-fmap]'), fpan = $('[data-fpanel]');
  if (fmap && fpan && SP.fmap && SP.fmap.length) {
    var fpts = $$('[data-face-pt]', fmap), fsel = -1;
    function showArea(i) {
      if (i === fsel) return; fsel = i; var A = SP.fmap[i], h = '';
      fpts.forEach(function (b) { b.setAttribute('aria-pressed', +b.getAttribute('data-i') === i); });
      A.p.forEach(function (ix) { var q = SP.posts[ix]; h += '<a class="chip" href="' + postUrl(q) + '">' + esc(q[0]) + ' \u2192</a>'; });
      fpan.innerHTML = '<p class="label">' + esc(A.t) + '</p><p class="fpanel__d">' + esc(A.d) + '</p><div class="fpanel__l">' + h + '</div>';
      fpan.classList.remove('in'); void fpan.offsetWidth; fpan.classList.add('in');
    }
    fpts.forEach(function (b) {
      var i = +b.getAttribute('data-i');
      b.addEventListener('click', function () { showArea(i); });
      if (fine) b.addEventListener('pointerenter', function () { showArea(i); });
      b.addEventListener('focus', function () { showArea(i); });
    });
    showArea(4);
  }
  /* ---------- encontre seu tratamento */
  var fd = $('[data-finder]');
  if (fd && SP.quiz.length) {
    var fa = $('[data-finder-areas]', fd), fg = $('[data-finder-goals]', fd), fr = $('[data-finder-out]', fd), fc = $('[data-finder-cta]', fd), ai = 0, gi = 0;
    function drawOut() {
      var A = SP.quiz[ai], G = A.g[gi], h = '';
      G.p.forEach(function (ix, k) {
        var p = SP.posts[ix], im = postImg(p);
        h += '<a class="res glow" style="animation-delay:' + (k * 60) + 'ms" href="' + postUrl(p) + '">' + (im ? '<img src="' + im + '" alt="" loading="lazy">' : '<span class="res__ph">' + esc(p[0].charAt(0)) + '</span>') + '<div><b>' + esc(p[0]) + '</b><small>' + esc(p[3].slice(0, 96)) + '\u2026</small></div><i aria-hidden="true">\u2192</i></a>';
      });
      if (G.l) h += '<a class="res glow" href="' + U(G.l[1]) + '"><span class="res__ph">+</span><div><b>' + esc(G.l[0]) + '</b><small>' + esc(G.l[2]) + '</small></div><i aria-hidden="true">\u2192</i></a>';
      fr.innerHTML = h;
      fc.href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent('Ol\u00e1, Skin Prime! Tenho interesse em ' + A.t + ' \u2014 ' + G.t + '. Gostaria de agendar uma avalia\u00e7\u00e3o.');
      $('[data-finder-sum]', fd).textContent = A.t + ' \u00b7 ' + G.t;
    }
    function drawGoals() {
      fg.innerHTML = SP.quiz[ai].g.map(function (g, i) { return '<button type="button" class="chip" aria-pressed="' + (i === gi) + '" data-i="' + i + '">' + esc(g.t) + '</button>'; }).join('');
      drawOut();
    }
    fa.innerHTML = SP.quiz.map(function (a, i) { return '<button type="button" class="area glow" aria-pressed="' + (i === 0) + '" data-i="' + i + '"><span class="label">0' + (i + 1) + '</span><b>' + esc(a.t) + '</b><small>' + esc(a.d) + '</small></button>'; }).join('');
    fa.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; ai = +b.getAttribute('data-i'); gi = 0; $$('button', fa).forEach(function (x, i) { x.setAttribute('aria-pressed', i === ai); }); drawGoals(); });
    fg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; gi = +b.getAttribute('data-i'); $$('button', fg).forEach(function (x, i) { x.setAttribute('aria-pressed', i === gi); }); drawOut(); });
    drawGoals();
  }

  /* ---------- explorador de tecnologias */
  var tx = $('[data-tech]');
  if (tx && SP.tech.length) {
    var tl = $('[data-tech-list]', tx), tp = $('[data-tech-panel]', tx), ti = -1, tAuto = !still, tTimer;
    tl.innerHTML = SP.tech.map(function (t, i) { return '<button type="button" data-i="' + i + '"><span>' + ('0' + (i + 1)).slice(-2) + '</span>' + esc(t.n) + '</button>'; }).join('');
    function showTech(i) {
      if (i === ti) return; ti = i; var t = SP.tech[i], p = SP.posts[t.i], im = postImg(p);
      $$('button', tl).forEach(function (b, k) { b.setAttribute('aria-pressed', k === i); });
      tp.classList.remove('in'); void tp.offsetWidth;
      tp.innerHTML = '<div class="tech__img">' + (im ? '<img src="' + im + '" alt="">' : '') + '<span class="scan"></span></div><div class="tech__tx"><p class="label">Tecnologia ' + ('0' + (i + 1)).slice(-2) + ' / ' + ('0' + SP.tech.length).slice(-2) + '</p><h3>' + esc(t.n) + '</h3><p>' + esc(p[3]) + '\u2026</p><a class="arrow" href="' + postUrl(p) + '">Saber mais</a></div>';
      tp.classList.add('in');
    }
    tl.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { tAuto = false; showTech(+b.getAttribute('data-i')); } });
    tl.addEventListener('pointerover', function (e) { var b = e.target.closest('button'); if (b && fine) { tAuto = false; showTech(+b.getAttribute('data-i')); } });
    showTech(0);
    if (tAuto) tTimer = setInterval(function () { if (!tAuto) return clearInterval(tTimer); var r = tx.getBoundingClientRect(); if (r.top < W.innerHeight && r.bottom > 0 && !d.hidden) showTech((ti + 1) % SP.tech.length); }, 4200);
  }

  /* ---------- carrossel arrast\u00e1vel */
  $$('[data-reel]').forEach(function (reel) {
    var tr = $('.reel__track', reel), pb = $('.reel__bar i', reel), down = false, sx = 0, sl = 0, moved = 0;
    function upd() { if (pb) pb.style.transform = 'scaleX(' + Math.max(.08, (tr.scrollLeft + tr.clientWidth) / tr.scrollWidth) + ')'; }
    tr.addEventListener('scroll', upd, { passive: true }); upd();
    tr.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') return; down = true; moved = 0; sx = e.clientX; sl = tr.scrollLeft; });
    W.addEventListener('pointermove', function (e) { if (!down) return; moved = Math.max(moved, Math.abs(e.clientX - sx)); if (moved > 6) tr.classList.add('drag'); tr.scrollLeft = sl - (e.clientX - sx); });
    W.addEventListener('pointerup', function () { down = false; tr.classList.remove('drag'); });
    tr.addEventListener('click', function (e) { if (moved > 6) { e.preventDefault(); e.stopPropagation(); } }, true);
    $$('[data-reel-go]', reel).forEach(function (b) { b.addEventListener('click', function () { tr.scrollBy({ left: +b.getAttribute('data-reel-go') * tr.clientWidth * .7, behavior: 'smooth' }); }); });
  });

  /* ---------- busca instant\u00e2nea (paleta) */
  var pal = $('.pal');
  if (pal) {
    var pi = $('input', pal), po = $('.pal__out', pal), sel = 0, hits = [];
    function search(q) {
      q = norm(q.trim()); var a = [], b = [];
      if (q) {
        SP.dis.forEach(function (x) { var n = norm(x[0]), k = n.indexOf(q); if (k > -1) a.push([k, 'Doen\u00e7a', x[0], U('doencas/' + x[1] + '.html'), x[2] ? x[2] + ' imagens' : '']); });
        SP.posts.forEach(function (x) { var k = norm(x[0]).indexOf(q); if (k < 0 && norm(x[3]).indexOf(q) > -1) k = 50; if (k > -1) b.push([k, 'Tratamento', x[0], postUrl(x), '']); });
      } else {
        [['A Cl\u00ednica', 'clinica.html'], ['Especialistas', 'especialistas.html'], ['Tratamentos', 'tratamentos/index.html'], ['Doen\u00e7as dermatol\u00f3gicas', 'doencas/index.html'], ['Atlas de imagens', 'atlas/index.html']].forEach(function (x) { a.push([0, 'P\u00e1gina', x[0], U(x[1]), '']); });
      }
      function s(x, y) { return x[0] - y[0] || x[2].localeCompare(y[2]); }
      return b.sort(s).slice(0, 6).concat(a.sort(s).slice(0, 8));
    }
    function draw() {
      hits = search(pi.value); sel = Math.min(sel, Math.max(0, hits.length - 1));
      po.innerHTML = hits.length ? hits.map(function (h, i) { return '<a href="' + h[3] + '" class="' + (i === sel ? 'on' : '') + '"><span class="label">' + h[1] + '</span><b>' + esc(h[2]) + '</b><small>' + h[4] + '</small></a>'; }).join('') : '<p class="pal__no">Nada encontrado. Tente outro termo ou fale com a cl\u00ednica.</p>';
    }
    function open() { pal.classList.add('on'); root.classList.add('pal-open'); pi.value = ''; sel = 0; draw(); setTimeout(function () { pi.focus(); }, 40); }
    function close() { pal.classList.remove('on'); root.classList.remove('pal-open'); }
    $$('[data-pal]').forEach(function (b) { b.addEventListener('click', open); });
    pi.addEventListener('input', function () { sel = 0; draw(); });
    pal.addEventListener('click', function (e) { if (e.target === pal) close(); });
    d.addEventListener('keydown', function (e) {
      var typing = /input|textarea|select/i.test((e.target.tagName || ''));
      if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) { e.preventDefault(); open(); return; }
      if (!pal.classList.contains('on')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowDown') { e.preventDefault(); sel = (sel + 1) % Math.max(1, hits.length); draw(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); sel = (sel - 1 + hits.length) % Math.max(1, hits.length); draw(); }
      if (e.key === 'Enter' && hits[sel]) { location.href = hits[sel][3]; }
    });
  }
  // busca da biblioteca na home: sugest\u00f5es ao digitar
  var lq = $('[data-live]');
  if (lq) {
    var lo = $('[data-live-out]');
    lq.addEventListener('input', function () {
      var q = norm(lq.value.trim()), h = '';
      if (q.length > 1) SP.dis.filter(function (x) { return norm(x[0]).indexOf(q) > -1; }).slice(0, 7).forEach(function (x) { h += '<a href="' + U('doencas/' + x[1] + '.html') + '"><b>' + esc(x[0]) + '</b><small>' + (x[2] ? x[2] + ' imagens' : 'verbete') + '</small></a>'; });
      lo.innerHTML = h; lo.hidden = !h;
    });
  }

  /* ---------- formul\u00e1rio -> WhatsApp */
  var form = $('#contato-form');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = new FormData(form), L = ['Ol\u00e1, Skin Prime! Gostaria de agendar um atendimento.', ''];
    [['nome', 'Nome'], ['telefone', 'Telefone'], ['email', 'E-mail'], ['interesse', 'Interesse'], ['mensagem', 'Mensagem']].forEach(function (p) { var v = (f.get(p[0]) || '').toString().trim(); if (v) L.push(p[1] + ': ' + v); });
    W.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(L.join('\n')), '_blank', 'noopener');
    var ok = $('#contato-ok'); if (ok) ok.hidden = false;
  });

  /* ---------- filtros (tratamentos, doen\u00e7as, atlas) */
  var list = $('[data-filter-list]');
  if (list) {
    var items = $$('[data-k]', list), q = $('[data-filter-q]'), chips = $$('.chip[data-cat]'), groups = $$('[data-group]', list), empty = $('.empty'), cat = '';
    function apply() {
      var s = norm(q ? q.value : ''), n = 0;
      items.forEach(function (it) { var ok = (!s || it.getAttribute('data-k').indexOf(s) > -1) && (!cat || (' ' + (it.getAttribute('data-c') || '') + ' ').indexOf(' ' + cat + ' ') > -1); it.hidden = !ok; if (ok) n++; });
      groups.forEach(function (g) { g.hidden = !g.querySelector('[data-k]:not([hidden])'); });
      if (empty) empty.hidden = n > 0;
    }
    function setCat(c) { cat = c; chips.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-cat') === c); }); apply(); }
    chips.forEach(function (b) { b.addEventListener('click', function () { setCat(b.getAttribute('data-cat')); try { history.replaceState(null, '', cat ? '#' + cat : location.pathname + location.search); } catch (e) { } }); });
    if (q) { q.addEventListener('input', apply); var p = new URLSearchParams(location.search).get('q'); if (p) q.value = p; if (q.form) q.form.addEventListener('submit', function (e) { e.preventDefault(); }); }
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && chips.some(function (b) { return b.getAttribute('data-cat') === h; })) setCat(h); else apply();
  }

  /* ---------- lightbox */
  var links = $$('a[data-lb]');
  if (links.length) {
    var lb = d.createElement('div'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Imagem ampliada');
    lb.innerHTML = '<div class="lb__bar"><span class="lb__n"></span><button type="button" data-x>Fechar \u2715</button></div><div class="lb__stage"><img alt=""></div><div class="lb__foot"><button type="button" data-p>\u2190 Anterior</button><button type="button" data-nx>Pr\u00f3xima \u2192</button></div>';
    d.body.appendChild(lb);
    var im = $('img', lb), nn = $('.lb__n', lb), set = [], i = 0, last;
    function show(k) { i = (k + set.length) % set.length; im.src = set[i].href; im.alt = set[i].getAttribute('data-alt') || ''; nn.textContent = (set[i].getAttribute('data-alt') || 'Imagem') + ' \u00b7 ' + (i + 1) + ' / ' + set.length; }
    function closeLb() { lb.classList.remove('on'); d.body.style.overflow = ''; if (last) last.focus(); }
    links.forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); last = a; var g = a.getAttribute('data-lb'); set = links.filter(function (x) { return x.getAttribute('data-lb') === g; }); show(set.indexOf(a)); lb.classList.add('on'); d.body.style.overflow = 'hidden'; $('[data-x]', lb).focus(); }); });
    $('[data-x]', lb).addEventListener('click', closeLb);
    $('[data-p]', lb).addEventListener('click', function () { show(i - 1); });
    $('[data-nx]', lb).addEventListener('click', function () { show(i + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb__stage')) closeLb(); });
    d.addEventListener('keydown', function (e) { if (!lb.classList.contains('on')) return; if (e.key === 'Escape') closeLb(); if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
  }

  /* ---------- transi\u00e7\u00e3o entre p\u00e1ginas */
  if (!still) {
    d.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href]') : null;
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target || a.hasAttribute('data-lb') || a.hasAttribute('download')) return;
      var u; try { u = new URL(a.href, location.href); } catch (x) { return; }
      if (u.origin !== location.origin || !/^https?:/.test(u.protocol)) return;
      if (u.pathname === location.pathname && u.hash) return;
      e.preventDefault(); root.classList.add('leaving'); setTimeout(function () { location.href = a.href; }, 320);
    });
    W.addEventListener('pageshow', function () { root.classList.remove('leaving'); });
  }
})();
