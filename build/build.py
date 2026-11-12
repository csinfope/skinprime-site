#!/usr/bin/env python3
"""Gera o site estático da Skin Prime em ../site a partir de build/data/*.json.
Uso:  python3 build/build.py   (executar na raiz do projeto)"""
import json, re, os, html, unicodedata, datetime, collections, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'site')
IMG = os.path.join(OUT, 'assets', 'img')
# páginas geradas antes são apagadas: assim, uma doença ou publicação removida no painel some do site
for _sub in ('doencas', 'atlas', 'tratamentos'):
    _d = os.path.join(OUT, _sub)
    if os.path.isdir(_d):
        for _stale in os.listdir(_d):
            if _stale.endswith('.html'):
                os.remove(os.path.join(_d, _stale))
E = html.escape
CONTENT = os.path.join(HERE, '..', 'content')


def jload(*parts):
    return json.load(open(os.path.join(CONTENT, *parts), encoding='utf-8'))


SITE = jload('config', 'site.json')
CT = SITE['contato']
HERO = SITE.get('abertura', {})
WA = 'https://wa.me/' + re.sub(r'\D', '', str(CT.get('whatsapp', '')))
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
CATS = [('face', 'Face'), ('corpo', 'Corpo'), ('cabelo', 'Cabelo'), ('procedimentos', 'Procedimentos'),
        ('cirurgia-plástica', 'Cirurgia Plástica'), ('nutrição', 'Nutrição'),
        ('dermatologia-clínica', 'Dermatologia Clínica'), ('news', 'News')]
MESES = 'jan fev mar abr mai jun jul ago set out nov dez'.split()
ICON_IMG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 17-5-5-9 8"/></svg>'
ICON_TXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 16h7"/></svg>'
ICON_S = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.700 6.700 0 0 1-3.300-2.900c-.2-.4.2-.4.6-1.300.1-.200 0-.300 0-.500l-.8-1.800c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.700.300-.900.900-1 2.100-.300 3.400a11.400 11.400 0 0 0 4.700 4.300c1.700.700 2.400.800 3.200.600.500-.100 1.500-.600 1.700-1.200.200-.600.200-1.100.100-1.200z"/></svg>'


def slug(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def norm(s):
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()


def imgname(i):
    return i.split('.')[0].replace('~mv2', '').replace('_mv2', '').replace('96b8be_', '')


def has(rel):
    return os.path.exists(os.path.join(IMG, rel))


def fdate(iso):
    y, m, d = iso.split('-')
    return f'{int(d)} {MESES[int(m)-1]} {y}'


def write(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


# ---------------------------------------------------------------- layout
NAV = [('clinica.html', 'A Clínica', 'clinica'), ('especialistas.html', 'Especialistas', 'especialistas'),
       ('tratamentos/index.html', 'Tratamentos', 'tratamentos'), ('doencas/index.html', 'Doenças', 'doencas'),
       ('atlas/index.html', 'Atlas', 'atlas'), ('index.html#contato', 'Contato', 'contato')]


def page(rel, title, desc, body, cur='', og='assets/img/clinic/vista.jpg'):
    R = '../' * rel.count('/')
    nav = ''.join(f'<a href="{R}{h}"{" aria-current=\"page\"" if k == cur else ""}>{t}</a>' for h, t, k in NAV)
    soc = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, _, u in SOCIAL)
    shape = 'face' if rel == 'index.html' else 'ring'
    full = f'{title} · Skin Prime' if title else 'Skin Prime · A arte da dermatologia no Recife'
    return f'''<!doctype html>
<html lang="pt-BR" data-root="{R}">
<head>
<script>(function(){{var c="js";try{{if(sessionStorage.getItem("sp-boot"))c+=" skip-boot"}}catch(e){{}}document.documentElement.className=c}})()</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(full)}</title>
<meta name="description" content="{E(desc[:300])}">
<meta name="theme-color" content="#f7f7f7">
<meta property="og:title" content="{E(full)}">
<meta property="og:description" content="{E(desc[:300])}">
<meta property="og:image" content="https://www.skinprime.com.br/{og}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="{R}assets/img/brand/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{R}assets/css/site.css">
<link rel="stylesheet" href="{R}assets/css/theme.css">
</head>
<body>
<canvas id="fx" data-shape="{shape}" aria-hidden="true"></canvas>
<div class="boot" aria-hidden="true"><div class="boot__in"><img src="{R}assets/img/brand/logo-teal.png" alt="" width="500" height="234"><div class="boot__bar"><i></i></div><p class="label"><span data-boot-n>0</span>% · calibrando sensores</p></div></div>
<div class="prog" aria-hidden="true"><i></i></div><div class="veil" aria-hidden="true"></div>
<header class="hdr"><div class="wrap hdr__in">
<a class="hdr__logo" href="{R}index.html" aria-label="Skin Prime — início"><img src="{R}assets/img/brand/logo-teal.png" alt="Skin Prime" width="500" height="234"></a>
<button class="find" type="button" data-pal aria-label="Buscar no site">{ICON_S}<span>Buscar</span><kbd>/</kbd></button>
<button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false"><i></i><i></i></button>
<nav class="nav" aria-label="Principal">{nav}<a class="btn btn--solid" href="{WA_MSG}" target="_blank" rel="noopener">Agendar</a></nav>
</div></header>
<main>
{body}
</main>
<footer class="ftr"><div class="wrap">
<div class="ftr__top">
<div><img src="{R}assets/img/brand/logo-bone.png" alt="Skin Prime" width="500" height="234" loading="lazy"><p>A arte da dermatologia.<br>Saúde, beleza e bem-estar no Recife.</p></div>
<div><h4>Navegar</h4><ul>{''.join(f'<li><a href="{R}{h}">{t}</a></li>' for h, t, _ in NAV)}</ul></div>
<div><h4>Endereço</h4><p>{ADDR_BR}</p></div>
<div><h4>Contato</h4><ul><li><a href="{WA_MSG}" target="_blank" rel="noopener">{E(PHONE)} · WhatsApp</a></li><li><a href="mailto:{EMAIL}">{E(EMAIL)}</a></li>{soc}</ul></div>
</div>
<div class="ftr__bot"><span>© {datetime.date.today().year} {E(EMP.get("razao_social", ""))} · CNPJ {E(EMP.get("cnpj", ""))}</span><span>{E(COORD)} · 19º andar</span></div>
</div></footer>
<a class="wa" href="{WA_MSG}" target="_blank" rel="noopener" aria-label="Falar pelo WhatsApp">{ICON_WA}</a>
<div class="pal" role="dialog" aria-modal="true" aria-label="Busca"><div class="pal__box"><div class="pal__in">{ICON_S}<label class="sr" for="pal-q">Buscar</label><input id="pal-q" type="search" placeholder="Busque um tratamento ou doença…" autocomplete="off"><kbd>esc</kbd></div><div class="pal__out"></div></div></div>
<script src="{R}assets/js/data.js" defer></script>
<script src="{R}assets/js/face.js" defer></script>
<script src="{R}assets/js/fx.js" defer></script>
<script src="{R}assets/js/site.js" defer></script>
<script src="{R}assets/js/tour.js" defer></script>
</body>
</html>
'''


def phead(R, crumbs, label, h1, lead='', extra=''):
    c = f'<a href="{R}index.html">Início</a>' + ''.join(
        (f'<span><a href="{R}{h}">{E(t)}</a></span>' if h else f'<span>{E(t)}</span>') for t, h in crumbs)
    return f'''<section class="phead"><div class="wrap">
<nav class="crumb" aria-label="Você está em">{c}</nav>
{f'<div class="phead__row"><h1 class="split">{h1}</h1>{extra}</div>' if extra else f'<h1 class="split">{h1}</h1>'}
{f'<p class="lead">{lead}</p>' if lead else ''}
{f'<p class="label" style="margin-top:22px">{label}</p>' if label else ''}
</div></section>'''


def cta(R):
    return f'''<section class="sec band--light"><div class="wrap cta">
<p class="label">Agende sua visita</p>
<h2 class="split">Sua pele merece um olhar <em>atento</em>.</h2>
<p class="lead">Fale com nossa equipe e faça parte da melhor experiência em saúde, beleza e bem-estar do Recife.</p>
<a class="btn btn--solid" href="{WA_MSG}" target="_blank" rel="noopener">{ICON_WA} Agendar pelo WhatsApp</a>
</div></section>'''


# ---------------------------------------------------------------- dados
import markdown as _md


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
    p['excerpt'] = (j.get('resumo') or re.sub(r'\s+', ' ', text)).strip()[:220]
    p['words'] = len(text.split())
    POSTS.append(p)
POSTS.sort(key=lambda p: (-int(re.sub(r'\D', '', p['date']) or 0), p['ordem'] if isinstance(p['ordem'], (int, float)) else 9999))

DIS = []
for fname, j in entries('doencas'):
    t = re.sub(r'\s+', ' ', j.get('titulo') or '').strip()
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
    plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body_html)).strip()
    DIS.append(dict(t=t, s=slug(fname), imgs=[asset(x) for x in (j.get('imagens') or []) if x], body=body_html, toc=toc,
                    bib=(j.get('bibliografia') or '').strip(), upd=str(j.get('atualizado') or '').strip(),
                    lead=plain[:240], letter=(norm(t)[:1] or '#').upper(), trat=j.get('tratamentos') or [], exam=j.get('exames') or []))
