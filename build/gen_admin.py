#!/usr/bin/env python3
"""Gera o painel administrativo em site/admin/ (Sveltia CMS).

- site/admin/index.html  : página do painel
- site/admin/config.yml  : quais conteúdos e campos aparecem no painel (JSON é YAML válido)
O código do Sveltia CMS fica em site/admin/vendor/ (versão fixa, copiada do pacote npm @sveltia/cms).
Uso: python3 build/gen_admin.py
"""
import json, os, re, io, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
REPO = 'csinfope/skinprime-site'
SITE_URL = 'https://csinfope.github.io/skinprime-site/'

# nomes dos serviços e categorias vêm do próprio gerador, para o painel e o site usarem os mesmos valores
src = open('build/build.py', encoding='utf-8').read()
ns = {}
exec(re.search(r"^CATS = \[.*?\]\n", src, re.S | re.M).group(0), ns)
exec(re.search(r"^SERV = \{.*?\n\}\n", src, re.S | re.M).group(0), ns)
SERVICES = [v[0] for v in ns['SERV'].values()]
EXAMS = [n for n in SERVICES if n in ('Biópsia', 'Dermatoscopia digital')]
TREATS = [n for n in SERVICES if n not in EXAMS]
CATS = [{'label': t, 'value': k} for k, t in ns['CATS']]


def S(label, name, hint=None, required=True, widget='string', **kw):
    f = {'label': label, 'name': name, 'widget': widget}
    if hint:
        f['hint'] = hint
    if not required:
        f['required'] = False
    f.update(kw)
    return f


