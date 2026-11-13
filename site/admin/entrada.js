/* Tela de entrada do painel: usuário e senha. Só depois do login o painel (Sveltia CMS) é carregado. */
(function () {
  const tela = document.getElementById('tela');
  const $ = (s) => tela.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const LOGO = '<img class="skp-logo" src="../assets/img/brand/logo-teal.png" alt="Skin Prime">';

  function msg(texto, tipo) { const m = $('.msg'); m.className = 'msg ' + (tipo || 'erro'); m.textContent = texto; }
  function ocupado(form, sim, rotulo) {
    const b = form.querySelector('button[type=submit]');
    if (sim) { b.dataset.r = b.textContent; b.textContent = rotulo || 'Verificando…'; } else if (b.dataset.r) b.textContent = b.dataset.r;
    b.disabled = sim;
  }

  // ---------- painel ----------
  function abrirPainel(s) {
    document.body.className = '';
    tela.remove();
    // registra no histórico quem fez cada alteração
    const nome = JSON.stringify(s.nome).slice(1, -1);
    const f0 = window.fetch.bind(window);
    window.fetch = function (url, opts) {
      try {
        const u = typeof url === 'string' ? url : url && url.url;
        if (u && u.indexOf('api.github.com') >= 0 && opts && typeof opts.body === 'string') {
          if (opts.body.indexOf('createCommitOnBranch') >= 0) {
            opts = { ...opts, body: opts.body.replace(/("headline":")((?:[^"\\]|\\.)*)"/, (m, a, h) => `${a}${h} · por ${nome}"`) };
          } else if (/\/contents\//.test(u) && /"message":"/.test(opts.body)) {
            opts = { ...opts, body: opts.body.replace(/("message":")((?:[^"\\]|\\.)*)"/, (m, a, h) => `${a}${h} · por ${nome}"`) };
          }
        }
      } catch (e) { /* segue sem alterar */ }
      return f0(url, opts);
    };
    // sair do painel (ou chave recusada) volta para esta tela
    const set0 = Storage.prototype.setItem, del0 = Storage.prototype.removeItem;
    const saiu = () => {
      if (Date.now() - (s.inicio || 0) < 20000) SKP.ls.set('skp-aviso', 'A chave de acesso do painel foi recusada pelo GitHub. Peça a um administrador para atualizá-la em “Usuários”.');
      SKP.ls.del('skp-sessao');
      setTimeout(() => location.reload(), 50);
    };
    Storage.prototype.setItem = function (k, v) {
      set0.call(this, k, v);
      if (this === localStorage && k === 'sveltia-cms.user' && !/"token"/.test(v)) saiu();
    };
    Storage.prototype.removeItem = function (k) {
      del0.call(this, k);
      if (this === localStorage && k === 'sveltia-cms.user') saiu();
    };
    // se a tela de login do próprio painel aparecer (GitHub/token), volta para a nossa
    const vigia = setInterval(() => {
      const t = [...document.querySelectorAll('button')].map((b) => b.textContent).join(' ');
      if (/Sign In with GitHub|Sign In Using Access Token|Entrar com (o )?GitHub|Token de Acesso/i.test(t)) { clearInterval(vigia); SKP.encerrarSessao(); saiu(); }
    }, 700);
    // faixa com o nome, link de usuários (administradores) e sair
    const faixa = document.createElement('div');
    faixa.id = 'skp-faixa';
    faixa.innerHTML = `<span>${esc(s.nome)}</span>${s.papel === 'admin' ? '<a href="usuarios.html">Usuários</a>' : '<a href="usuarios.html#senha">Minha senha</a>'}<button type="button">Sair</button>`;
    faixa.querySelector('button').onclick = () => { SKP.encerrarSessao(); location.reload(); };
    document.body.appendChild(faixa);
    const sc = document.createElement('script');
    sc.src = 'vendor/sveltia-cms.js';
    document.body.appendChild(sc);
  }

  // ---------- login ----------
  function telaLogin(dados) {
    tela.innerHTML = `<div class="skp-wrap"><form class="skp-card" autocomplete="on">${LOGO}
      <h1>Painel administrativo</h1><p class="sub">Entre com o usuário e a senha que o administrador criou para você.</p>
      <label for="u">Usuário</label><input id="u" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" required>
      <label for="p">Senha</label><input id="p" name="password" type="password" autocomplete="current-password" required>
      <button class="full" type="submit">Entrar</button><div class="msg"></div>
      <p class="dica" style="text-align:center;margin-top:18px">Esqueceu a senha? Peça a um administrador para criar uma nova.</p></form></div>`;
    const aviso = SKP.ls.get('skp-aviso');
    if (aviso) { msg(aviso); SKP.ls.del('skp-aviso'); }
    const form = $('form');
    $('#u').focus();
    form.onsubmit = async (e) => {
      e.preventDefault();
      ocupado(form, true);
      try {
        const r = await SKP.desbloquear(dados, $('#u').value, $('#p').value);
        SKP.iniciarSessao(r.usuario, r.token);
        abrirPainel(SKP.sessao());
      } catch (err) { msg(err.message); ocupado(form, false); $('#p').select(); }
    };
  }

  // ---------- primeira configuração ----------
  function telaInicial() {
    tela.innerHTML = `<div class="skp-wrap"><form class="skp-card">${LOGO}
      <h1>Configuração inicial</h1><p class="sub">Crie o primeiro administrador do painel. Esta tela só aparece uma vez.</p>
      <label for="n">Seu nome</label><input id="n" required>
      <label for="u">Usuário</label><input id="u" autocomplete="username" autocapitalize="none" spellcheck="false" required>
      <div class="grid"><div><label for="p">Senha</label><input id="p" type="password" autocomplete="new-password" required></div>
      <div><label for="p2">Repita a senha</label><input id="p2" type="password" autocomplete="new-password" required></div></div>
      <p class="dica">Pelo menos ${SKP.MIN_SENHA} caracteres. Prefira uma frase fácil de lembrar.</p>
      <label for="t">Chave de acesso do GitHub</label><input id="t" type="password" autocomplete="off" spellcheck="false" required>
      <ol class="passos"><li>Entre no GitHub, em <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">Settings › Developer settings › Fine-grained tokens</a>.</li>
      <li>Repository access: <b>Only select repositories</b> › <b>${SKP.REPO}</b>.</li>
      <li>Permissions › Repository › <b>Contents: Read and write</b>. Gere e cole aqui.</li></ol>
      <p class="dica">A chave fica guardada criptografada; ninguém mais precisará dela para entrar.</p>
      <button class="full" type="submit">Criar administrador</button><div class="msg"></div></form></div>`;
    const form = $('form');
    form.onsubmit = async (e) => {
      e.preventDefault();
      try {
        if ($('#p').value !== $('#p2').value) throw new Error('As senhas não são iguais.');
        SKP.validarSenha($('#p').value);
        ocupado(form, true, 'Verificando a chave…');
        const token = $('#t').value.trim();
        await SKP.verificarToken(token);
        const { rawK, cofre } = await SKP.novoCofre(token);
        const u = await SKP.novoUsuario({ login: $('#u').value, nome: $('#n').value, papel: 'admin' }, $('#p').value, rawK);
        ocupado(form, true, 'Salvando…');
        await SKP.salvarNoGitHub(token, { versao: 1, cofre, usuarios: [u] }, `Painel: configura o acesso por usuário e senha · por ${u.nome}`);
        SKP.iniciarSessao(u, token);
        abrirPainel(SKP.sessao());
      } catch (err) { msg(err.message); ocupado(form, false); }
    };
  }

  // ---------- início ----------
  const s = SKP.sessao();
  if (s) { abrirPainel(s); return; }
  SKP.encerrarSessao();
  SKP.lerPublicado().then((dados) => (dados && dados.usuarios && dados.usuarios.length ? telaLogin(dados) : telaInicial()))
    .catch((err) => { tela.innerHTML = `<div class="skp-wrap"><div class="skp-card">${LOGO}<h1>Painel administrativo</h1><div class="msg erro" style="display:block">${esc(err.message)}</div></div></div>`; });
})();