DIS.sort(key=lambda d: norm(d['t']))
N_IMG = sum(len(d['imgs']) for d in DIS)
NI = f'{N_IMG:,}'.replace(',', '.')
BY_LETTER = collections.OrderedDict()
for d in DIS:
    BY_LETTER.setdefault(d['letter'], []).append(d)
print(f'{len(POSTS)} posts · {len(DIS)} doenças · {N_IMG} imagens de atlas')


def card(p, R):
    if p['cover_f']:
        im = f'<div class="card__img{" card__img--video" if p["video"] else ""}"><img src="{R}{p["thumb"]}" alt="" loading="lazy" width="640" height="480"></div>'
    else:
        im = f'<div class="card__img card__img--none{" card__img--video" if p["video"] else ""}"><span>{E(p["title"].strip()[0])}</span></div>'
    cats = ' · '.join(dict(CATS)[c] for c in p['cats'][:2])
    return f'''<a class="card glow" href="{R}tratamentos/{p['s']}.html" data-k="{E(norm(p['title']+' '+p['excerpt']))}" data-c="{E(' '.join(p['cats']))}">
{im}
<div class="meta">{f'<b>{E(cats)}</b>' if cats else ''}<span>{fdate(p['date'])}</span></div>
<h3>{E(p['title'].strip())}</h3>
<p>{E(p['excerpt'])}</p>
</a>'''


# ---------------------------------------------------------------- especialistas
TEAM = []
for fname, j in entries('equipe'):
    if not (j.get('nome') or '').strip():
        continue
    TEAM.append(dict(k=slug(fname), n=j['nome'].strip(), role=j.get('funcao', ''), reg=j.get('registro', ''), h=j.get('titulo', ''),
                     link=(j.get('link_rotulo') or 'Saiba mais', j.get('link_url') or ''), short=j.get('frase', ''),
                     tx=[x.strip() for x in re.split(r'\n\s*\n', j.get('texto') or '') if x.strip()],
                     foto=asset(j.get('foto')) or 'assets/img/brand/favicon.svg', ordem=j.get('ordem') if isinstance(j.get('ordem'), (int, float)) else 99))
TEAM.sort(key=lambda t: (t['ordem'], t['n']))
CLINIC = []
for _ph in jload('config', 'clinica.json').get('fotos', []):
    _full = asset(_ph.get('imagem'))
    if _full:
        CLINIC.append((slug(os.path.splitext(os.path.basename(_full))[0]), _ph.get('legenda', ''), _full, thumb(_full)))
TECH = ['Atria II', 'Morpheus', 'Ulthera', 'Ultraformer 3', 'CoolSculpting', 'Emsculpt', 'Exilis Ultra 360º', 'Vanquish',
        'X-Wave', 'Vela Shape 2', 'Spectra XT', 'EndyMed', 'Vectra H2', 'LifeViz', 'ZYE Smart Laser', 'Laser de CO2',
        'Dermatoscopia Digital', 'Laser de Picossegundos', 'Ultraction 3D']

# ---------------------------------------------------------------- dados para as interações (data.js)
def find_posts(keys, cat=None, limit=5):
    out = []
    for i, p in enumerate(POSTS):
        t = norm(p['title'])
        if (cat and cat in p['cats']) or any(k in t for k in keys):
            if i not in out and p['words'] > 20:
                out.append(i)
    return out[:limit]


