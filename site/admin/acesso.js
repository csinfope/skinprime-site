/* Acesso ao painel da Skin Prime por usuário e senha.
 *
 * O painel (Sveltia CMS) grava no repositório do GitHub com uma chave de acesso (token).
 * Essa chave fica guardada criptografada em usuarios.json e só é aberta com a senha de um usuário:
 *   - a chave do GitHub é cifrada com uma chave mestra K (AES-GCM 256);
 *   - cada usuário tem um par de chaves (ECDH P-256); a parte privada é cifrada com a senha
 *     (PBKDF2-SHA256, 600 mil iterações) e K é entregue a cada usuário cifrada para a sua chave pública.
 * Assim o administrador cria usuários e troca a chave do GitHub sem precisar saber a senha de ninguém.
 */
const SKP = (() => {
  const REPO = 'csinfope/skinprime-site';
  const BRANCH = 'main';
  const PATH = 'site/admin/usuarios.json';
  const ITER = 600000;
  const SESSAO_HORAS = 12;
  const MIN_SENHA = 10;
  const EC = { name: 'ECDH', namedCurve: 'P-256' };
  const enc = new TextEncoder(), dec = new TextDecoder();
  const b64 = (buf) => { let s = ''; new Uint8Array(buf).forEach((c) => { s += String.fromCharCode(c); }); return btoa(s); };
  const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  const rnd = (n) => crypto.getRandomValues(new Uint8Array(n));
  const norm = (login) => String(login || '').trim().toLowerCase();

  async function chaveDaSenha(senha, salt, iter) {
    const base = await crypto.subtle.importKey('raw', enc.encode(senha), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: iter }, base,
      { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
  }
  async function fechar(key, bytes) {
    const iv = rnd(12);
    return { iv: b64(iv), ct: b64(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, bytes)) };
  }
  async function abrir(key, caixa) {
    return new Uint8Array(await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64(caixa.iv) }, key, unb64(caixa.ct)));
  }
  const chaveMestra = (raw) => crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['encrypt', 'decrypt']);
  async function chaveEcdh(privada, publicaJwk) {
    const pub = await crypto.subtle.importKey('jwk', publicaJwk, EC, false, []);
    return crypto.subtle.deriveKey({ name: 'ECDH', public: pub }, privada, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
  }
  async function entregarK(publicaJwk, rawK) {
    const eph = await crypto.subtle.generateKey(EC, true, ['deriveKey']);
    const caixa = await fechar(await chaveEcdh(eph.privateKey, publicaJwk), rawK);
    caixa.epk = await crypto.subtle.exportKey('jwk', eph.publicKey);
    return caixa;
  }
  async function cifrarPrivada(privJwk, senha) {
    const salt = rnd(16);
    const privada = await fechar(await chaveDaSenha(senha, salt, ITER), enc.encode(JSON.stringify(privJwk)));
    return { salt: b64(salt), iter: ITER, privada };
  }

  function validarSenha(senha) {
    if (String(senha || '').length < MIN_SENHA) throw new Error(`A senha precisa ter pelo menos ${MIN_SENHA} caracteres.`);
  }

  /** Cria a ficha de um usuário novo (ou nova senha para um usuário existente). */
  async function novoUsuario({ login, nome, papel }, senha, rawK) {
    validarSenha(senha);
    login = norm(login);
    if (!/^[a-z0-9._-]{3,40}$/.test(login)) throw new Error('Usuário: use de 3 a 40 letras sem acento, números, ponto, hífen ou sublinhado.');
    const par = await crypto.subtle.generateKey(EC, true, ['deriveKey']);
    const publica = await crypto.subtle.exportKey('jwk', par.publicKey);
    const privJwk = await crypto.subtle.exportKey('jwk', par.privateKey);
    return { login, nome: String(nome || login).trim(), papel: papel === 'admin' ? 'admin' : 'editor',
      ...(await cifrarPrivada(privJwk, senha)), publica, chave: await entregarK(publica, rawK),
      criado: new Date().toISOString().slice(0, 10) };
  }

  /** Abre o cofre com usuário e senha. Erro genérico se algo não bater. */
  async function desbloquear(dados, login, senha) {
    const u = (dados.usuarios || []).find((x) => x.login === norm(login));
    const falha = new Error('Usuário ou senha incorretos.');
    if (!u) { await chaveDaSenha(senha || '-', rnd(16), ITER).catch(() => {}); throw falha; }
    let privJwk;
    try {
      privJwk = JSON.parse(dec.decode(await abrir(await chaveDaSenha(senha, unb64(u.salt), u.iter || ITER), u.privada)));
    } catch (e) { throw falha; }
    const privada = await crypto.subtle.importKey('jwk', privJwk, EC, false, ['deriveKey']);
    const rawK = await abrir(await chaveEcdh(privada, u.chave.epk), u.chave);
    const token = dec.decode(await abrir(await chaveMestra(rawK), dados.cofre));
    return { usuario: u, rawK, token, privJwk };
  }

  /** Nova chave mestra e nova chave do GitHub, entregues a todos os usuários (sem saber as senhas). */
  async function trocarChave(dados, token) {
    const rawK = rnd(32);
    const cofre = await fechar(await chaveMestra(rawK), enc.encode(token.trim()));
    const usuarios = [];
    for (const u of dados.usuarios) usuarios.push({ ...u, chave: await entregarK(u.publica, rawK) });
    return { rawK, dados: { ...dados, cofre, usuarios } };
  }

  async function novoCofre(token) {
    const rawK = rnd(32);
    return { rawK, cofre: await fechar(await chaveMestra(rawK), enc.encode(token.trim())) };
  }

  // ---------- GitHub ----------
  async function gh(token, caminho, opts = {}) {
    const r = await fetch('https://api.github.com' + caminho, { ...opts,
      headers: { Accept: 'application/vnd.github+json', Authorization: 'Bearer ' + token, ...(opts.headers || {}) } });
    if (!r.ok) {
      const err = new Error(r.status === 401 ? 'A chave do GitHub foi recusada (expirada, revogada ou digitada errada).'
        : r.status === 403 || r.status === 404 ? 'A chave do GitHub não tem permissão de escrita neste site.'
          : `O GitHub respondeu com erro ${r.status}.`);
      err.status = r.status; throw err;
    }
    return r.status === 204 ? null : r.json();
  }
  async function verificarToken(token) {
    const repo = await gh(token.trim(), `/repos/${REPO}`);
    if (repo.permissions && !repo.permissions.push) throw new Error('A chave do GitHub não tem permissão de escrita neste site.');
  }
  async function lerDoGitHub(token) {
    const f = await gh(token, `/repos/${REPO}/contents/${PATH}?ref=${BRANCH}`);
    const texto = dec.decode(unb64(f.content.replace(/\s/g, '')));
    return { dados: JSON.parse(texto), sha: f.sha };
  }
  async function salvarNoGitHub(token, dados, mensagem) {
    let sha;
    try { sha = (await gh(token, `/repos/${REPO}/contents/${PATH}?ref=${BRANCH}`)).sha; } catch (e) { if (e.status !== 404) throw e; }
    const texto = JSON.stringify(dados, null, 1) + '\n';
    return gh(token, `/repos/${REPO}/contents/${PATH}`, { method: 'PUT', body: JSON.stringify({
      message: mensagem, content: b64(enc.encode(texto)), branch: BRANCH, ...(sha ? { sha } : {}) }) });
  }
  /** usuarios.json publicado com o site (null se ainda não existe). */
  async function lerPublicado() {
    const r = await fetch('usuarios.json?t=' + Date.now(), { cache: 'no-store' });
    if (r.status === 404) return null;
    if (!r.ok) throw new Error('Não consegui carregar a lista de usuários. Verifique a internet e tente de novo.');
    return r.json();
  }

  // ---------- sessão ----------
  const ls = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sem armazenamento */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* idem */ } },
  };
  function sessao() {
    const s = ls.get('skp-sessao');
    const u = ls.get('sveltia-cms.user');
    if (!s || !u || !u.token || !(s.expira > Date.now())) return null;
    return s;
  }
  function iniciarSessao(u, token) {
    ls.set('sveltia-cms.user', { backendName: 'github', token });
    ls.set('skp-sessao', { login: u.login, nome: u.nome, papel: u.papel, inicio: Date.now(), expira: Date.now() + SESSAO_HORAS * 3600e3 });
  }
  function encerrarSessao() { ls.del('skp-sessao'); ls.del('sveltia-cms.user'); }

  return { REPO, MIN_SENHA, norm, validarSenha, novoUsuario, desbloquear, trocarChave, novoCofre, cifrarPrivada, entregarK,
    verificarToken, lerDoGitHub, salvarNoGitHub, lerPublicado, sessao, iniciarSessao, encerrarSessao, ls };
})();
