#!/usr/bin/env python3
"""Gera o site estático da Skin Prime em ../site a partir de build/data/*.json.
Uso:  python3 build/build.py   (executar na raiz do projeto)"""
import json, re, os, html, unicodedata, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'site')
IMG = os.path.join(OUT, 'assets', 'img')
E = html.escape
WA = 'https://wa.me/558130364040'
WA_MSG = WA + '?text=' + 'Ol%C3%A1%2C%20Skin%20Prime!%20Gostaria%20de%20agendar%20uma%20consulta.'
MAPS = 'https://www.google.com/maps/search/?api=1&query=RioMar+Trade+Center+Torre+C+Av.+Rep%C3%BAblica+do+L%C3%ADbano+251+Pina+Recife'
REVISTA = 'https://www.skinprime.com.br/_files/ugd/96b8be_44971ebf18c04e0eb636ec94da8b884f.pdf'
SOCIAL = [('Instagram', '@skinprime_', 'https://www.instagram.com/skinprime_/'),
          ('Facebook', 'skinprimeoficial', 'https://www.facebook.com/skinprimeoficial'),
          ('YouTube', '@skinprime3693', 'https://www.youtube.com/@skinprime3693'),
          ('Spotify', 'Playlist Skin Prime', 'https://open.spotify.com/playlist/4Vmj4nMBTfzhT5obi0249Q')]
CATS = [('face', 'Face'), ('corpo', 'Corpo'), ('cabelo', 'Cabelo'), ('procedimentos', 'Procedimentos'),
        ('cirurgia-plástica', 'Cirurgia Plástica'), ('nutrição', 'Nutrição'),
        ('dermatologia-clínica', 'Dermatologia Clínica'), ('news', 'News')]
MESES = 'jan fev mar abr mai jun jul ago set out nov dez'.split()
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
    shape = {'': 'logo', 'clinica': 'skin', 'especialistas': 'helix', 'tratamentos': 'helix', 'doencas': 'cell', 'atlas': 'ring'}.get(cur, 'ring')
    body = body.replace('<section class="phead">', f'<section class="phead" data-fx="{shape}" data-fx-x=".55" data-fx-y=".1" data-fx-s=".8" data-fx-f=".75" data-fx-my=".5">')
    full = f'{title} · Skin Prime' if title else 'Skin Prime · A arte da dermatologia no Recife'
    return f'''<!doctype html>
<html lang="pt-BR" data-root="{R}">
<head>
<script>(function(){{var c="js";try{{if(sessionStorage.getItem("sp-boot"))c+=" skip-boot"}}catch(e){{}}document.documentElement.className=c}})()</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(full)}</title>
<meta name="description" content="{E(desc[:300])}">
<meta name="theme-color" content="#03080a">
<meta property="og:title" content="{E(full)}">
<meta property="og:description" content="{E(desc[:300])}">
<meta property="og:image" content="https://www.skinprime.com.br/{og}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="{R}assets/img/brand/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{R}assets/css/site.css">
</head>
<body>
<canvas id="fx" data-shape="{shape}" aria-hidden="true"></canvas>
<div class="boot" aria-hidden="true"><div class="boot__in"><img src="{R}assets/img/brand/logo-bone.png" alt="" width="500" height="234"><div class="boot__bar"><i></i></div><p class="label"><span data-boot-n>0</span>% · calibrando sensores</p></div></div>
<div class="prog" aria-hidden="true"><i></i></div><div class="veil" aria-hidden="true"></div>
<header class="hdr"><div class="wrap hdr__in">
<a class="hdr__logo" href="{R}index.html" aria-label="Skin Prime — início"><img src="{R}assets/img/brand/logo-bone.png" alt="Skin Prime" width="500" height="234"></a>
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
<div><h4>Endereço</h4><p>RioMar Trade Center<br>Av. República do Líbano, 251<br>Torre C · 19º andar · Sala 1905<br>Pina, Recife – PE · 51110-160</p></div>
<div><h4>Contato</h4><ul><li><a href="{WA_MSG}" target="_blank" rel="noopener">(81) 3036-4040 · WhatsApp</a></li><li><a href="mailto:contato@skinprime.com.br">contato@skinprime.com.br</a></li>{soc}</ul></div>
</div>
<div class="ftr__bot"><span>© {datetime.date.today().year} Clinical Center Rio Mar · Skin Prime · CNPJ 37.572.208/0001-95</span><span>8°05′S · 34°53′W · 19º andar</span></div>
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


def phead(R, crumbs, label, h1, lead=''):
    c = f'<a href="{R}index.html">Início</a>' + ''.join(
        (f'<span><a href="{R}{h}">{E(t)}</a></span>' if h else f'<span>{E(t)}</span>') for t, h in crumbs)
    return f'''<section class="phead"><div class="wrap">