QUIZ = [
    ('Face', 'Rugas, flacidez, manchas, textura e olheiras', [
        ('Rugas e linhas de expressão', ['toxina botulinica a', 'botox', 'preenchimento', 'acido hialuronico', 'rejuvenescimento'], None),
        ('Flacidez e contorno', ['morpheus: conheca', 'ulthera', 'ultraformer', 'fios de sustentacao', 'bioestimulador', 'atria', 'papada'], None),
        ('Manchas e melasma', ['melasma', 'manchas', 'peelings', 'luz intensa', 'picossegundos', 'spectra'], None),
        ('Textura, poros e cicatrizes', ['microagulhamento', 'laser de co2', 'cicatrizes', 'dermoabrasao', 'peeling de cristal', 'zye'], None),
        ('Olheiras', ['olheiras'], None)]),
    ('Corpo', 'Gordura localizada, celulite, definição e depilação', [
        ('Gordura localizada', ['gordura localizada', 'coolsculp', 'vanquish', 'emptiers', 'lipoaspiracao'], None),
        ('Flacidez e celulite', ['flacidez e celulite', 'vela shape', 'x-wave', 'exilis', 'radiofrequencia', 'endymed', 'ultraction'], None),
        ('Definição muscular', ['emsculpt'], None),
        ('Estrias e cicatrizes', ['estrias', 'mmp e laser'], None),
        ('Depilação a laser', ['depilacao'], None),
        ('Cirurgia plástica', ['abdominoplastia', 'mamoplastia', 'lipoaspiracao', 'rinoplastia', 'blefaroplastia', 'ritidoplastia', 'otoplastia'], None)]),
    ('Cabelo', 'Queda, afinamento e saúde do couro cabeludo', [
        ('Queda e afinamento', ['capilar', 'tricologia', 'mmp', 'intradermoterapia'], None),
        ('Cuidados em casa', ['cabelos saudaveis'], None),
        ('Doenças do couro cabeludo', ['dermatite seborreica'], ('Alopecias e foliculites', 'doencas/index.html?q=alopecia', 'Verbetes na biblioteca de doenças'))]),
    ('Pele e saúde', 'Diagnóstico, doenças de pele, nutrição e rotina', [
        ('Avaliação e diagnóstico', ['dermatoscopia', 'biopsia', 'vectra', 'lifeviz', 'avaliacao mais eficaz'], None),
        ('Pequenos procedimentos', ['curetagem', 'eletrocauter', 'pequenas cirurgias', 'tatuagens', 'fototerapia'], None),
        ('Doenças de pele', ['alergia de contato', 'vitiligo', 'acantose', 'doencas dermatologicas mais'], ('Biblioteca de doenças', 'doencas/index.html', f'{len(DIS)} verbetes em ordem alfabética')),
        ('Nutrição', ['nutricao'], None),
        ('Rotina de cuidados', ['skincare', '60 anos'], None)]),
]
quiz = []
for t, dsc, goals in QUIZ:
    g = []
    for gt, keys, link in goals:
        ps = find_posts(keys)
        if ps or link:
            item = {'t': gt, 'p': ps}
            if link:
                item['l'] = list(link)
            g.append(item)
    quiz.append({'t': t, 'd': dsc, 'g': g})
TECHK = [('Atria II', 'atria'), ('Morpheus', 'morpheus: conheca'), ('Ulthera', 'ulthera'), ('Ultraformer 3', 'ultraformer'),
         ('CoolSculpting', 'coolsculp'), ('Emsculpt', 'emsculpt'), ('Exilis Ultra 360º', 'exilis'), ('Vanquish', 'vanquish'),
         ('X-Wave', 'x-wave'), ('Vela Shape 2', 'vela shape'), ('Spectra XT', 'spectra'), ('EndyMed', 'endymed'),
         ('Vectra H2', 'vectra'), ('LifeViz', 'lifeviz'), ('ZYE Smart Laser', 'zye'), ('Laser de CO2', 'laser de co2'),
         ('Laser de Picossegundos', 'picossegundos'), ('Dermatoscopia Digital', 'dermatoscopia'), ('Ultraction 3D', 'ultraction')]
tech = []
for n, k in TECHK:
    m = [i for i, p in enumerate(POSTS) if k in norm(p['title'])]
    if m:
        tech.append({'n': n, 'i': m[0]})
FMAP = [('testa', 'Testa e glabela', 'Linhas de expressão e rugas dinâmicas.', ['toxina botulinica a', 'botox (toxina', 'toxina botulinica alem'], ''),
        ('olhos', 'Olhos e olheiras', 'Olheiras, pálpebras e região periorbital.', ['olheiras', 'blefaroplastia'], ''),
        ('macas', 'Maçãs do rosto', 'Volume, sustentação e estímulo de colágeno.', ['bioestimulador', 'preenchimento injetavel', 'rejuvenescimento 4d'], 'l'),
        ('labios', 'Lábios', 'Contorno, hidratação e volume.', ['acido hialuronico', 'preenchimento ou btx'], 'l'),
        ('mandibula', 'Mandíbula e contorno', 'Definição do contorno facial e sustentação.', ['fios de sustentacao', 'ultraformer', 'ulthera'], ''),
        ('papada', 'Papada e pescoço', 'Gordura submentoniana e flacidez.', ['papada', 'ultrassom micro', 'radiofrequencia'], 'l')]
fmap = [{'k': k, 't': t, 'd': d2, 'p': find_posts(keys, limit=3)} for k, t, d2, keys, _ in FMAP]
data = {'posts': [[p['title'].strip(), p['s'], ' '.join(p['cats']), p['excerpt'][:170], p['thumb']] for p in POSTS],
        'dis': [[d['t'], d['s'], len(d['imgs'])] for d in DIS], 'quiz': quiz, 'tech': tech, 'fmap': fmap}
write('assets/js/data.js', 'window.SP=' + json.dumps(data, separators=(',', ':')) + ';')
print('quiz:', [(q['t'], [(g['t'], len(g['p'])) for g in q['g']]) for q in quiz], '· tech:', len(tech))

