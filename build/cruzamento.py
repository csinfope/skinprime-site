#!/usr/bin/env python3
"""Cruza cada doença do site com os tratamentos/diagnósticos que a clínica divulga no próprio site.

Método (somente evidência textual, sem inferência clínica):
  1. Catálogo = serviços descritos nas publicações de Tratamentos (build/data/posts.json).
  2. Para cada doença (build/data/doencas.json), procura no texto as modalidades do catálogo.
  3. Cada ocorrência é classificada pelo contexto da frase e guardada com o trecho.

Saídas: build/data/cruzamento.json e a planilha indicada em argv[1].
"""
import json, re, sys, unicodedata, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

def norm(s):
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()

D = json.load(open('build/data/doencas.json', encoding='utf-8'))
P = json.load(open('build/data/posts.json', encoding='utf-8'))
SITE = 'https://csinfope.github.io/skinprime-site/'

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', norm(s)).strip('-')

# serviço da clínica -> (tipo, padrões no texto das doenças, palavras para achar as publicações da clínica)
CAT = [
    ('Toxina botulínica', 'Tratamento', [r'toxina botulinica', r'\bbotox\b'], ['toxina botulinica', 'botox', 'btx']),
    ('Preenchimento com ácido hialurônico', 'Tratamento', [r'preenchimento', r'acido hialuronico', r'preenchedor'], ['preenchimento', 'acido hialuronico']),
    ('Peelings químicos', 'Tratamento', [r'peeling', r'esfoliacao quimica', r'quimioesfoliacao'], ['peelings quimicos']),
    ('Dermoabrasão / microdermoabrasão / peeling de cristal', 'Tratamento', [r'dermoabrasao', r'dermabrasao'], ['dermoabrasao', 'peeling de cristal']),
    ('Microagulhamento', 'Tratamento', [r'microagulhamento'], ['microagulhamento']),
    ('Laser de CO2 / laser fracionado', 'Tratamento', [r'laser (de )?co2', r'\bco2\b', r'laser fracionado', r'laser ablativo'], ['laser de co2', 'mmp e laser']),
    ('Laser ND-YAG / Q-Switched (Spectra XT)', 'Tratamento', [r'nd ?[:\-]? ?yag', r'q[\- ]switched'], ['spectra', 'q-switched', 'nd-yag']),
    ('Luz intensa pulsada', 'Tratamento', [r'luz intensa pulsada', r'luz pulsada'], ['luz intensa pulsada']),
    ('Lasers (tipo a confirmar)', 'Tratamento', [r'\blasers?\b', r'laserterapia'], ['lasers', 'duvidas frequentes sobre laser', 'zye']),
    ('Depilação a laser', 'Tratamento', [r'\bdepilacao', r'\bepilacao', r'fotoepilacao'], ['depilacao']),
    ('Fototerapia', 'Tratamento', [r'fototerapia', r'\bpuva\b', r'\buvb\b'], ['fototerapia']),
    ('LED', 'Tratamento', [r'\bleds?\b'], ['led -']),
    ('Eletrocauterização', 'Tratamento', [r'eletrocauteriza', r'eletrocoagula', r'eletrocirurgia', r'eletrodissec', r'eletrofulgura', r'\bcauterizacao\b'], ['eletrocauterizacao']),
    ('Curetagem', 'Tratamento', [r'curetagem'], ['curetagem']),
    ('Pequenas cirurgias (avaliar porte)', 'Tratamento', [r'exerese', r'excisao', r'remocao cirurgica', r'tratamento cirurgico', r'\bcirurgi'], ['pequenas cirurgias']),
    ('Tricologia e tratamentos capilares', 'Tratamento', [r'minoxidil', r'mesoterapia', r'microinfusao'], ['tricologia', 'tratamento capilares', 'mmp e laser', 'intradermoterapia', 'cabelos saudaveis']),
    ('Radiofrequência', 'Tratamento', [r'radiofrequencia'], ['radiofrequencia']),
    ('Nutrição', 'Tratamento', [r'\bdieta', r'nutricion'], ['nutricao funcional']),
    ('Biópsia', 'Diagnóstico', [r'biopsia', r'histopatolog'], ['biopsia']),
    ('Dermatoscopia digital', 'Diagnóstico', [r'dermatoscopi', r'dermoscopi'], ['dermatoscopia']),
]
# modalidades citadas nos textos das doenças que NÃO aparecem nas publicações da clínica
GAP = [
    ('Crioterapia / criocirurgia (nitrogênio líquido)', [r'crioterapia', r'criocirurgia', r'nitrogenio liquido']),
    ('Terapia fotodinâmica', [r'terapia fotodinamica', r'fotodinamica']),
    ('Cirurgia micrográfica de Mohs', [r'\bmohs\b']),
    ('Laser de corante pulsado (dye laser)', [r'dye laser', r'pulsed dye', r'corante pulsado']),
    ('Excimer laser', [r'excimer']),
    ('Laser Erbium', [r'erbium']),
    ('Infiltração intralesional', [r'infiltracao', r'intralesional']),
    ('Radioterapia', [r'radioterapia']),
]
CUE = re.compile(r'trat|terap|indica|opc|utiliz|remo[cv]|realiza|recomend|respond|melhora|conduta|procedimento|emprega|aplica|sess[ao]|pode ser|podem ser|eficaz|resultado')
NEG = re.compile(r'\bnao\b|evitar|contraindic|contra-indic|desencade|causad|induzid|secundari[oa] a|complicac|apos (o |a )?(uso|tratamento|aplicac)|ineficaz|pouco eficaz|sem resposta')
SEC = re.compile(r'(?:^|\n)\s*(Tratamentos?|Terap[êe]utica|Conduta)\s*[.:\-–]')
REF = re.compile(r'\b(of|and|the|review|journal|with|et al|clinical|treatment|study)\b')
SUN = re.compile(r'filtro|protetor|fotoprote|protecao solar|protegendo|bronzeamento|exposicao solar|radiacao solar')
OTHER_LASER = re.compile(r'excimer|dye laser|pulsed dye|corante pulsado|erbium|alexandrit')
HAIR = re.compile(r'alopecia|foliculite decalvante|foliculite dissecante|moniletrix')