<nav class="crumb" aria-label="Você está em">{c}</nav>
<h1 class="split">{h1}</h1>
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
POSTS = json.load(open(os.path.join(HERE, 'data', 'posts.json'), encoding='utf-8'))
RAW = json.load(open(os.path.join(HERE, 'data', 'doencas.json'), encoding='utf-8'))
seen = set()
for p in POSTS:
    s = slug(p['title']) or slug(p['slug'])
    while s in seen:
        s += '-2'
    seen.add(s)
    p['s'] = s
    p['cover_f'] = imgname(p['cover']) if p['cover'] and has(f"posts/{imgname(p['cover'])}.jpg") else ''
    p['video'] = p['vids'][0] if p.get('vids') else ''
    text = re.sub(r'<[^>]+>', ' ', p['body'])
    p['excerpt'] = (p['desc'] or re.sub(r'\s+', ' ', text)).strip()[:220]
    p['words'] = len(text.split())

KEYS = ['epidemiologia', 'etiopatogenia', 'etiologia', 'patogenia', 'patogênese', 'fisiopatologia', 'fisiopatogenia',
        'clínica', 'manifestações clínicas', 'quadro clínico', 'aspectos clínicos', 'diagnóstico diferencial',
        'diagnóstico', 'diagnose', 'tratamento', 'terapêutica', 'prognóstico', 'histopatologia', 'histologia',
        'classificação', 'complicações', 'prevenção', 'profilaxia', 'evolução', 'exames', 'laboratório',
        'introdução', 'definição', 'sinonímia', 'conceito', 'transmissão', 'formas clínicas', 'causas', 'sintomas']
HEAD = re.compile(r'^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.:\n]{2,48})[.:]\s*(?=\S|$)')
DIS = []
seen = set()
for r in RAW:
    t = re.sub(r'\s+', ' ', r['title']).strip()
    s = slug(t)
    while s in seen:
        s += '-2'
    seen.add(s)
    imgs = []
    for im in r.get('imagens') or []:
        m = re.match(r'wix:image://v1/([^/]+)/', im.get('src', ''))
        if m and has(f'atlas/{imgname(m.group(1))}.jpg'):
            n = imgname(m.group(1))
            if n not in imgs:
                imgs.append(n)
    paras, toc = [], []
    for raw in re.split(r'\n\s*\n|\n', r['texto']):
        raw = raw.strip()
        if not raw:
            continue
        m = HEAD.match(raw)
        if m and len(m.group(1).split()) <= 5 and any(m.group(1).lower().startswith(k) for k in KEYS):
            hid = slug(m.group(1))
            while hid in [x[0] for x in toc]:
                hid += '-2'
            toc.append((hid, m.group(1)))
            paras.append(f'<h2 id="{hid}">{E(m.group(1))}</h2>')
            raw = raw[m.end():].strip()
            if not raw:
                continue
        paras.append(f'<p>{E(raw)}</p>')
    bib = (r.get('bibliografia') or '').strip()
    DIS.append(dict(t=t, s=s, imgs=imgs, body='\n'.join(paras), toc=toc, bib=bib, upd=(r.get('atualizao') or '').strip(),
                    lead=re.sub(r'\s+', ' ', r['texto']).strip()[:240], letter=norm(t)[0].upper()))
DIS.sort(key=lambda d: norm(d['t']))
N_IMG = sum(len(d['imgs']) for d in DIS)
NI = f'{N_IMG:,}'.replace(',', '.')
BY_LETTER = collections.OrderedDict()
for d in DIS:
    BY_LETTER.setdefault(d['letter'], []).append(d)
print(f'{len(POSTS)} posts · {len(DIS)} doenças · {N_IMG} imagens de atlas')