# ---------------------------------------------------------------- home
R = ''
HERO_LEAD = re.sub(r'^<p>|</p>$', '', mdhtml(HERO.get('texto', '')).strip())
docs = ''.join(f'''<article class="doc glow rv" data-tilt><div class="doc__ph"><img src="{t['foto']}" alt="{E(t['n'])}" loading="lazy" width="640" height="640"></div>
<div><h3>{E(t['n'])}</h3></div><p class="reg"><b>{t['role']}</b>{t['reg']}</p><p>{E(t['short'])}</p>
<a class="arrow" href="especialistas.html#{t['k']}">Conhecer</a></article>''' for t in TEAM)
letters = ''.join((f'<a href="doencas/index.html#letra-{L}">{L}</a>' if L in BY_LETTER else f'<span>{L}</span>') for L in 'ABCDEFGHIJKLMNOPQRSTUVXZ')
tick = ''.join(f'<span>{E(t)}</span>' for t in TECH) * 2
reel = ''.join(f'<a href="{full}" data-tour="{k}" data-alt="{E(c)}" draggable="false"><img src="{th}" alt="{E(c)}" loading="lazy" width="900" height="600" draggable="false"><span class="cap3d">Ver em 3D</span><span class="cap">{i:02d} · {E(c)}</span></a>' for i, (k, c, full, th) in enumerate(CLINIC, 1))
home = f'''<section class="hero" data-fx="face" data-fx-x=".43" data-fx-y=".04" data-fx-s="1.02" data-fx-f="1" data-fx-my=".5">
<img class="hero__face" src="assets/img/brand/face.webp" alt="Rosto feminino com contorno facial definido" width="720" height="654">
<div class="wrap hero__in">
<p class="label">{E(HERO.get("rotulo", ""))}</p>
<h1 class="split">{E(HERO.get("titulo", ""))} <em>{E(HERO.get("titulo_destaque", ""))}</em></h1>
<p class="lead">{HERO_LEAD}</p>
<div class="hero__cta"><a class="btn btn--solid" href="#encontre">Encontre seu tratamento</a><a class="btn" href="{WA_MSG}" target="_blank" rel="noopener">{ICON_WA} Agendar pelo WhatsApp</a></div>
<div class="fpanel panel" data-fpanel aria-live="polite"><p class="label">Mapa facial</p><p class="fpanel__d">Toque nos pontos do rosto para ver os tratamentos de cada região.</p></div>
<p class="fhint">Mapa facial interativo · toque nos pontos do rosto</p>
<div class="facts"><div><b data-count="{len(TEAM)}">{len(TEAM)}</b><span>Especialistas</span></div><div><b data-count="{len(tech)}">{len(tech)}</b><span>Tecnologias</span></div><div><b data-count="{len(DIS)}">{len(DIS)}</b><span>Doenças catalogadas</span></div><div><b data-count="{N_IMG}">{NI}</b><span>Imagens no atlas</span></div></div>
</div></section>

<section class="sec" id="encontre"><div class="wrap">
<div class="sec__head"><p class="label">Explore</p><h2 class="split">O que você quer <em>cuidar</em> hoje?</h2><p>Escolha a região e o objetivo para ver os tratamentos relacionados que a clínica oferece. A indicação certa é definida em consulta, com avaliação do seu caso.</p></div>
<div class="finder rv" data-finder>
<div class="finder__l" data-finder-areas></div>
<div class="finder__r panel"><div class="finder__goals" data-finder-goals></div><div class="finder__out" data-finder-out><p class="lead">Ative o JavaScript para usar o explorador, ou <a class="arrow" href="tratamentos/index.html">veja todos os tratamentos</a>.</p></div>
<div class="finder__foot"><small><span class="label" data-finder-sum></span><br>Conteúdo informativo; não substitui avaliação médica.</small><a class="btn btn--solid" data-finder-cta href="{WA_MSG}" target="_blank" rel="noopener">{ICON_WA} Quero uma avaliação</a></div></div>
</div></div></section>

<section class="sec" id="tecnologia"><div class="wrap">
<div class="sec__head"><p class="label">Tecnologia</p><h2 class="split">O que há de mais <em>moderno</em> num só lugar.</h2><p>Passe o cursor ou toque em cada equipamento para conhecer o que ele faz. São {len(tech)} tecnologias disponíveis na clínica.</p></div>
<div class="tech rv" data-tech><div class="tech__list" data-tech-list></div><div class="tech__panel panel" data-tech-panel></div></div>
</div>
<div class="ticker" aria-hidden="true"><div>{tick}</div></div>
</section>

<section class="sec" id="clinica">
<div class="wrap"><div class="sec__head"><p class="label">A clínica · 19º andar</p><h2 class="split">Uma estrutura nunca vista no <em>Recife</em>.</h2><p>Arraste para percorrer os ambientes e clique em uma foto para entrar nela em 3D: recepção, lounge com vista para a cidade, consultórios e salas de laser e procedimentos.</p></div></div>
<div class="reel rv" data-reel><div class="reel__track">{reel}</div>
<div class="wrap"><div class="reel__ui"><button type="button" data-reel-go="-1" aria-label="Anterior">←</button><div class="reel__bar"><i></i></div><button type="button" data-reel-go="1" aria-label="Próximo">→</button></div>
<blockquote class="quote rv" style="margin-top:clamp(40px,6vw,80px)">“A Skin Prime é a concretização de um sonho, vai muito além de uma clínica humanizada. Aqui, cada mínimo detalhe foi pensado para oferecer o cuidado especial e personalizado que você merece.”<cite>Dr. Francisco Assis Filho · Dermatologista</cite></blockquote>
<p style="margin-top:28px"><a class="arrow" href="clinica.html">Visitar os ambientes</a></p></div></div>
</section>

<section class="sec" id="equipe"><div class="wrap">
<div class="sec__head"><p class="label">Equipe</p><h2 class="split">Conheça nossa equipe de <em>especialistas</em>.</h2><p>Dermatologistas, cirurgiões plásticos, fisioterapeutas, nutricionistas, nutrólogos, ginecologistas e esteticistas à sua disposição.</p></div>
<div class="team">{docs}</div>
</div></section>

<section class="sec" id="biblioteca"><div class="wrap">
<div class="sec__head"><p class="label">Biblioteca dermatológica</p><h2 class="split">Entenda a sua <em>pele</em>.</h2><p>Um acervo de referência mantido pela clínica: doenças dermatológicas descritas em detalhe e um atlas de imagens clínicas.</p></div>
<div class="lib rv">
<div><form class="search" action="doencas/index.html" method="get" role="search"><label class="sr" for="q-home">Buscar doença</label><input id="q-home" name="q" type="search" data-live placeholder="Digite: acne, melasma, psoríase…" autocomplete="off"><button type="submit">Buscar →</button><div class="live" data-live-out hidden></div></form>
<div class="az">{letters}</div></div>
<div class="pair"><a class="glow" href="doencas/index.html"><span class="label">Doenças dermatológicas</span><b><span class="num">{len(DIS)}</span> verbetes</b><span>Epidemiologia, quadro clínico, diagnóstico e tratamento, em ordem alfabética.</span></a>
<a class="glow" href="atlas/index.html"><span class="label">Atlas de imagens</span><b><span class="num">{NI}</span> imagens</b><span>Registros clínicos organizados por doença, para fins educativos.</span></a></div>
</div></div></section>

<section class="sec" style="padding-top:0;padding-bottom:clamp(48px,6vw,90px)"><div class="wrap mag">
<img class="rv" src="assets/img/brand/revista.webp" alt="Revista digital Skin Prime — A arte da dermatologia" loading="lazy" width="1400" height="800">
<div class="rv"><p class="label">Revista digital</p><h2 class="split">Clique e acesse nossa <em>revista</em>.</h2><p class="lead">A arte da dermatologia em páginas: tecnologias, tratamentos e a visão dos nossos especialistas.</p>
<a class="btn" href="{REVISTA}" target="_blank" rel="noopener">Abrir a revista (PDF)</a></div>
</div></section>

<section class="sec band--light" id="news"><div class="wrap">
<div class="sec__head"><p class="label">News</p><h2 class="split">Confira os últimos <em>posts</em>.</h2><p>Novidades, tecnologias e orientações dos nossos dermatologistas.</p></div>
<div class="cards">{''.join(card(p, '') for p in POSTS[:3])}</div>
<p style="margin-top:40px"><a class="arrow" href="tratamentos/index.html#news">Veja mais</a></p>
</div></section>

<section class="sec"><div class="wrap">
<div class="sec__head"><p class="label">Redes sociais</p><h2 class="split">Fique por <em>dentro</em>.</h2><p>Últimas publicações no Instagram e no YouTube, além da nossa playlist no Spotify.</p></div>
<div class="social">{''.join(f'<a href="{u}" target="_blank" rel="noopener"><span class="label">{n}</span><b>{E(h)}</b></a>' for n, h, u in SOCIAL)}</div>
</div></section>

<section class="sec" id="contato" style="padding-top:0"><div class="wrap">
<hr class="rule" style="margin-bottom:clamp(60px,9vw,120px)">
<div class="contact">
<div><p class="label" style="margin-bottom:22px">Contato</p><h2 class="split">Agende sua <em>consulta</em>.</h2>
<p class="lead" style="margin-block:22px 38px">E faça parte da melhor experiência em saúde, beleza e bem-estar do Recife.</p>
<form class="form" id="contato-form">
<div class="field"><label for="f-nome">Nome</label><input id="f-nome" name="nome" required autocomplete="name"></div>
<div class="field"><label for="f-tel">Telefone</label><input id="f-tel" name="telefone" type="tel" autocomplete="tel" inputmode="tel"></div>
<div class="field"><label for="f-email">E-mail</label><input id="f-email" name="email" type="email" autocomplete="email"></div>
<div class="field"><label for="f-int">Interesse</label><select id="f-int" name="interesse"><option value="">Selecione</option>{''.join(f'<option>{t}</option>' for _, t in CATS[:-1])}<option>Outro</option></select></div>
<div class="field"><label for="f-msg">Mensagem</label><textarea id="f-msg" name="mensagem" rows="3"></textarea></div>
<button class="btn btn--solid" type="submit">{ICON_WA} Enviar pelo WhatsApp</button>
<small>Ao enviar, abrimos o WhatsApp da clínica com a sua mensagem pronta.</small>
<p id="contato-ok" class="label" hidden>Mensagem preparada: conclua o envio na janela do WhatsApp.</p>
</form></div>
<div class="info">
<dl>
<div><dt>Telefone · WhatsApp</dt><dd class="big"><a href="{WA_MSG}" target="_blank" rel="noopener">{E(PHONE)}</a></dd></div>
<div><dt>Endereço</dt><dd>{ADDR_BR}</dd></div>
<div><dt>E-mail</dt><dd><a href="mailto:{EMAIL}">{E(EMAIL)}</a></dd></div>
<div><dt>Trabalhe conosco</dt><dd><a href="mailto:{EMAIL}?subject=Vagas%20de%20Emprego%20Skin%20Prime">Envie seu currículo</a></dd></div>
</dl>
<div class="coord"><span>{E(COORD)}</span><a class="arrow" style="border:0;padding:0" href="{MAPS}" target="_blank" rel="noopener">Abrir no mapa</a></div>
{MAP_HTML}
</div>
</div></div></section>'''
SHORT = {'testa': 'Testa', 'olhos': 'Olhos', 'macas': 'Maçãs', 'labios': 'Lábios', 'mandibula': 'Mandíbula', 'papada': 'Papada'}
home += '<div class="fmap" data-fmap>' + ''.join(f'<button class="fpt{" fpt--l" if side else ""}" type="button" data-face-pt="{k}" data-i="{i}" aria-pressed="false"><i></i><span><b class="lg">{E(t)}</b><b class="sh">{E(SHORT.get(k, t))}</b></span></button>' for i, (k, t, d2, keys, side) in enumerate(FMAP)) + '</div>'
write('index.html', page('index.html', '', 'Skin Prime: dermatologia, estética, nutrição e saúde no RioMar Trade Center, Recife. Conheça a clínica, os especialistas, os tratamentos e a biblioteca de doenças dermatológicas.', home))


