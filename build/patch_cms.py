#!/usr/bin/env python3
"""Adapta build/build.py para ler o conteúdo de content/ (editado pelo painel). Execução única."""
import os, re
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = 'build/build.py'; s = open(p, encoding='utf-8').read()
if 'SITE = jload(' in s:
    raise SystemExit('build.py já adaptado')


def cut(start, end_marker, repl, include_end=True):
    """Substitui o trecho entre start e end_marker (inclusive)."""
    global s
    i = s.index(start); j = s.index(end_marker, i) + (len(end_marker) if include_end else 0)
    s = s[:i] + repl + s[j:]


def rep(a, b, count=1, regex=False):
    global s
    if regex:
        s2, n = re.subn(a, b, s)
        assert n >= 1, a
        s = s2
    else:
        assert a in s, a[:80]
        s = s.replace(a, b) if count == 0 else s.replace(a, b, count)


# ---------------------------------------------------------------- A) configurações vindas do painel
cut("WA = 'https://wa.me/558130364040'", "'https://open.spotify.com/playlist/4Vmj4nMBTfzhT5obi0249Q')]\n", '''CONTENT = os.path.join(HERE, '..', 'content')


def jload(*parts):
    return json.load(open(os.path.join(CONTENT, *parts), encoding='utf-8'))


SITE = jload('config', 'site.json')
CT = SITE['contato']
HERO = SITE.get('abertura', {})
WA = 'https://wa.me/' + re.sub(r'\\D', '', str(CT.get('whatsapp', '')))
WA_MSG = WA + '?text=' + urllib.parse.quote(CT.get('mensagem_whatsapp', ''))
MAPS = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote_plus(CT.get('busca_mapa', ''))
MAP_EMBED = 'https://www.google.com/maps?q=' + urllib.parse.quote_plus(CT.get('busca_mapa', '')) + '&z=16&output=embed'
MAP_HTML = f'<div class="map"><iframe src="{MAP_EMBED}" title="Mapa: Skin Prime" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe><a class="map__open" href="{MAPS}" target="_blank" rel="noopener">Abrir no Google Maps →</a></div>'
REVISTA = SITE.get('revista_pdf', '')
SOCIAL = [(r.get('rede', ''), r.get('usuario', ''), r.get('link', '')) for r in SITE.get('redes', []) if r.get('link')]
PHONE = CT.get('telefone', '')
EMAIL = CT.get('email', '')
ADDR = [x for x in (CT.get('endereco_linha1'), CT.get('endereco_linha2'), CT.get('endereco_linha3')) if x]
ADDR_BR = '<br>'.join(html.escape(x) for x in ADDR)
COORD = CT.get('coordenadas', '')
EMP = SITE.get('empresa', {})
''')

# rodapé, contato e página da clínica
rep('<p>RioMar Trade Center<br>Av. República do Líbano, 251<br>Torre C · 19º andar · Sala 1905<br>Pina, Recife – PE · 51110-160</p>', '<p>{ADDR_BR}</p>')
rep('(81) 3036-4040 · WhatsApp', '{E(PHONE)} · WhatsApp')
rep('mailto:contato@skinprime.com.br?subject=', 'mailto:{EMAIL}?subject=')
rep('mailto:contato@skinprime.com.br">contato@skinprime.com.br', 'mailto:{EMAIL}">{E(EMAIL)}', 0)
rep('Clinical Center Rio Mar · Skin Prime · CNPJ 37.572.208/0001-95', '{E(EMP.get("razao_social", ""))} · CNPJ {E(EMP.get("cnpj", ""))}')
rep('8°05′S · 34°53′W', '{E(COORD)}', 0)
rep('(81) 3036-4040</a>', '{E(PHONE)}</a>', 0)
rep(r'RioMar Trade Center · Av\. República do Líbano, 251<br>Torre C, 19º andar – Sala 1905<br>Pina, Recife – PE · CEP 51110-160', '{ADDR_BR}', regex=True)

# tema (cores do painel)
rep('<link rel="stylesheet" href="{R}assets/css/site.css">', '<link rel="stylesheet" href="{R}assets/css/site.css">\n<link rel="stylesheet" href="{R}assets/css/theme.css">')