def card(p, R):
    if p['cover_f']:
        im = f'<div class="card__img{" card__img--video" if p["video"] else ""}"><img src="{R}assets/img/posts/{p["cover_f"]}-m.jpg" alt="" loading="lazy" width="640" height="480"></div>'
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
TEAM = [
    dict(k='emmanuel', n='Dr. Emmanuel França', role='Dermatologista', reg='CRM 5999 · RQE 636',
         h='A pele revela seu Eu', link=('Site pessoal', 'https://www.emmanuelfranca.com.br/'),
         short='Sentir-se bem, física e mentalmente, é fantástico. A pele reflete isto.',
         tx=['Sentir-se bem, física e mentalmente é fantástico. A pele reflete isto. E revela seu Eu. Tudo que a dermatologia faz é para que você alcance essa plenitude.',
             'Tenho acompanhado a dermatologia em todos os seus aspectos e conseguimos colocar num só lugar os recursos que podem solucionar as necessidades que sua pele precisa.',
             'Saber que estamos oferecendo o melhor para nosso paciente é o grande objetivo da Skin Prime.']),
    dict(k='francisco', n='Dr. Francisco Assis Filho', role='Dermatologista', reg='CRM 18608 · RQE 4565',
         h='Afinal, a beleza é igual pra todo mundo?', link=('Site pessoal', 'https://www.franciscoassisdermato.com.br/'),
         short='A matemática por trás dos tratamentos que realçam a beleza de cada um.',
         tx=['Durante toda minha formação médica, sempre me perguntei: por que nos preocupamos tanto com a beleza? Confesso que até hoje me encanto com a matemática por trás dos tratamentos que nos possibilitam encontrar a simetria ideal, promover a jovialidade e ser assertivo nas proporções, que realçam ainda mais a beleza de cada um.',
             'Concordo que a beleza é subjetiva, mas quem nunca pensou em ter uma pele nutrida, saudável e jovem? Valorizo a beleza natural, mas também sou a favor de ressaltar o que há de melhor em cada pessoa. Por isso, tenho me empenhado nestes últimos anos em aplicar associações de tratamentos, com o que há de mais moderno em tecnologias e formulações.',
             'A SkinPrime é a concretização de um sonho, vai muito além de uma clínica humanizada. Aqui, cada mínimo detalhe foi pensado para oferecer o cuidado especial e personalizado que você merece. Queremos que não lhe falte motivos pra enxergar a beleza da vida. Porque você e sua pele merecem mais!',
             'Reunimos uma equipe formada por renomados dermatologistas, cirurgiões plásticos, fisioterapeutas, nutricionistas, nutrólogos, ginecologistas e esteticistas, que estão à sua disposição. Entendemos que o cuidado com você deve ser pensado de forma global, afinal, diversos fatores interferem na saúde da sua pele.']),
    dict(k='daniela', n='Daniela Saldanha', role='Nutricionista', reg='CRN 29209/P',
         h='A nutrição com um olhar mais amplo.', link=('Instagram', 'https://www.instagram.com/nutridanielasaldanhafranca/'),
         short='Estar saudável por dentro para se ver mais bonito por fora.',
         tx=['Se engana quem acha que a saúde da pele não tem a ver com o que comemos. Acredite em mim, manter cabelos volumosos, bonitos, unhas fortes, além de uma pele bem cuidada e hidratada, também depende da qualidade da nossa alimentação. Precisamos pensar na nutrição com um olhar mais amplo.',
             'Estou aqui pra te ajudar a manter uma rotina mais saudável. Tenho certeza que novos hábitos vão fazer você se sentir bem melhor. Afinal, quem não gosta de dar um UP na aparência?',
             'Na minha especialização em nutrição clínica funcional, mergulhei na análise de dietas que interferem na estética, através da reposição de nutrientes, que vão influenciar os quesitos da beleza. Estar saudável por dentro para se ver mais bonito por fora tem tudo a ver com o que você come. Pense nisso!',
             'É um prazer te receber na Skin Prime.']),
    dict(k='yana', n='Dra. Yana Carvalho', role='Dermatologista', reg='CRM 26131 · RQE 11047',
         h='Beleza e cuidado!', link=('Instagram', 'https://www.instagram.com/yanacarvalho/'),
         short='O futuro da sua pele ainda pode ser desenhado.',
         tx=['“Sua pele revela muito sobre você. Para um olhar atento, ela pode dizer o que se passa no seu corpo e na sua mente. Seu passado e o seu presente estão escritos em suas linhas. Já o futuro, ainda pode ser desenhado. E minha paixão como dermatologista é entender essas nuances e fazer parte dessa história.”',
             'Dra. Yana Carvalho cursou a graduação em Medicina na Universidade Federal de Pernambuco (UFPE) e realizou sua Residência médica em Dermatologia na Universidade de Pernambuco (UPE). Atualmente participa do mestrado em Ciências da Saúde na UPE e é professora de Dermatologia da Faculdade de Medicina de Olinda e preceptora na Universidade de Pernambuco.',
             'É membra da Sociedade Brasileira de Dermatologia e atua nos cuidados com Pele, Cabelos e Unhas.']),
    dict(k='andre', n='Dr. André Rosa', role='Dermatologista', reg='CRM 13132 · RQE 7642',
         h='A especialidade que trata e cuida do maior órgão do corpo: a pele!', link=('Instagram', 'https://www.instagram.com/andrerosadermato/'),
         short='Saúde, beleza e bem-estar com o rigor que a ciência pede.',
         tx=['A dermatologia tornou-se minha paixão pela possibilidade de aliar saúde, beleza e bem-estar, com todo o rigor que a ciência pede e o acolhimento que nossos pacientes precisam.',
             'Aqui exercemos nossa especialidade com compromisso, ética e amor.']),
    dict(k='aleksana', n='Dra. Aleksana Viana', role='Dermatologista', reg='CRM 16907',
         h='A Arte da Dermatologia', link=('Instagram', 'https://www.instagram.com/aleksanavianadermato/'),
         short='Rejuvenescimento elegante e seguro, com muita naturalidade.',
         tx=['Sou médica dermatologista graduada pela UFPE, membro da SBD e tenho 15 anos de carreira. Entre os incontáveis cursos e congressos nacionais e internacionais, o aprendizado que mais valorizo é a boa relação médico-paciente, em que alinhamos as expectativas para um melhor resultado final.',
             'O que mais gosto do meu trabalho é ver a satisfação em cada rosto tratado por mim. É sobre devolver autoestima, autocuidado, amor próprio. Entrego resultados estéticos com muita naturalidade, buscando um rejuvenescimento elegante e seguro, realçando a própria beleza de cada paciente.',
             'A dermatologia é a arte de cuidar da pele, cabelos e unhas. Manter a pele jovem, bonita e, principalmente, saudável, além de devolver a autoestima dos pacientes, são a minha missão.']),
]
CLINIC = [('vista', 'Vista do 19º andar'), ('lounge', 'Lounge'), ('recepcao', 'Recepção'), ('espera', 'Sala de espera'),
          ('cafe', 'Café'), ('consultorio', 'Consultório'), ('sala-laser', 'Sala de laser'),
          ('sala-procedimentos', 'Sala de procedimentos'), ('capilar', 'Terapia capilar'), ('detalhe', 'Detalhes')]
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
data = {'posts': [[p['title'].strip(), p['s'], ' '.join(p['cats']), p['excerpt'][:170], p['cover_f']] for p in POSTS],
        'dis': [[d['t'], d['s'], len(d['imgs'])] for d in DIS], 'quiz': quiz, 'tech': tech}