# ---------------------------------------------------------------- clínica
tour = ''.join(f'<a href="{full}" data-tour="{k}" data-alt="{E(c)}"><img src="{th}" alt="{E(c)}" loading="lazy" width="900" height="600"><span class="cap3d">Ver em 3D</span><span class="cap">{E(c)}</span></a>' for k, c, full, th in CLINIC)
body = phead('', [('A Clínica', '')], 'RioMar Trade Center · Torre C · 19º andar · Sala 1905', 'Uma estrutura clínica nunca vista no <em>Recife</em>.',
             'A experiência e a tecnologia se encontram quando o assunto é dermatologia, estética, nutrição e saúde. Clique em uma foto para entrar no ambiente em 3D.') + f'''
<section class="sec"><div class="wrap">
<div class="tour">{tour}</div>
</div></section>
<section class="sec band--light"><div class="wrap">
<div class="sec__head"><p class="label">O cuidado pensado de forma global</p><h2>Quatro frentes, um só <em>lugar</em>.</h2><p>Conseguimos colocar num só lugar os recursos que podem solucionar as necessidades que sua pele precisa.</p></div>
<div class="pillars">
<div><p class="label">Dermatologia</p><h3>Clínica e cirúrgica</h3><p>Diagnóstico e tratamento de pele, cabelos e unhas, com dermatoscopia digital, biópsias e pequenas cirurgias.</p><a class="arrow" href="tratamentos/index.html#dermatologia-clínica">Ver</a></div>
<div><p class="label">Estética</p><h3>Face e corpo</h3><p>Lasers, ultrassom microfocado, radiofrequência, bioestimuladores, toxina botulínica e preenchimentos.</p><a class="arrow" href="tratamentos/index.html#face">Ver</a></div>
<div><p class="label">Nutrição</p><h3>Funcional e estética</h3><p>Estar saudável por dentro para se ver mais bonito por fora: a alimentação como parte do tratamento.</p><a class="arrow" href="tratamentos/index.html#nutrição">Ver</a></div>
<div><p class="label">Saúde</p><h3>Equipe multidisciplinar</h3><p>Dermatologistas, cirurgiões plásticos, fisioterapeutas, nutricionistas, nutrólogos, ginecologistas e esteticistas.</p><a class="arrow" href="especialistas.html">Ver</a></div>
</div></div></section>
<section class="sec"><div class="wrap contact">
<div><p class="label" style="margin-bottom:22px">Como chegar</p><h2>No coração do <em>Pina</em>.</h2></div>
<div class="info"><dl><div><dt>Endereço</dt><dd>{ADDR_BR}</dd></div>
<div><dt>Telefone · WhatsApp</dt><dd class="big"><a href="{WA_MSG}" target="_blank" rel="noopener">{E(PHONE)}</a></dd></div></dl>
<div class="coord"><span>{E(COORD)}</span><a class="arrow" style="border:0;padding:0" href="{MAPS}" target="_blank" rel="noopener">Abrir no mapa</a></div>{MAP_HTML}</div>
</div></section>''' + cta('')
write('clinica.html', page('clinica.html', 'A Clínica', 'Conheça os ambientes da Skin Prime no RioMar Trade Center, Recife: uma estrutura clínica para dermatologia, estética, nutrição e saúde.', body, 'clinica'))

