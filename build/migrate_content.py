#!/usr/bin/env python3
"""Migração única: extrai o conteúdo que estava dentro de build.py e build/data/*.json
para arquivos em content/, que o painel administrativo (Sveltia CMS) edita.

Uso (na raiz do projeto): python3 build/migrate_content.py
"""
import json, os, re, io, contextlib
from markdownify import markdownify

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# roda o gerador atual para obter os dados já processados (POSTS, DIS, TEAM, ...)
ns = {'__file__': os.path.join(ROOT, 'build', 'build.py'), '__name__': 'migrate'}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open('build/build.py', encoding='utf-8').read(), 'build.py', 'exec'), ns)

C = 'content'
for d in ('config', 'equipe', 'doencas', 'tratamentos'):
    os.makedirs(os.path.join(C, d), exist_ok=True)


def dump(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def md(html):
    out = markdownify(html, heading_style='ATX', bullets='-', strip=['span'])
    out = re.sub(r'\n{3,}', '\n\n', out).strip()
    return out


# ---------------------------------------------------------------- configurações gerais
site = {
    'nome': 'Skin Prime',
    'abertura': {
        'rotulo': 'Recife · RioMar Trade Center · 19º andar',
        'titulo': 'A arte da',
        'titulo_destaque': 'dermatologia',
        'texto': 'A experiência e a tecnologia se encontram para trazer uma estrutura clínica nunca vista no Recife quando o assunto é **dermatologia, estética, nutrição e saúde**.',
    },
    'contato': {
        'telefone': '(81) 3036-4040',
        'whatsapp': '558130364040',
        'mensagem_whatsapp': 'Olá, Skin Prime! Gostaria de agendar uma consulta.',
        'email': 'contato@skinprime.com.br',
        'endereco_linha1': 'RioMar Trade Center · Av. República do Líbano, 251',
        'endereco_linha2': 'Torre C, 19º andar – Sala 1905',
        'endereco_linha3': 'Pina, Recife – PE · CEP 51110-160',
        'busca_mapa': 'RioMar Trade Center Torre C, Av. República do Líbano, 251, Pina, Recife - PE',
        'coordenadas': '8°05′S · 34°53′W',
    },
    'empresa': {'razao_social': 'Clinical Center Rio Mar · Skin Prime', 'cnpj': '37.572.208/0001-95'},
    'revista_pdf': ns['REVISTA'],
    'redes': [{'rede': n, 'usuario': h, 'link': u} for n, h, u in ns['SOCIAL']],
    'cores': {
        'fundo': '#f7f7f7', 'texto': '#1d2b2d', 'texto_secundario': '#4f6468',
        'botoes': '#996059', 'destaque': '#4a7079', 'rodape': '#1d2b2d',
    },
}
dump(f'{C}/config/site.json', site)

# ---------------------------------------------------------------- equipe
for i, t in enumerate(ns['TEAM'], 1):
    dump(f"{C}/equipe/{t['k']}.json", {
        'nome': t['n'], 'ordem': i, 'funcao': t['role'], 'registro': t['reg'],
        'foto': f"/assets/img/team/{t['k']}.jpg", 'frase': t['short'], 'titulo': t['h'],
        'texto': '\n\n'.join(t['tx']), 'link_rotulo': t['link'][0], 'link_url': t['link'][1],
    })

# ---------------------------------------------------------------- fotos da clínica
dump(f'{C}/config/clinica.json', {'fotos': [{'imagem': f'/assets/img/clinic/{k}.jpg', 'legenda': c} for k, c in ns['CLINIC']]})

# ---------------------------------------------------------------- doenças
SERV, OK, CRUZ = ns['SERV'], ns['OK_LEVELS'], ns['CRUZ']
for d in ns['DIS']:
    c = CRUZ.get(d['t'], {'itens': []})
    trat, exa = [], []
    for it in c['itens']:
        if it['nivel'].startswith(OK) and it['servico'] in SERV:
            nome = SERV[it['servico']][0]
            (exa if it['tipo'] == 'Diagnóstico' else trat).append(nome)
    body = re.sub(r'<h2 id="[^"]*">', '<h2>', d['body'])
    dump(f"{C}/doencas/{d['s']}.json", {
        'titulo': d['t'], 'atualizado': d['upd'], 'texto': md(body), 'bibliografia': d['bib'],
        'imagens': [f'/assets/img/atlas/{n}.jpg' for n in d['imgs']],
        'tratamentos': list(dict.fromkeys(trat)), 'exames': list(dict.fromkeys(exa)),
    })

# ---------------------------------------------------------------- tratamentos / news
for i, p in enumerate(ns['POSTS']):
    html = ns['post_body'](p)
    vids = []

    def keep(m):
        vids.append(m.group(0))
        return f'<p>VIDEO{len(vids) - 1}</p>'
    html = re.sub(r'<video[^>]*></video>', keep, html)
    html = html.replace('src="../assets/', 'src="/assets/')
    body = md(html)
    for k, v in enumerate(vids):
        body = body.replace(f'VIDEO{k}', v)
    dump(f"{C}/tratamentos/{p['s']}.json", {
        'titulo': p['title'].strip(), 'data': p['date'], 'ordem': i,
        'categorias': p['cats'], 'capa': f"/assets/img/posts/{p['cover_f']}.jpg" if p['cover_f'] else '',
        'resumo': p['excerpt'], 'texto': body,
    })

print('conteúdo migrado:', len(ns['TEAM']), 'membros ·', len(ns['DIS']), 'doenças ·', len(ns['POSTS']), 'tratamentos')