write('assets/js/data.js', 'window.SP=' + json.dumps(data, separators=(',', ':')) + ';')
print('quiz:', [(q['t'], [(g['t'], len(g['p'])) for g in q['g']]) for q in quiz], '· tech:', len(tech))

# ---------------------------------------------------------------- home
R = ''
docs = ''.join(f'''<article class="doc glow rv" data-tilt><div class="doc__ph"><img src="assets/img/team/{t['k']}.jpg" alt="{E(t['n'])}" loading="lazy" width="640" height="640"></div>
<div><h3>{E(t['n'])}</h3></div><p class="reg"><b>{t['role']}</b>{t['reg']}</p><p>{E(t['short'])}</p>
<a class="arrow" href="especialistas.html#{t['k']}">Conhecer</a></article>''' for t in TEAM)
letters = ''.join((f'<a href="doencas/index.html#letra-{L}">{L}</a>' if L in BY_LETTER else f'<span>{L}</span>') for L in 'ABCDEFGHIJKLMNOPQRSTUVXZ')
tick = ''.join(f'<span>{E(t)}</span>' for t in TECH) * 2
reel = ''.join(f'<a href="assets/img/clinic/{k}.jpg" data-tour="{k}" data-alt="{E(c)}" draggable="false"><img src="assets/img/clinic/{k}-m.jpg" alt="{E(c)}" loading="lazy" width="900" height="600" draggable="false"><span class="cap3d">Ver em 3D</span><span class="cap">{i:02d} · {E(c)}</span></a>' for i, (k, c) in enumerate(CLINIC, 1))
home = f'''<section class="hero" data-fx="logo" data-fx-x=".46" data-fx-y=".2" data-fx-s=".82" data-fx-f="1" data-fx-my=".46">
<div class="hud" aria-hidden="true"><span>Sistema <b>ativo</b></span><span>Partículas <b data-hud-n>15.000</b></span><span>Forma <b data-hud-shape>Marca</b></span><span>Ponteiro <b data-hud-p>0000 · 0000</b></span></div>
<span class="corner corner--a" aria-hidden="true"></span><span class="corner corner--b" aria-hidden="true"></span>
<div class="wrap hero__in">
<p class="label">Recife · RioMar Trade Center · 19º andar</p>
<h1 class="split">A arte da <em>dermatologia</em></h1>
<p class="lead">A experiência e a tecnologia se encontram para trazer uma estrutura clínica nunca vista no Recife quando o assunto é <strong>dermatologia, estética, nutrição e saúde</strong>.</p>
<div class="hero__cta"><a class="btn btn--solid" href="#encontre">Encontre seu tratamento</a><a class="btn" href="{WA_MSG}" target="_blank" rel="noopener">{ICON_WA} Agendar pelo WhatsApp</a></div>
<div class="modes" role="group" aria-label="Mudar a forma das partículas"><span>Interaja</span>
<button class="chip" type="button" data-go="logo" aria-pressed="true">Marca</button><button class="chip" type="button" data-go="helix" aria-pressed="false">DNA</button><button class="chip" type="button" data-go="skin" aria-pressed="false">Camadas da pele</button><button class="chip" type="button" data-go="face" aria-pressed="false">Rosto em transformação</button><button class="chip" type="button" data-go="toxin" aria-pressed="false">Toxina botulínica</button><button class="chip" type="button" data-go="cell" aria-pressed="false">Célula</button></div>
<div class="facts"><div><b data-count="{len(TEAM)}">{len(TEAM)}</b><span>Especialistas</span></div><div><b data-count="{len(tech)}">{len(tech)}</b><span>Tecnologias</span></div><div><b data-count="{len(DIS)}">{len(DIS)}</b><span>Doenças catalogadas</span></div><div><b data-count="{N_IMG}">{NI}</b><span>Imagens no atlas</span></div></div>
</div></section>

<section class="sec" id="encontre" data-fx="face" data-fx-x=".7" data-fx-y=".3" data-fx-s=".8" data-fx-f=".4"><div class="wrap">
<div class="sec__head"><p class="label">Explore</p><h2 class="split">O que você quer <em>cuidar</em> hoje?</h2><p>Escolha a região e o objetivo para ver os tratamentos relacionados que a clínica oferece. A indicação certa é definida em consulta, com avaliação do seu caso.</p></div>
<div class="finder rv" data-finder>
<div class="finder__l" data-finder-areas></div>
<div class="finder__r panel"><div class="finder__goals" data-finder-goals></div><div class="finder__out" data-finder-out><p class="lead">Ative o JavaScript para usar o explorador, ou <a class="arrow" href="tratamentos/index.html">veja todos os tratamentos</a>.</p></div>
<div class="finder__foot"><small><span class="label" data-finder-sum></span><br>Conteúdo informativo; não substitui avaliação médica.</small><a class="btn btn--solid" data-finder-cta href="{WA_MSG}" target="_blank" rel="noopener">{ICON_WA} Quero uma avaliação</a></div></div>
</div></div></section>

<section class="sec" id="tecnologia" data-fx="toxin" data-fx-x=".72" data-fx-y=".35" data-fx-s=".8" data-fx-f=".45"><div class="wrap">
<div class="sec__head"><p class="label">Tecnologia</p><h2 class="split">O que há de mais <em>moderno</em> num só lugar.</h2><p>Passe o cursor ou toque em cada equipamento para conhecer o que ele faz. São {len(tech)} tecnologias disponíveis na clínica.</p></div>
<div class="tech rv" data-tech><div class="tech__list" data-tech-list></div><div class="tech__panel panel" data-tech-panel></div></div>
</div>
<div class="ticker" aria-hidden="true"><div>{tick}</div></div>
</section>

<section class="sec" id="clinica" data-fx="skin" data-fx-x=".5" data-fx-y=".3" data-fx-s="1" data-fx-f=".3">
<div class="wrap"><div class="sec__head"><p class="label">A clínica · 19º andar</p><h2 class="split">Uma estrutura nunca vista no <em>Recife</em>.</h2><p>Arraste para percorrer os ambientes e clique em uma foto para entrar nela em 3D: recepção, lounge com vista para a cidade, consultórios e salas de laser e procedimentos.</p></div></div>
<div class="reel rv" data-reel><div class="reel__track">{reel}</div>
<div class="wrap"><div class="reel__ui"><button type="button" data-reel-go="-1" aria-label="Anterior">←</button><div class="reel__bar"><i></i></div><button type="button" data-reel-go="1" aria-label="Próximo">→</button></div>
<blockquote class="quote rv" style="margin-top:clamp(40px,6vw,80px)">“A Skin Prime é a concretização de um sonho, vai muito além de uma clínica humanizada. Aqui, cada mínimo detalhe foi pensado para oferecer o cuidado especial e personalizado que você merece.”<cite>Dr. Francisco Assis Filho · Dermatologista</cite></blockquote>
<p style="margin-top:28px"><a class="arrow" href="clinica.html">Visitar os ambientes</a></p></div></div>
</section>

<section class="sec" id="equipe" data-fx="helix" data-fx-x=".72" data-fx-y=".1" data-fx-s=".9" data-fx-f=".45"><div class="wrap">
<div class="sec__head"><p class="label">Equipe</p><h2 class="split">Conheça nossa equipe de <em>especialistas</em>.</h2><p>Dermatologistas, cirurgiões plásticos, fisioterapeutas, nutricionistas, nutrólogos, ginecologistas e esteticistas à sua disposição.</p></div>
<div class="team">{docs}</div>
</div></section>

<section class="sec" id="biblioteca" data-fx="cell" data-fx-x=".6" data-fx-y=".05" data-fx-s=".85" data-fx-f=".4"><div class="wrap">
<div class="sec__head"><p class="label">Biblioteca dermatológica</p><h2 class="split">Entenda a sua <em>pele</em>.</h2><p>Um acervo de referência mantido pela clínica: doenças dermatológicas descritas em detalhe e um atlas de imagens clínicas.</p></div>
<div class="lib rv">
<div><form class="search" action="doencas/index.html" method="get" role="search"><label class="sr" for="q-home">Buscar doença</label><input id="q-home" name="q" type="search" data-live placeholder="Digite: acne, melasma, psoríase…" autocomplete="off"><button type="submit">Buscar →</button><div class="live" data-live-out hidden></div></form>
<div class="az">{letters}</div></div>
<div class="pair"><a class="glow" href="doencas/index.html"><span class="label">Doenças dermatológicas</span><b><span class="num">{len(DIS)}</span> verbetes</b><span>Epidemiologia, quadro clínico, diagnóstico e tratamento, em ordem alfabética.</span></a>
<a class="glow" href="atlas/index.html"><span class="label">Atlas de imagens</span><b><span class="num">{NI}</span> imagens</b><span>Registros clínicos organizados por doença, para fins educativos.</span></a></div>
</div></div></section>

<section class="sec" style="padding-top:0"><div class="wrap mag">
<img class="rv" src="assets/img/brand/revista.webp" alt="Revista digital Skin Prime — A arte da dermatologia" loading="lazy" width="1400" height="760">
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

<section class="sec" id="contato" style="padding-top:0" data-fx="ring" data-fx-x=".5" data-fx-y="0" data-fx-s="1.1" data-fx-f=".25"><div class="wrap">
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
<div><dt>Telefone · WhatsApp</dt><dd class="big"><a href="{WA_MSG}" target="_blank" rel="noopener">(81) 3036-4040</a></dd></div>
<div><dt>Endereço</dt><dd>RioMar Trade Center · Av. República do Líbano, 251<br>Torre C, 19º andar – Sala 1905<br>Pina, Recife – PE · CEP 51110-160</dd></div>
<div><dt>E-mail</dt><dd><a href="mailto:contato@skinprime.com.br">contato@skinprime.com.br</a></dd></div>
<div><dt>Trabalhe conosco</dt><dd><a href="mailto:contato@skinprime.com.br?subject=Vagas%20de%20Emprego%20Skin%20Prime">Envie seu currículo</a></dd></div>
</dl>
<div class="coord"><span>8°05′S · 34°53′W</span><a class="arrow" style="border:0;padding:0" href="{MAPS}" target="_blank" rel="noopener">Abrir no mapa</a></div>
<img src="assets/img/clinic/lounge-m.jpg" alt="Lounge da Skin Prime" loading="lazy" width="900" height="600">
</div>
</div></div></section>'''
write('index.html', page('index.html', '', 'Skin Prime: dermatologia, estética, nutrição e saúde no RioMar Trade Center, Recife. Conheça a clínica, os especialistas, os tratamentos e a biblioteca de doenças dermatológicas.', home))