# ---------------------------------------------------------------- especialistas
profs = ''.join(f'''<article class="profile" id="{t['k']}">
<div class="profile__id"><div class="profile__ph"><img src="{t['foto']}" alt="{E(t['n'])}" loading="lazy" width="640" height="640"></div>
<h2>{E(t['n'])}</h2><p class="reg"><b>{t['role']}</b>{t['reg']}</p>
<a class="arrow" style="justify-self:start" href="{t['link'][1]}" target="_blank" rel="noopener">{t['link'][0]}</a></div>
<div class="profile__txt"><h3>{E(t['h'])}</h3><div class="prose">{''.join(f'<p>{E(x)}</p>' for x in t['tx'])}</div></div>
</article>''' for t in TEAM)
body = phead('', [('Especialistas', '')], '', 'Quem cuida da sua <em>pele</em>.',
             'Uma equipe formada por renomados especialistas, porque o cuidado com você deve ser pensado de forma global.') + f'''
<section class="sec" style="padding-top:clamp(30px,5vw,60px)"><div class="wrap">
{profs}</div></section>''' + cta('')
write('especialistas.html', page('especialistas.html', 'Especialistas', 'Conheça os dermatologistas e a nutricionista da Skin Prime, no Recife.', body, 'especialistas'))

# ---------------------------------------------------------------- tratamentos
chips = '<button class="chip" type="button" data-cat="" aria-pressed="true">Todos</button>' + ''.join(
    f'<button class="chip" type="button" data-cat="{k}" aria-pressed="false">{t}</button>' for k, t in CATS)
body = phead('../', [('Tratamentos', '')], f'{len(POSTS)} publicações', 'Procedimentos e <em>tratamentos</em>.',
             'Conheça nossos procedimentos, tecnologias e as novidades da dermatologia.') + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap">
<div class="tools"><div class="chips" role="group" aria-label="Filtrar por categoria">{chips}</div>
<form class="search" role="search"><label class="sr" for="q-t">Buscar tratamento</label><input id="q-t" type="search" data-filter-q placeholder="Buscar tratamento…" autocomplete="off"></form></div>
<div class="cards" data-filter-list>{''.join(card(p, '../') for p in POSTS)}</div>
<p class="empty" hidden>Nenhuma publicação encontrada.</p>
</div></section>''' + cta('../')
write('tratamentos/index.html', page('tratamentos/index.html', 'Tratamentos', 'Procedimentos, tecnologias e tratamentos da Skin Prime: face, corpo, cabelo, cirurgia plástica, nutrição e dermatologia clínica.', body, 'tratamentos'))


def post_body(p):
    b = p['html']
    b = re.sub(r'(src|href)="/?assets/', r'\1="../assets/', b)
    b = b.replace('<img ', '<img loading="lazy" ')
    b = re.sub(r'<a href="(https?://[^"]*)"', r'<a href="\1" target="_blank" rel="noopener"', b)
    return b


for i, p in enumerate(POSTS):
    cats = ' · '.join(dict(CATS)[c] for c in p['cats'])
    mins = max(1, round(p['words'] / 200))
    cover = f'<div class="cover"><img src="../{p["cover"]}" alt="" width="1280" height="640"></div>' if p['cover_f'] else ''
    prev, nxt = POSTS[i - 1], POSTS[(i + 1) % len(POSTS)]
    rel = [q for q in POSTS if q is not p and set(q['cats']) & set(p['cats'])][:3] or [q for q in POSTS if q is not p][:3]
    body = phead('../', [('Tratamentos', 'tratamentos/index.html'), (p['title'].strip(), '')],
                 ' · '.join(x for x in [cats, fdate(p['date']), f'{mins} min de leitura'] if x), E(p['title'].strip())) + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap art">
<aside class="art__side"><a class="arrow" style="justify-self:start" href="index.html">Todos os tratamentos</a>
<p class="note">Quer saber se este tratamento é indicado para você? <a href="{WA_MSG}" target="_blank" rel="noopener" style="color:var(--aqua)">Fale com a clínica</a>.</p></aside>
<article>{cover}<div class="prose">{post_body(p)}</div></article>
</div></section>
<section class="sec band--light"><div class="wrap"><div class="sec__head"><p class="label">Continue lendo</p><h2>Veja <em>também</em>.</h2></div>
<div class="cards">{''.join(card(q, '../') for q in rel)}</div></div></section>
<nav class="pn" aria-label="Outras publicações"><a href="{prev['s']}.html"><span class="label label--mute">← Anterior</span><b>{E(prev['title'].strip())}</b></a><a href="{nxt['s']}.html"><span class="label label--mute">Próximo →</span><b>{E(nxt['title'].strip())}</b></a></nav>'''
    write(f"tratamentos/{p['s']}.html", page('tratamentos/x.html', p['title'].strip(), p['excerpt'], body, 'tratamentos',
                                              p['cover'] if p['cover_f'] else 'assets/img/clinic/vista.jpg'))


# bloco "Na Skin Prime" ao final de cada doença, a partir do cruzamento (build/cruzamento.py)
try:
    CRUZ = {c['doenca']: c for c in json.load(open(os.path.join(HERE, 'data', 'cruzamento.json'), encoding='utf-8'))}
except OSError:
    CRUZ = {}
# serviço do cruzamento -> (nome exibido, trecho do título da publicação que o descreve)
SERV = {
    'Toxina botulínica': ('Toxina botulínica', 'toxina botulinica a'),
    'Preenchimento com ácido hialurônico': ('Preenchimento com ácido hialurônico', 'acido hialuronico'),
    'Peelings químicos': ('Peelings químicos', 'peelings quimicos'),
    'Dermoabrasão / microdermoabrasão / peeling de cristal': ('Dermoabrasão e microdermoabrasão', 'dermoabrasao'),
    'Microagulhamento': ('Microagulhamento', 'microagulhamento'),
    'Laser de CO2 / laser fracionado': ('Laser de CO2', 'laser de co2'),
    'Laser ND-YAG / Q-Switched (Spectra XT)': ('Laser ND-YAG / Q-Switched', 'q-switched'),
    'Luz intensa pulsada': ('Luz intensa pulsada', 'luz intensa pulsada'),
    'Lasers (tipo a confirmar)': ('Lasers', 'lasers'),
    'Depilação a laser': ('Depilação a laser', 'depilacao a laser'),
    'Fototerapia': ('Fototerapia', 'fototerapia'),
    'LED': ('LED', 'led -'),
    'Eletrocauterização': ('Eletrocauterização', 'eletrocauterizacao'),
    'Curetagem': ('Curetagem dermatológica', 'curetagem'),
    'Pequenas cirurgias (avaliar porte)': ('Pequenas cirurgias', 'pequenas cirurgias'),
    'Tricologia e tratamentos capilares': ('Tricologia e tratamentos capilares', 'tricologia'),
    'Radiofrequência': ('Radiofrequência', 'radiofrequencia'),
    'Nutrição': ('Acompanhamento nutricional', 'nutricao funcional'),
    'Biópsia': ('Biópsia', 'biopsia'),
    'Dermatoscopia digital': ('Dermatoscopia digital', 'dermatoscopia'),
}
OK_LEVELS = ('Indicado no texto', 'Área de atuação', 'Citado como exame')
DISP = {v[0]: v[1] for v in SERV.values()}