config = {
    'backend': {'name': 'github', 'repo': REPO, 'branch': 'main',
                'commit_messages': {'create': 'Painel: cria {{collection}} “{{slug}}”', 'update': 'Painel: atualiza {{collection}} “{{slug}}”',
                                    'delete': 'Painel: remove {{collection}} “{{slug}}”', 'uploadMedia': 'Painel: envia imagem “{{path}}”',
                                    'deleteMedia': 'Painel: remove imagem “{{path}}”'}},
    'site_url': SITE_URL, 'display_url': SITE_URL,
    'logo': {'src': '../assets/img/brand/logo-teal.png'},
    'media_folder': 'site/assets/img/uploads', 'public_folder': '/assets/img/uploads',
    'slug': {'encoding': 'ascii', 'clean_accents': True, 'sanitize_replacement': '-'},
    'collections': [
        {
            'name': 'configuracoes', 'label': 'Configurações do site', 'icon': 'settings', 'editor': {'preview': False},
            'files': [
                {'name': 'site', 'label': 'Informações gerais, contato e cores', 'file': 'content/config/site.json', 'format': 'json',
                 'fields': [
                     S('Nome da clínica', 'nome'),
                     {'label': 'Abertura da página inicial', 'name': 'abertura', 'widget': 'object', 'fields': [
                         S('Linha pequena acima do título', 'rotulo'),
                         S('Título', 'titulo', 'Primeira parte do título. Ex.: “A arte da”.'),
                         S('Palavra em destaque', 'titulo_destaque', 'Aparece em itálico, com degradê. Ex.: “dermatologia”.'),
                         S('Texto', 'texto', 'Use **duas estrelas** em volta das palavras que devem ficar em negrito.', widget='text'),
                     ]},
                     {'label': 'Contato', 'name': 'contato', 'widget': 'object', 'fields': [
                         S('Telefone (como aparece no site)', 'telefone', 'Ex.: (81) 3036-4040'),
                         S('Número do WhatsApp', 'whatsapp', 'Só números, com 55 e DDD. Ex.: 558130364040'),
                         S('Mensagem pronta do WhatsApp', 'mensagem_whatsapp'),
                         S('E-mail', 'email'),
                         S('Endereço · linha 1', 'endereco_linha1'),
                         S('Endereço · linha 2', 'endereco_linha2', required=False),
                         S('Endereço · linha 3', 'endereco_linha3', required=False),
                         S('Endereço para o mapa do Google', 'busca_mapa', 'O texto que o Google Maps vai procurar.'),
                         S('Coordenadas (texto decorativo)', 'coordenadas', required=False),
                     ]},
                     {'label': 'Empresa', 'name': 'empresa', 'widget': 'object', 'fields': [S('Razão social', 'razao_social'), S('CNPJ', 'cnpj')]},
                     S('Link da revista digital (PDF)', 'revista_pdf', required=False),
                     {'label': 'Redes sociais', 'name': 'redes', 'widget': 'list', 'required': False, 'summary': '{{fields.rede}} · {{fields.usuario}}',
                      'fields': [S('Rede', 'rede', 'Ex.: Instagram'), S('Usuário ou nome exibido', 'usuario'), S('Link', 'link')]},
                     {'label': 'Cores do site', 'name': 'cores', 'widget': 'object',
                      'hint': 'Mudanças de cor aparecem em todo o site. O fundo animado e o rodapé usam a paleta da marca.', 'fields': [
                          S('Fundo', 'fundo', widget='color'), S('Texto principal', 'texto', widget='color'),
                          S('Texto secundário', 'texto_secundario', widget='color'),
                          S('Botões principais e WhatsApp', 'botoes', widget='color'),
                          S('Destaques (rótulos, links, botões de seleção)', 'destaque', widget='color'),
                          S('Rodapé', 'rodape', widget='color'),
                      ]},
                 ]},
                {'name': 'clinica', 'label': 'Fotos dos ambientes da clínica', 'file': 'content/config/clinica.json', 'format': 'json',
                 'media_folder': '/site/assets/img/clinic', 'public_folder': '/assets/img/clinic',
                 'fields': [{'label': 'Fotos', 'name': 'fotos', 'widget': 'list', 'summary': '{{fields.legenda}}',
                             'hint': 'Arraste para mudar a ordem. Fotos na horizontal funcionam melhor no tour 3D.',
                             'fields': [S('Foto', 'imagem', widget='image'), S('Legenda', 'legenda')]}]},
            ],
        },
        {
            'name': 'doencas', 'label': 'Doenças', 'label_singular': 'Doença', 'icon': 'medical_information',
            'folder': 'content/doencas', 'format': 'json', 'extension': 'json', 'create': True, 'delete': True,
            'identifier_field': 'titulo', 'slug': '{{titulo}}', 'summary': '{{titulo}}', 'sortable_fields': ['titulo'],
            'media_folder': '/site/assets/img/atlas', 'public_folder': '/assets/img/atlas', 'editor': {'preview': False},
            'description': 'Cada doença gera sua página e, se tiver imagens, uma página no Atlas.',
            'fields': [
                S('Nome da doença', 'titulo'),
                S('Atualizado em', 'atualizado', 'Ex.: 03/02/2025', required=False),
                S('Texto', 'texto', 'Use “Heading 2” (Título 2) para as seções: Epidemiologia, Quadro clínico, Tratamento… Elas viram o índice lateral.', widget='markdown'),
                S('Bibliografia', 'bibliografia', required=False, widget='text'),
                {'label': 'Imagens do atlas', 'name': 'imagens', 'widget': 'list', 'required': False,
                 'hint': 'Imagens clínicas desta doença. A primeira é a capa no Atlas.',
                 'field': {'label': 'Imagem', 'name': 'imagem', 'widget': 'image'}},
                {'label': 'Tratamentos da clínica para esta doença', 'name': 'tratamentos', 'widget': 'select', 'multiple': True,
                 'required': False, 'options': TREATS, 'hint': 'Aparecem no bloco “Na Skin Prime” no fim da página. Peça a revisão de um dermatologista.'},
                {'label': 'Exames da clínica para esta doença', 'name': 'exames', 'widget': 'select', 'multiple': True,
                 'required': False, 'options': EXAMS},
            ],
        },
        {
            'name': 'tratamentos', 'label': 'Tratamentos e News', 'label_singular': 'Publicação', 'icon': 'spa',
            'folder': 'content/tratamentos', 'format': 'json', 'extension': 'json', 'create': True, 'delete': True,
            'identifier_field': 'titulo', 'slug': '{{titulo}}', 'summary': '{{titulo}} · {{data}}', 'sortable_fields': ['data', 'titulo'],
            'media_folder': '/site/assets/img/posts', 'public_folder': '/assets/img/posts', 'editor': {'preview': False},
            'fields': [
                S('Título', 'titulo'),
                S('Data', 'data', widget='datetime', format='YYYY-MM-DD', time_format=False, date_format='DD/MM/YYYY'),
                {'label': 'Categorias', 'name': 'categorias', 'widget': 'select', 'multiple': True, 'required': False, 'options': CATS,
                 'hint': '“News” coloca a publicação na seção de novidades da página inicial.'},
                S('Imagem de capa', 'capa', required=False, widget='image'),
                S('Resumo', 'resumo', 'Aparece nos cartões. Se ficar vazio, usa o começo do texto.', required=False, widget='text'),
                S('Texto', 'texto', widget='markdown'),
            ],
        },
        {
            'name': 'equipe', 'label': 'Equipe', 'label_singular': 'Membro da equipe', 'icon': 'groups',
            'folder': 'content/equipe', 'format': 'json', 'extension': 'json', 'create': True, 'delete': True,
            'identifier_field': 'nome', 'slug': '{{nome}}', 'summary': '{{ordem}} · {{nome}} · {{funcao}}', 'sortable_fields': ['ordem', 'nome'],
            'media_folder': '/site/assets/img/team', 'public_folder': '/assets/img/team', 'editor': {'preview': False},
            'fields': [
                S('Nome', 'nome'),
                S('Ordem de exibição', 'ordem', 'Número: 1 aparece primeiro.', widget='number', value_type='int', default=99),
                S('Função', 'funcao', 'Ex.: Dermatologista'),
                S('Registro profissional', 'registro', 'Ex.: CRM 5999 · RQE 636', required=False),
                S('Foto', 'foto', 'Foto quadrada, com o rosto centralizado.', widget='image'),
                S('Frase curta (cartão da página inicial)', 'frase', required=False, widget='text'),
                S('Título do perfil', 'titulo', required=False),
                S('Texto do perfil', 'texto', 'Separe os parágrafos com uma linha em branco.', required=False, widget='text'),
                S('Rótulo do link', 'link_rotulo', 'Ex.: Instagram', required=False),
                S('Link (Instagram ou site)', 'link_url', required=False),
            ],
        },
    ],
}

os.makedirs('site/admin', exist_ok=True)
with open('site/admin/config.yml', 'w', encoding='utf-8') as f:
    f.write('# Configuração do painel (Sveltia CMS). Gerado por build/gen_admin.py — JSON também é YAML válido.\n')
    json.dump(config, f, ensure_ascii=False, indent=1)
    f.write('\n')
with open('site/admin/index.html', 'w', encoding='utf-8') as f:
    f.write('''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Painel · Skin Prime</title>
<link rel="icon" href="../assets/img/brand/favicon.svg" type="image/svg+xml">
</head>
<body>
<script src="vendor/sveltia-cms.js"></script>
</body>
</html>
''')
print('painel gerado:', len(TREATS), 'tratamentos e', len(EXAMS), 'exames como opções')