# ---------------------------------------------------------------- clínica
tour = ''.join(f'<a href="assets/img/clinic/{k}.jpg" data-tour="{k}" data-alt="{E(c)}"><img src="assets/img/clinic/{k}-m.jpg" alt="{E(c)}" loading="lazy" width="900" height="600"><span class="cap3d">Ver em 3D</span><span class="cap">{E(c)}</span></a>' for k, c in CLINIC)
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
<div class="info"><dl><div><dt>Endereço</dt><dd>RioMar Trade Center · Av. República do Líbano, 251<br>Torre C, 19º andar – Sala 1905<br>Pina, Recife – PE · CEP 51110-160</dd></div>
<div><dt>Telefone · WhatsApp</dt><dd class="big"><a href="{WA_MSG}" target="_blank" rel="noopener">(81) 3036-4040</a></dd></div></dl>
<div class="coord"><span>8°05′S · 34°53′W</span><a class="arrow" style="border:0;padding:0" href="{MAPS}" target="_blank" rel="noopener">Abrir no mapa</a></div></div>
</div></section>''' + cta('')
write('clinica.html', page('clinica.html', 'A Clínica', 'Conheça os ambientes da Skin Prime no RioMar Trade Center, Recife: uma estrutura clínica para dermatologia, estética, nutrição e saúde.', body, 'clinica'))

# ---------------------------------------------------------------- especialistas
profs = ''.join(f'''<article class="profile" id="{t['k']}">
<div class="profile__id"><div class="profile__ph"><img src="assets/img/team/{t['k']}.jpg" alt="{E(t['n'])}" loading="lazy" width="640" height="640"></div>
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
    b = p['body']
    b = re.sub(r'(<br>\s*)+', '', b)

    def im(m):
        n = imgname(m.group(1))
        if not has(f'posts/{n}.jpg') or n == p['cover_f']:
            return ''
        return f'<img src="../assets/img/posts/{n}.jpg" alt="{m.group(2)}" loading="lazy">'
    b = re.sub(r'<img data-id="([^"]+)" alt="([^"]*)">', im, b)
    vids = list(p.get('vids') or [])

    def vd(m):
        if not vids:
            return ''
        v = vids.pop(0)
        return f'<video controls preload="metadata" playsinline src="https://video.wixstatic.com/video/{v}/720p/mp4/file.mp4"></video>'
    b = re.sub(r'<video></video>', vd, b)
    b = re.sub(r'<iframe[^>]*></iframe>', '', b)
    b = re.sub(r'<a href="(https?://[^"]*)">', r'<a href="\1" target="_blank" rel="noopener">', b)
    b = re.sub(r'<li><p>(.*?)</p></li>', r'<li>\1</li>', b, flags=re.S)
    b = re.sub(r'<(p|h2|h3|h4)>\s*</\1>', '', b)
    return b