# ---------------------------------------------------------------- B) tratamentos e doenças
cut("POSTS = json.load(", "    p['words'] = len(text.split())\n", '''import markdown as _md


def mdhtml(t):
    return _md.markdown(t or '', extensions=['extra', 'sane_lists'])


def asset(p):
    return (p or '').strip().lstrip('/')


def thumb(p):
    p = asset(p)
    if not p:
        return ''
    b, e = os.path.splitext(p)
    return b + '-m' + e if os.path.exists(os.path.join(OUT, b + '-m' + e)) else p


def entries(folder):
    d = os.path.join(CONTENT, folder)
    return [(f[:-5], jload(folder, f)) for f in sorted(os.listdir(d)) if f.endswith('.json')] if os.path.isdir(d) else []


POSTS = []
for fname, j in entries('tratamentos'):
    if not (j.get('titulo') or '').strip():
        continue
    body_html = mdhtml(j.get('texto', ''))
    text = re.sub(r'<[^>]+>', ' ', body_html)
    p = dict(title=j['titulo'].strip(), s=slug(fname), date=str(j.get('data') or '2000-01-01')[:10], cats=j.get('categorias') or [],
             cover=asset(j.get('capa')), ordem=j.get('ordem', 9999), html=body_html)
    p['thumb'] = thumb(p['cover']); p['cover_f'] = p['cover']
    p['video'] = 'video' if '<video' in body_html else ''
    p['excerpt'] = (j.get('resumo') or re.sub(r'\\s+', ' ', text)).strip()[:220]
    p['words'] = len(text.split())
    POSTS.append(p)
POSTS.sort(key=lambda p: (-int(re.sub(r'\\D', '', p['date']) or 0), p['ordem'] if isinstance(p['ordem'], (int, float)) else 9999))
''')
cut("KEYS = ['epidemiologia'", "DIS.sort(key=lambda d: norm(d['t']))\n", '''DIS = []
for fname, j in entries('doencas'):
    t = re.sub(r'\\s+', ' ', j.get('titulo') or '').strip()
    if not t:
        continue
    toc = []

    def _hid(m, toc=toc):
        label = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        h = slug(label) or 'secao'
        while h in [x[0] for x in toc]:
            h += '-2'
        toc.append((h, label))
        return f'<h2 id="{h}">{m.group(1)}</h2>'
    body_html = re.sub(r'<h2>(.*?)</h2>', _hid, mdhtml(j.get('texto', '')))
    plain = re.sub(r'\\s+', ' ', re.sub(r'<[^>]+>', ' ', body_html)).strip()
    DIS.append(dict(t=t, s=slug(fname), imgs=[asset(x) for x in (j.get('imagens') or []) if x], body=body_html, toc=toc,
                    bib=(j.get('bibliografia') or '').strip(), upd=str(j.get('atualizado') or '').strip(),
                    lead=plain[:240], letter=(norm(t)[:1] or '#').upper(), trat=j.get('tratamentos') or [], exam=j.get('exames') or []))
DIS.sort(key=lambda d: norm(d['t']))
''')

# imagens: caminhos completos vindos do painel
rep('{R}assets/img/posts/{p["cover_f"]}-m.jpg', '{R}{p["thumb"]}')
rep('../assets/img/posts/{p["cover_f"]}.jpg', '../{p["cover"]}')
rep('''f"assets/img/posts/{p['cover_f']}.jpg"''', "p['cover']")
rep("p['cover_f']] for p in POSTS]", "p['thumb']] for p in POSTS]")
rep('../assets/img/atlas/{n}.jpg', '../{n}', 0)
rep('../assets/img/atlas/{m}.jpg', '../{m}', 0)
rep('../assets/img/atlas/{d["imgs"][0]}.jpg', '../{d["imgs"][0]}')

# corpo dos tratamentos (Markdown -> HTML)
cut("def post_body(p):", "    return b\n", '''def post_body(p):
    b = p['html']
    b = re.sub(r'(src|href)="/?assets/', r'\\1="../assets/', b)
    b = b.replace('<img ', '<img loading="lazy" ')
    b = re.sub(r'<a href="(https?://[^"]*)"', r'<a href="\\1" target="_blank" rel="noopener"', b)
    return b
''')