def posts_for(keys):
    out = []
    for p in P:
        t = norm(p['title'])
        if any(k in t for k in keys) and p['title'].strip() not in out:
            out.append(p['title'].strip())
    return out

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?;])\s+|\n+', text) if s.strip()]

def snippet(sent, m):
    a = max(0, m.start() - 110); b = min(len(sent), m.end() + 130)
    return ('…' if a else '') + sent[a:b].strip() + ('…' if b < len(sent) else '')

rows, gaps, summary = [], [], []
for d in sorted(D, key=lambda x: norm(x['title'])):
    title = re.sub(r'\s+', ' ', d['title']).strip(); text = d['texto']
    ms = SEC.search(text); sec_start = ms.start() if ms else None
    # frases com a posição no texto
    sents, pos = [], 0
    for s in sentences(text):
        i = text.find(s[:40], pos); i = pos if i < 0 else i; sents.append((i, s)); pos = i + len(s)
    found = {}
    for name, tipo, pats, _ in CAT:
        best = None
        for i, s in sents:
            ns = norm(s)
            if REF.search(ns) or (name == 'Fototerapia' and SUN.search(ns)) or (name == 'Lasers (tipo a confirmar)' and OTHER_LASER.search(ns)):
                continue
            for pat in pats:
                m = re.search(pat, ns)
                if not m:
                    continue
                in_sec = sec_start is not None and i >= sec_start
                if tipo == 'Diagnóstico':
                    lvl = 'Citado como exame'
                elif NEG.search(ns):
                    lvl = 'Revisar: frase com negação ou causa'
                elif in_sec or CUE.search(ns):
                    lvl = 'Indicado no texto'
                else:
                    lvl = 'Apenas citado'
                rank = {'Indicado no texto': 0, 'Citado como exame': 0, 'Apenas citado': 1, 'Revisar: frase com negação ou causa': 2}[lvl]
                if best is None or rank < best[0]:
                    best = (rank, lvl, snippet(s, re.search(pat, ns)) if len(ns) == len(s) else s[:240])
                break
        if best:
            found[name] = (tipo, best[1], best[2])
    # laser genérico só entra se nenhum laser específico foi achado
    if 'Lasers (tipo a confirmar)' in found and any(k in found for k in ('Laser de CO2 / laser fracionado', 'Laser ND-YAG / Q-Switched (Spectra XT)')):
        del found['Lasers (tipo a confirmar)']
    if HAIR.search(norm(title)) and 'Tricologia e tratamentos capilares' not in found:
        found['Tricologia e tratamentos capilares'] = ('Tratamento', 'Área de atuação (pelo nome da doença)', 'Doença do couro cabeludo/cabelos; a clínica divulga Tricologia e tratamentos capilares.')
    g = []
    for name, pats in GAP:
        for i, s in sents:
            ns = norm(s); m = next((re.search(p, ns) for p in pats if re.search(p, ns)), None)
            if m and not REF.search(ns):
                g.append(name); gaps.append((title, name, snippet(s, m) if len(ns) == len(s) else s[:240])); break
    for name, (tipo, lvl, snip) in found.items():
        pubs = posts_for(next(c[3] for c in CAT if c[0] == name))
        rows.append((title, name, tipo, lvl, snip, '; '.join(pubs[:3]), SITE + 'doencas/' + slug(title) + '.html'))
    summary.append((title, found, g, sec_start is not None))