for i, p in enumerate(POSTS):
    cats = ' · '.join(dict(CATS)[c] for c in p['cats'])
    mins = max(1, round(p['words'] / 200))
    cover = f'<div class="cover"><img src="../assets/img/posts/{p["cover_f"]}.jpg" alt="" width="1280" height="640"></div>' if p['cover_f'] else ''
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
                                              f"assets/img/posts/{p['cover_f']}.jpg" if p['cover_f'] else 'assets/img/clinic/vista.jpg'))

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
    gal = ''
    if d['imgs']:
        gal = f'''<h2 id="imagens" style="font-size:clamp(1.6rem,2.6vw,2.1rem);margin-top:2.2em;padding-top:.9em;border-top:1px solid var(--line);scroll-margin-top:110px">Atlas de imagens <span class="label label--mute" style="margin-left:10px">{len(d['imgs'])}</span></h2>
<div class="gal">{''.join(f'<a href="../assets/img/atlas/{n}.jpg" data-lb="atlas" data-alt="{E(d["t"])}"><img src="../assets/img/atlas/{n}.jpg" alt="{E(d["t"])} — imagem clínica {k}" loading="lazy" width="200" height="200"></a>' for k, n in enumerate(d['imgs'], 1))}</div>'''
    bib = f'<h3 style="margin-top:2.4em;font-size:1.2rem">Bibliografia</h3><p class="biblio" style="margin-top:.8em">{E(d["bib"])}</p>' if d['bib'] else ''
    body = phead('../', [('Doenças Dermatológicas', 'doencas/index.html'), (d['t'], '')],
                 ' · '.join(x for x in [f'Atualizado em {d["upd"]}' if d['upd'] else '', f'{len(d["imgs"])} imagens no atlas' if d['imgs'] else ''] if x), E(d['t'])) + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap art">