# ---------------------------------------------------------------- C) equipe e fotos da clínica
cut("TEAM = [\n", "CLINIC = [", '''TEAM = []
for fname, j in entries('equipe'):
    if not (j.get('nome') or '').strip():
        continue
    TEAM.append(dict(k=slug(fname), n=j['nome'].strip(), role=j.get('funcao', ''), reg=j.get('registro', ''), h=j.get('titulo', ''),
                     link=(j.get('link_rotulo') or 'Saiba mais', j.get('link_url') or ''), short=j.get('frase', ''),
                     tx=[x.strip() for x in re.split(r'\\n\\s*\\n', j.get('texto') or '') if x.strip()],
                     foto=asset(j.get('foto')) or 'assets/img/brand/favicon.svg', ordem=j.get('ordem') if isinstance(j.get('ordem'), (int, float)) else 99))
TEAM.sort(key=lambda t: (t['ordem'], t['n']))
CLINIC = [''', include_end=True)
cut("CLINIC = [('vista'", "('detalhe', 'Detalhes')]\n", '''CLINIC = []
for _ph in jload('config', 'clinica.json').get('fotos', []):
    _full = asset(_ph.get('imagem'))
    if _full:
        CLINIC.append((slug(os.path.splitext(os.path.basename(_full))[0]), _ph.get('legenda', ''), _full, thumb(_full)))
''')
s = s.replace("CLINIC = [CLINIC = []", "CLINIC = []")
rep("assets/img/team/{t['k']}.jpg", "{t['foto']}", 0)
rep('assets/img/clinic/{k}-m.jpg', '{th}', 0)
rep('assets/img/clinic/{k}.jpg', '{full}', 0)
rep('for i, (k, c) in enumerate(CLINIC, 1))', 'for i, (k, c, full, th) in enumerate(CLINIC, 1))')
rep('for k, c in CLINIC)', 'for k, c, full, th in CLINIC)')

# ---------------------------------------------------------------- D) abertura
rep('<p class="label">Recife · RioMar Trade Center · 19º andar</p>', '<p class="label">{E(HERO.get("rotulo", ""))}</p>')
rep('<h1 class="split">A arte da <em>dermatologia</em></h1>', '<h1 class="split">{E(HERO.get("titulo", ""))} <em>{E(HERO.get("titulo_destaque", ""))}</em></h1>')
rep(r'<p class="lead">A experiência e a tecnologia se encontram para trazer uma estrutura clínica nunca vista no Recife quando o assunto é <strong>dermatologia, estética, nutrição e saúde</strong>\.</p>',
    '<p class="lead">{HERO_LEAD}</p>', regex=True)
rep("R = ''\n", "R = ''\nHERO_LEAD = re.sub(r'^<p>|</p>$', '', mdhtml(HERO.get('texto', '')).strip())\n")

# ---------------------------------------------------------------- E) bloco "Na Skin Prime": tratamentos escolhidos no painel
cut("    c = CRUZ.get(d['t'], {'itens': []})", "(diag if it['tipo'] == 'Diagnóstico' else trat).append((nome, p))\n", '''    trat = [(n, post_by(DISP.get(n) or norm(n))) for n in d.get('trat', [])]
    diag = [(n, post_by(DISP.get(n) or norm(n))) for n in d.get('exam', [])]
''')
rep("OK_LEVELS = ('Indicado no texto', 'Área de atuação', 'Citado como exame')", "OK_LEVELS = ('Indicado no texto', 'Área de atuação', 'Citado como exame')\nDISP = {v[0]: v[1] for v in SERV.values()}")

# ---------------------------------------------------------------- F) cores -> assets/css/theme.css
rep("# ---------------------------------------------------------------- extras", '''# ---------------------------------------------------------------- cores do painel
def _hex(v, d):
    return v if isinstance(v, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', v.strip()) else d


_c = SITE.get('cores', {})
_t = dict(ink=_hex(_c.get('fundo'), '#f7f7f7'), bone=_hex(_c.get('texto'), '#1d2b2d'), mute=_hex(_c.get('texto_secundario'), '#4f6468'),
          rose=_hex(_c.get('botoes'), '#996059'), aqua=_hex(_c.get('destaque'), '#4a7079'), ftr=_hex(_c.get('rodape'), '#1d2b2d'))
write('assets/css/theme.css', '/* gerado a partir das cores do painel (content/config/site.json) */\\n'
      f":root{{--ink:{_t['ink']};--bone:{_t['bone']};--mute:{_t['mute']};--rose:{_t['rose']};--aqua:{_t['aqua']};"
      f"--grad:linear-gradient(100deg,{_t['aqua']},{_t['rose']})}}\\n"
      f"body{{background:{_t['ink']}}}\\n.ftr{{--ink:{_t['ftr']}}}\\n")

# ---------------------------------------------------------------- extras''')

open(p, 'w', encoding='utf-8').write(s)
print('build.py adaptado')