json.dump([{'doenca': t, 'itens': [{'servico': k, 'tipo': v[0], 'nivel': v[1], 'trecho': v[2]} for k, v in f.items()], 'sem_correspondencia': g}
           for t, f, g, _ in summary], open('build/data/cruzamento.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ planilha
wb = Workbook()
F = 'Arial'
HFILL = PatternFill('solid', fgColor='0B2A30'); HFONT = Font(name=F, bold=True, color='FFFFFF', size=10)
BASE = Font(name=F, size=10); WRAP = Alignment(wrap_text=True, vertical='top')
YEL = PatternFill('solid', fgColor='FFF2CC')
def head(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, 1):
        c = ws.cell(row=1, column=i); c.font = HFONT; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32; ws.freeze_panes = 'B2'
def finish(ws, name, ncols):
    for r in ws.iter_rows(min_row=2):
        for c in r:
            c.font = BASE; c.alignment = WRAP
    if ws.max_row > 1:
        t = Table(displayName=name, ref=f'A1:{get_column_letter(ncols)}{ws.max_row}')
        t.tableStyleInfo = TableStyleInfo(name='TableStyleLight1', showRowStripes=True); ws.add_table(t)

# 1) Cruzamento (formato longo)
ws = wb.active; ws.title = 'Cruzamento'
head(ws, ['Doença', 'Serviço da clínica', 'Tipo', 'Nível de evidência no texto', 'Trecho do texto da doença', 'Publicações da clínica sobre o serviço', 'Página da doença', 'Revisão médica (Confirmar / Excluir)', 'Observação do revisor'],
     [30, 34, 13, 26, 70, 40, 34, 20, 30])
for r in rows:
    ws.append(list(r) + ['', ''])
finish(ws, 'Cruzamento', 9)
for r in range(2, ws.max_row + 1):
    ws.cell(row=r, column=8).fill = YEL; ws.cell(row=r, column=9).fill = YEL
    ws.cell(row=r, column=7).hyperlink = ws.cell(row=r, column=7).value
n = ws.max_row

# 2) Resumo por doença
ws2 = wb.create_sheet('Por doença')
head(ws2, ['Doença', 'Tratamentos indicados no texto e oferecidos pela clínica', 'Tratamentos apenas citados / a revisar', 'Diagnóstico na clínica', 'Citado no texto, sem publicação correspondente da clínica', 'Nº de serviços cruzados', 'Texto tem seção de tratamento?'],
     [32, 50, 44, 26, 44, 12, 14])
for i, (t, f, g, has) in enumerate(summary, 2):
    ind = [k for k, v in f.items() if v[0] == 'Tratamento' and v[1].startswith(('Indicado', 'Área'))]
    oth = [f'{k} ({v[1].split(":")[0].lower()})' for k, v in f.items() if v[0] == 'Tratamento' and not v[1].startswith(('Indicado', 'Área'))]
    dia = [k for k, v in f.items() if v[0] == 'Diagnóstico']
    ws2.append([t, '; '.join(ind), '; '.join(oth), '; '.join(dia), '; '.join(g), f'=COUNTIF(Cruzamento!$A$2:$A${n},A{i})', 'Sim' if has else 'Não'])
finish(ws2, 'PorDoenca', 7)

# 3) Por serviço
ws3 = wb.create_sheet('Por serviço')
head(ws3, ['Serviço da clínica', 'Tipo', 'Nº de doenças (todas as menções)', 'Nº com indicação no texto', 'Doenças com indicação no texto', 'Doenças apenas citadas / a revisar'], [38, 13, 14, 14, 80, 60])
for i, (name, tipo, _, _) in enumerate(CAT, 2):
    ind = [r[0] for r in rows if r[1] == name and r[3].startswith(('Indicado', 'Área', 'Citado como exame'))]
    oth = [r[0] for r in rows if r[1] == name and not r[3].startswith(('Indicado', 'Área', 'Citado como exame'))]
    ws3.append([name, tipo, f'=COUNTIF(Cruzamento!$B$2:$B${n},A{i})',
                f'=COUNTIFS(Cruzamento!$B$2:$B${n},A{i},Cruzamento!$D$2:$D${n},"Indicado*")+COUNTIFS(Cruzamento!$B$2:$B${n},A{i},Cruzamento!$D$2:$D${n},"Área*")+COUNTIFS(Cruzamento!$B$2:$B${n},A{i},Cruzamento!$D$2:$D${n},"Citado como exame")',
                '; '.join(ind), '; '.join(oth)])
finish(ws3, 'PorServico', 6)

# 4) Lacunas
ws4 = wb.create_sheet('Sem correspondência')
head(ws4, ['Doença', 'Modalidade citada no texto da doença', 'Trecho', 'A clínica oferece? (Sim / Não)'], [32, 40, 90, 18])
for g in gaps:
    ws4.append(list(g) + [''])
finish(ws4, 'Lacunas', 4)
for r in range(2, ws4.max_row + 1):
    ws4.cell(row=r, column=4).fill = YEL

# 5) Catálogo
ws5 = wb.create_sheet('Catálogo usado')
head(ws5, ['Serviço da clínica', 'Tipo', 'Publicações do site que descrevem o serviço', 'Termos procurados nos textos das doenças (sem acento)'], [38, 13, 80, 60])
for name, tipo, pats, keys in CAT:
    ws5.append([name, tipo, '; '.join(posts_for(keys)), ', '.join(p.replace('\\b', '').replace('\\', '') for p in pats)])
finish(ws5, 'Catalogo', 4)

# 0) Leia-me
ws0 = wb.create_sheet('Leia-me', 0)
ws0.column_dimensions['A'].width = 34; ws0.column_dimensions['B'].width = 100
nd = len(summary)
lines = [
    ('Cruzamento: doenças do site × serviços da clínica', None),
    ('', None),
    ('O que é', 'Para cada uma das doenças publicadas no site, quais tratamentos e exames que a clínica divulga no próprio site aparecem no texto daquela doença.'),
    ('Como foi feito', 'Busca automática de termos. O catálogo de serviços vem das 88 publicações de Tratamentos do site. Cada serviço foi procurado no texto de cada doença; o trecho encontrado fica registrado. Não há inferência clínica: se o texto da doença não cita a modalidade, ela não entra.'),
    ('Limite importante', 'É um cruzamento de textos, não uma indicação médica. Uma modalidade citada pode estar em contexto histórico, de exceção ou de causa. Todo item precisa ser confirmado por um dermatologista da clínica antes de ser publicado ou usado com pacientes.'),
    ('Doença sem serviço cruzado', 'Não significa que a clínica não trata. Significa que o texto só descreve tratamento clínico/medicamentoso (feito em consulta) ou não cita nenhuma modalidade do catálogo.'),
    ('', None),
    ('Níveis de evidência', None),
    ('Indicado no texto', 'A modalidade aparece na seção de tratamento da doença, ou numa frase com termos de tratamento (tratar, indicado, opção, utilizado...).'),
    ('Apenas citado', 'A modalidade aparece no texto, mas fora de um contexto claro de tratamento.'),
    ('Revisar: frase com negação ou causa', 'A frase contém "não", "evitar", "desencadeado", "após o uso" etc. Pode ser contraindicação ou causa, não tratamento.'),
    ('Citado como exame', 'Biópsia/histopatologia ou dermatoscopia citadas no texto (diagnóstico).'),
    ('Área de atuação (pelo nome da doença)', 'Alopecias e afins: ligadas à Tricologia pelo nome, mesmo sem a modalidade citada no texto.'),
    ('', None),
    ('Células amarelas', 'São para a clínica preencher: confirmação médica de cada item (aba Cruzamento) e se a clínica oferece as modalidades sem publicação correspondente (aba Sem correspondência).'),
    ('', None),
    ('Números', None),
    ('Doenças analisadas', nd),
    ('Doenças com ao menos um serviço cruzado', f'=COUNTIF(\'Por doença\'!F2:F{nd + 1},">0")'),
    ('Doenças sem nenhum serviço cruzado', f'=COUNTIF(\'Por doença\'!F2:F{nd + 1},0)'),
    ('Pares doença × serviço encontrados', f'=COUNTA(Cruzamento!A2:A{n})'),
    ('… com indicação no texto (tratamento)', f'=COUNTIFS(Cruzamento!C2:C{n},"Tratamento",Cruzamento!D2:D{n},"Indicado*")'),
    ('… apenas citados', f'=COUNTIF(Cruzamento!D2:D{n},"Apenas citado")'),
    ('… a revisar (negação ou causa)', f'=COUNTIF(Cruzamento!D2:D{n},"Revisar*")'),
    ('… exames (biópsia, dermatoscopia)', f'=COUNTIF(Cruzamento!C2:C{n},"Diagnóstico")'),
    ('Menções a modalidades sem publicação da clínica', f'=COUNTA(\'Sem correspondência\'!A2:A{len(gaps) + 1})'),
    ('Doenças cujo texto tem seção de tratamento', f'=COUNTIF(\'Por doença\'!G2:G{nd + 1},"Sim")'),
    ('', None),
    ('Fonte', 'Textos de www.skinprime.com.br coletados em 09/11/2026 (214 doenças e 88 publicações de tratamentos). O site original só expõe parte do catálogo de doenças a partir da letra P.'),
]
for a, b in lines:
    ws0.append([a, b])
for r in ws0.iter_rows():
    for c in r:
        c.font = BASE; c.alignment = WRAP
ws0['A1'].font = Font(name=F, bold=True, size=14)
for r in ws0.iter_rows(min_col=1, max_col=1):
    if r[0].value in ('Níveis de evidência', 'Números'):
        r[0].font = Font(name=F, bold=True, size=11)
    elif r[0].row > 1:
        r[0].font = Font(name=F, bold=True, size=10)
wb.save(sys.argv[1])
c = collections.Counter(r[3] for r in rows)
print('doencas', nd, '· pares', len(rows), dict(c), '· lacunas', len(gaps), '· sem cruzamento', sum(1 for _, f, _, _ in summary if not f))