<aside class="art__side"><a class="arrow" style="justify-self:start" href="index.html">Voltar ao índice</a>{f'<ol>{toc}</ol>' if toc else ''}
<p class="note">Conteúdo informativo. Não substitui a consulta com um dermatologista. <a href="{WA_MSG}" target="_blank" rel="noopener" style="color:var(--aqua)">Agende sua avaliação</a>.</p></aside>
<article><div class="prose">{d['body']}</div>{gal}{bib}</article>
</div></section>
<nav class="pn" aria-label="Outras doenças"><a href="{prev['s']}.html"><span class="label label--mute">← Anterior</span><b>{E(prev['t'])}</b></a><a href="{nxt['s']}.html"><span class="label label--mute">Próxima →</span><b>{E(nxt['t'])}</b></a></nav>'''
    write(f"doencas/{d['s']}.html", page('doencas/x.html', d['t'], d['lead'], body, 'doencas'))

# ---------------------------------------------------------------- atlas
WI = [d for d in DIS if d['imgs']]
grid = ''.join(f'<a href="../doencas/{d["s"]}.html#imagens" data-k="{E(norm(d["t"]))}"><div class="ph"><img src="../assets/img/atlas/{d["imgs"][0]}.jpg" alt="" loading="lazy" width="200" height="200"></div><b>{E(d["t"])}</b><small>{len(d["imgs"])} {"imagem" if len(d["imgs"])==1 else "imagens"}</small></a>' for d in WI)
body = phead('../', [('Atlas de Imagens', '')], f'{NI} imagens · {len(WI)} doenças', 'Atlas de <em>imagens</em>.',
             'Registros clínicos organizados por doença, em ordem alfabética. Imagens reais, de caráter educativo.') + f'''