def post_by(key):
    for p in POSTS:
        if key in norm(p['title']):
            return p
    return None


def solucao(d):
    """Bloco final da página da doença: o que a clínica oferece para aquela condição."""
    trat = [(n, post_by(DISP.get(n) or norm(n))) for n in d.get('trat', [])]
    diag = [(n, post_by(DISP.get(n) or norm(n))) for n in d.get('exam', [])]
    wa = WA + '?text=' + urllib.parse.quote(f"Olá, Skin Prime! Gostaria de agendar uma avaliação sobre {d['t']}.")

    def lista(items):
        out = ''
        for nome, p in items:
            if p:
                out += f'<a class="sol__i glow" href="../tratamentos/{p["s"]}.html"><b>{E(nome)}</b><span>Saber mais →</span></a>'
            else:
                out += f'<span class="sol__i"><b>{E(nome)}</b></span>'
        return out
    if trat or diag:
        intro = f'Entre os recursos citados para {E(d["t"])}, estes estão disponíveis na clínica:'
        blocos = ''
        if trat:
            blocos += f'<p class="label">Tratamentos</p><div class="sol__g">{lista(trat)}</div>'
        if diag:
            blocos += f'<p class="label">Diagnóstico</p><div class="sol__g">{lista(diag)}</div>'
    else:
        intro = f'O texto sobre {E(d["t"])} não cita procedimentos específicos entre os oferecidos pela clínica. A conduta é definida em consulta: nossa equipe avalia as manifestações na pele e orienta o tratamento ou o encaminhamento adequado.'
        blocos = ''
    return f'''<section class="sol panel" id="na-clinica">
<p class="label">Na Skin Prime</p>
<h2>Como podemos ajudar</h2>
<p class="sol__intro">{intro}</p>
{blocos}
<div class="sol__foot"><small>A escolha do tratamento depende de avaliação médica individual. Este conteúdo é informativo e não substitui a consulta.</small>
<a class="btn btn--solid" href="{wa}" target="_blank" rel="noopener">{ICON_WA} Agendar avaliação</a></div>
</section>'''

# ---------------------------------------------------------------- doenças
az = ''.join((f'<a href="#letra-{L}">{L}</a>' if L in BY_LETTER else f'<span>{L}</span>') for L in 'ABCDEFGHIJKLMNOPQRSTUVXZ')
groups = ''.join(f'''<section class="letter" id="letra-{L}" data-group><b aria-hidden="true">{L}</b><ul>{''.join(
    f'<li data-k="{E(norm(d["t"]))}"><a href="{d["s"]}.html"><span>{E(d["t"])}</span>{f"<small>{len(d['imgs'])} img</small>" if d["imgs"] else ""}</a></li>' for d in ds)}</ul></section>'''
                 for L, ds in BY_LETTER.items())
body = phead('../', [('Doenças Dermatológicas', '')], f'{len(DIS)} verbetes · ordem alfabética', 'Doenças <em>dermatológicas</em>.',
             'Um guia de referência sobre as condições que afetam a pele, os cabelos e as unhas.') + f'''
<div class="azbar"><div class="wrap"><nav class="az" aria-label="Índice alfabético">{az}</nav></div></div>
<section class="sec" style="padding-top:clamp(30px,4vw,50px)"><div class="wrap">
<div class="tools"><form class="search" role="search" style="max-width:560px"><label class="sr" for="q-d">Buscar doença</label><input id="q-d" type="search" data-filter-q placeholder="Buscar doença…" autocomplete="off"></form>
<a class="arrow" href="../atlas/index.html">Atlas de imagens</a></div>
<div data-filter-list>{groups}</div>
<p class="empty" hidden>Nenhuma doença encontrada com esse termo.</p>
<p class="note" style="margin-top:40px">Conteúdo de caráter informativo e educativo. Não substitui a consulta com um médico dermatologista.</p>
</div></section>''' + cta('../')
write('doencas/index.html', page('doencas/index.html', 'Doenças Dermatológicas', f'Guia com {len(DIS)} doenças dermatológicas: epidemiologia, quadro clínico, diagnóstico e tratamento.', body, 'doencas'))

for i, d in enumerate(DIS):
    prev, nxt = DIS[i - 1], DIS[(i + 1) % len(DIS)]
    toc = ''.join(f'<li><a href="#{h}">{E(t)}</a></li>' for h, t in d['toc'])
    if d['imgs']:
        toc += '<li><a href="#imagens">Imagens</a></li>'
    toc += '<li><a href="#na-clinica">Na Skin Prime</a></li>'
    gal = ''
    if d['imgs']:
        gal = f'''<h2 id="imagens" style="font-size:clamp(1.6rem,2.6vw,2.1rem);margin-top:2.2em;padding-top:.9em;border-top:1px solid var(--line);scroll-margin-top:110px">Atlas de imagens <span class="label label--mute" style="margin-left:10px">{len(d['imgs'])}</span></h2>
<p style="margin-top:.6em"><a class="arrow" href="../atlas/{d['s']}.html">Abrir no Atlas de Imagens</a></p>
<div class="gal">{''.join(f'<a href="../{n}" data-lb="atlas" data-alt="{E(d["t"])}"><img src="../{n}" alt="{E(d["t"])} — imagem clínica {k}" loading="lazy" width="200" height="200"></a>' for k, n in enumerate(d['imgs'], 1))}</div>'''
    bib = f'<h3 style="margin-top:2.4em;font-size:1.2rem">Bibliografia</h3><p class="biblio" style="margin-top:.8em">{E(d["bib"])}</p>' if d['bib'] else ''
    if d['imgs']:
        xl = f'<div class="xlinks"><a class="btn" href="../atlas/{d["s"]}.html">{ICON_IMG} Ver no Atlas de Imagens <span class="xlinks__n">{len(d["imgs"])}</span></a></div>'
        side_x = f'<a class="xside" href="../atlas/{d["s"]}.html">{ICON_IMG}<span>Atlas de imagens<small>{len(d["imgs"])} {"imagem" if len(d["imgs"]) == 1 else "imagens"} desta doença</small></span></a>'
    else:
        xl = '<div class="xlinks"><span class="xlinks__none">Esta doença ainda não tem imagens no atlas.</span></div>'
        side_x = ''
    body = phead('../', [('Doenças Dermatológicas', 'doencas/index.html'), (d['t'], '')],
                 ' · '.join(x for x in [f'Atualizado em {d["upd"]}' if d['upd'] else ''] if x), E(d['t']), extra=xl) + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap art">
<aside class="art__side"><a class="arrow" style="justify-self:start" href="index.html">Voltar ao índice</a>{side_x}{f'<ol>{toc}</ol>' if toc else ''}
<p class="note">Conteúdo informativo. Não substitui a consulta com um dermatologista. <a href="{WA_MSG}" target="_blank" rel="noopener" style="color:var(--aqua)">Agende sua avaliação</a>.</p></aside>
<article><div class="prose">{d['body']}</div>{gal}{bib}{solucao(d)}</article>
</div></section>
<nav class="pn" aria-label="Outras doenças"><a href="{prev['s']}.html"><span class="label label--mute">← Anterior</span><b>{E(prev['t'])}</b></a><a href="{nxt['s']}.html"><span class="label label--mute">Próxima →</span><b>{E(nxt['t'])}</b></a></nav>'''
    write(f"doencas/{d['s']}.html", page('doencas/x.html', d['t'], d['lead'], body, 'doencas'))

# ---------------------------------------------------------------- atlas: uma página por doença
WI = [d for d in DIS if d['imgs']]
for i, d in enumerate(WI):
    prev, nxt = WI[i - 1], WI[(i + 1) % len(WI)]
    n = len(d['imgs'])
    back = f'<div class="xlinks"><a class="btn btn--solid" href="../doencas/{d["s"]}.html">{ICON_TXT} Ler sobre {E(d["t"])}</a><a class="btn" href="index.html">Todas as doenças do atlas</a></div>'
    gal = ''.join(f'<a href="../{m}" data-lb="atlas" data-alt="{E(d["t"])} · imagem {k} de {n}"><img src="../{m}" alt="{E(d["t"])} — imagem clínica {k}" loading="lazy" width="300" height="300"></a>' for k, m in enumerate(d['imgs'], 1))
    body = phead('../', [('Atlas de Imagens', 'atlas/index.html'), (d['t'], '')], f'{n} {"imagem clínica" if n == 1 else "imagens clínicas"} · toque para ampliar', E(d['t']), extra=back) + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap">
<div class="gal gal--atlas">{gal}</div>
<div class="xback panel"><div><p class="label">Texto da doença</p><p>Epidemiologia, quadro clínico, diagnóstico e tratamento de {E(d["t"])}, e como a Skin Prime pode ajudar.</p></div><a class="btn btn--solid" href="../doencas/{d["s"]}.html">{ICON_TXT} Voltar ao texto da doença</a></div>
<p class="note" style="margin-top:28px">Imagens clínicas de caráter educativo. Não substituem a avaliação de um dermatologista.</p>
</div></section>
<nav class="pn" aria-label="Outras doenças do atlas"><a href="{prev['s']}.html"><span class="label label--mute">← Anterior</span><b>{E(prev['t'])}</b></a><a href="{nxt['s']}.html"><span class="label label--mute">Próxima →</span><b>{E(nxt['t'])}</b></a></nav>'''
    write(f"atlas/{d['s']}.html", page('atlas/x.html', f'{d["t"]} · Atlas de Imagens', f'Atlas de imagens clínicas de {d["t"]}: {n} imagens.', body, 'atlas'))

# ---------------------------------------------------------------- atlas
WI = [d for d in DIS if d['imgs']]
grid = ''.join(f'<a href="{d["s"]}.html" data-k="{E(norm(d["t"]))}"><div class="ph"><img src="../{d["imgs"][0]}" alt="" loading="lazy" width="200" height="200"></div><b>{E(d["t"])}</b><small>{len(d["imgs"])} {"imagem" if len(d["imgs"])==1 else "imagens"}</small></a>' for d in WI)
body = phead('../', [('Atlas de Imagens', '')], f'{NI} imagens · {len(WI)} doenças', 'Atlas de <em>imagens</em>.',
             'Registros clínicos organizados por doença, em ordem alfabética. Imagens reais, de caráter educativo.') + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap">
<div class="tools"><form class="search" role="search" style="max-width:560px"><label class="sr" for="q-a">Buscar no atlas</label><input id="q-a" type="search" data-filter-q placeholder="Buscar no atlas…" autocomplete="off"></form>
<a class="arrow" href="../doencas/index.html">Ler sobre as doenças</a></div>
<div class="atlas" data-filter-list>{grid}</div>
<p class="empty" hidden>Nenhum resultado no atlas.</p>
</div></section>''' + cta('../')
write('atlas/index.html', page('atlas/index.html', 'Atlas de Imagens', f'Atlas dermatológico da Skin Prime com {N_IMG} imagens clínicas organizadas por doença.', body, 'atlas'))

# ---------------------------------------------------------------- cores do painel
def _hex(v, d):
    return v if isinstance(v, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', v.strip()) else d


_c = SITE.get('cores', {})
_t = dict(ink=_hex(_c.get('fundo'), '#f7f7f7'), bone=_hex(_c.get('texto'), '#1d2b2d'), mute=_hex(_c.get('texto_secundario'), '#4f6468'),
          rose=_hex(_c.get('botoes'), '#996059'), aqua=_hex(_c.get('destaque'), '#4a7079'), ftr=_hex(_c.get('rodape'), '#1d2b2d'))
write('assets/css/theme.css', '/* gerado a partir das cores do painel (content/config/site.json) */\n'
      f":root{{--ink:{_t['ink']};--bone:{_t['bone']};--mute:{_t['mute']};--rose:{_t['rose']};--aqua:{_t['aqua']};"
      f"--grad:linear-gradient(100deg,{_t['aqua']},{_t['rose']})}}\n"
      f"body{{background:{_t['ink']}}}\n.ftr{{--ink:{_t['ftr']}}}\n")

# ---------------------------------------------------------------- extras
body = phead('', [('Página não encontrada', '')], 'Erro 404', 'Esta página saiu do <em>foco</em>.', 'O endereço pode ter mudado. Volte ao início ou fale com a clínica.') + '<section class="sec"><div class="wrap"><a class="btn" href="/">Voltar ao início</a></div></section>'
write('404.html', page('404.html', 'Página não encontrada', 'Página não encontrada.', body).replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/'))
write('assets/img/brand/favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#1d2b2d"/><circle cx="32" cy="32" r="24" fill="none" stroke="#a4d2db" stroke-width="1.2"/><text x="32" y="43" text-anchor="middle" font-family="Didot,Bodoni MT,Georgia,serif" font-size="32" fill="#cc8d85">S</text></svg>')
urls = ['', 'clinica.html', 'especialistas.html', 'tratamentos/', 'doencas/', 'atlas/'] + [f"tratamentos/{p['s']}.html" for p in POSTS] + [f"doencas/{d['s']}.html" for d in DIS] + [f"atlas/{d['s']}.html" for d in DIS if d['imgs']]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://www.skinprime.com.br/{u}</loc></url>\n' for u in urls) + '</urlset>\n')
write('robots.txt', 'User-agent: *\nAllow: /\nSitemap: https://www.skinprime.com.br/sitemap.xml\n')
print('ok:', len(urls), 'páginas')