<section class="sec" style="padding-top:clamp(36px,5vw,64px)"><div class="wrap">
<div class="tools"><form class="search" role="search" style="max-width:560px"><label class="sr" for="q-a">Buscar no atlas</label><input id="q-a" type="search" data-filter-q placeholder="Buscar no atlas…" autocomplete="off"></form>
<a class="arrow" href="../doencas/index.html">Ler sobre as doenças</a></div>
<div class="atlas" data-filter-list>{grid}</div>
<p class="empty" hidden>Nenhum resultado no atlas.</p>
</div></section>''' + cta('../')
write('atlas/index.html', page('atlas/index.html', 'Atlas de Imagens', f'Atlas dermatológico da Skin Prime com {N_IMG} imagens clínicas organizadas por doença.', body, 'atlas'))

# ---------------------------------------------------------------- extras
body = phead('', [('Página não encontrada', '')], 'Erro 404', 'Esta página saiu do <em>foco</em>.', 'O endereço pode ter mudado. Volte ao início ou fale com a clínica.') + '<section class="sec"><div class="wrap"><a class="btn" href="/">Voltar ao início</a></div></section>'
write('404.html', page('404.html', 'Página não encontrada', 'Página não encontrada.', body).replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/'))
write('assets/img/brand/favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#071315"/><circle cx="32" cy="32" r="24" fill="none" stroke="#93ccd5" stroke-width="1.2"/><text x="32" y="43" text-anchor="middle" font-family="Didot,Bodoni MT,Georgia,serif" font-size="32" fill="#dba396">S</text></svg>')
urls = ['', 'clinica.html', 'especialistas.html', 'tratamentos/', 'doencas/', 'atlas/'] + [f"tratamentos/{p['s']}.html" for p in POSTS] + [f"doencas/{d['s']}.html" for d in DIS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://www.skinprime.com.br/{u}</loc></url>\n' for u in urls) + '</urlset>\n')
write('robots.txt', 'User-agent: *\nAllow: /\nSitemap: https://www.skinprime.com.br/sitemap.xml\n')
print('ok:', len(urls), 'páginas')
