#!/usr/bin/env python3
"""Planilha para revisão médica: uma linha por doença, com o que está publicado no site e campos para o médico.
Uso: python3 build/planilha_revisao.py SAIDA.xlsx   (lê build/data/cruzamento.json)"""
import json, sys, re, unicodedata
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

J = json.load(open('build/data/cruzamento.json', encoding='utf-8'))
SITE = 'https://csinfope.github.io/skinprime-site/doencas/'
def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()).strip('-')
NOME = {'Dermoabrasão / microdermoabrasão / peeling de cristal': 'Dermoabrasão e microdermoabrasão', 'Laser de CO2 / laser fracionado': 'Laser de CO2',
        'Laser ND-YAG / Q-Switched (Spectra XT)': 'Laser ND-YAG / Q-Switched', 'Lasers (tipo a confirmar)': 'Lasers (tipo a confirmar)',
        'Pequenas cirurgias (avaliar porte)': 'Pequenas cirurgias', 'Nutrição': 'Acompanhamento nutricional', 'Curetagem': 'Curetagem dermatológica'}
nm = lambda s: NOME.get(s, s)
OK = ('Indicado no texto', 'Área de atuação', 'Citado como exame')

F = 'Arial'
base = Font(name=F, size=10); bold = Font(name=F, size=10, bold=True)
hfont = Font(name=F, size=10, bold=True, color='FFFFFF'); hfill = PatternFill('solid', fgColor='0B2A30')
yel = PatternFill('solid', fgColor='FFF2CC'); grey = PatternFill('solid', fgColor='F2F2F2')
thin = Side(style='thin', color='BFBFBF'); box = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')

wb = Workbook()
# ------------------------------------------------------------ Instruções
w0 = wb.active; w0.title = 'Instruções'
w0.column_dimensions['A'].width = 30; w0.column_dimensions['B'].width = 105
txt = [
    ('Revisão médica: doenças × tratamentos da clínica', ''),
    ('', ''),
    ('Para que serve', 'O site da Skin Prime mostra, ao final da página de cada doença, um bloco "Na Skin Prime" com os tratamentos e exames da clínica ligados àquela doença. Esta planilha lista o que está publicado em cada uma, para o médico confirmar, corrigir ou completar.'),
    ('De onde vieram as ligações', 'De uma busca automática de palavras nos textos do próprio site: se o texto da doença cita uma modalidade que a clínica divulga, ela foi ligada. Não houve avaliação clínica. Por isso podem existir ligações indevidas e faltar ligações óbvias.'),
    ('', ''),
    ('Como preencher', ''),
    ('Aba "Revisão por doença"', 'Preencha apenas as colunas amarelas (G a J). As colunas A a F são o que o sistema encontrou.'),
    ('G · Aprovado como está?', 'Escolha Sim, Não ou Com ajustes.'),
    ('H · Excluir', 'Escreva os tratamentos ou exames da lista que NÃO devem aparecer para essa doença.'),
    ('I · Incluir', 'Escreva os tratamentos ou exames que a clínica oferece para essa doença e que faltaram.'),
    ('J · Observações', 'Qualquer orientação: texto a mudar, doença que não deve ter o bloco, encaminhamento etc.'),
    ('Aba "Modalidades a confirmar"', 'Modalidades citadas nos textos das doenças que não têm página no site (crioterapia, terapia fotodinâmica etc.). Marque se a clínica oferece.'),
    ('Aba "Trechos de apoio"', 'Só para consulta: o trecho do texto que originou cada ligação.'),
    ('', ''),
    ('Exemplo de preenchimento', 'Doença: Melasma · G: Com ajustes · H: Biópsia · I: Laser de picossegundos; Microagulhamento · J: Reforçar fotoproteção no texto.'),
    ('', ''),
    ('Legenda das colunas', ''),
    ('C · Tratamentos publicados', 'Estão hoje no site, na página da doença.'),
    ('D · Exames publicados', 'Biópsia e dermatoscopia, quando citadas no texto. Também estão hoje no site.'),
    ('E · Não publicados (a avaliar)', 'Modalidades da clínica que aparecem no texto em contexto duvidoso (apenas citadas, ou em frase com negação/causa). Não estão no site.'),
    ('F · Sem página na clínica', 'Modalidades citadas no texto da doença para as quais o site não tem publicação. Não estão no site.'),
    ('', ''),
    ('Resumo', ''),
    ('Doenças na planilha', f'=COUNTA(\'Revisão por doença\'!B2:B{len(J) + 1})'),
    ('Com tratamento ou exame publicado', f'=COUNTIF(\'Revisão por doença\'!K2:K{len(J) + 1},"Sim")'),
    ('Sem nenhum item publicado (bloco genérico)', f'=COUNTIF(\'Revisão por doença\'!K2:K{len(J) + 1},"Não")'),
    ('Já revisadas pelo médico', f'=COUNTA(\'Revisão por doença\'!G2:G{len(J) + 1})'),
    ('Faltam revisar', f'=COUNTA(\'Revisão por doença\'!B2:B{len(J) + 1})-COUNTA(\'Revisão por doença\'!G2:G{len(J) + 1})'),
]
for a, b in txt:
    w0.append([a, b])
for r in w0.iter_rows():
    for c in r:
        c.font = base; c.alignment = wrap
    if r[0].value and not r[1].value:
        r[0].font = Font(name=F, size=11, bold=True)
    elif r[0].value:
        r[0].font = bold
w0['A1'].font = Font(name=F, size=14, bold=True)
w0.page_setup.orientation = 'landscape'; w0.page_setup.fitToWidth = 1; w0.page_setup.fitToHeight = 0; w0.sheet_properties.pageSetUpPr.fitToPage = True

# ------------------------------------------------------------ Revisão por doença
ws = wb.create_sheet('Revisão por doença')
cols = [('Nº', 5), ('Doença', 28), ('Tratamentos publicados no site', 36), ('Exames publicados no site', 18), ('Não publicados (a avaliar)', 26),
        ('Citado no texto, sem página na clínica', 26), ('Aprovado como está?', 13), ('Excluir (o que não se aplica)', 26), ('Incluir (o que faltou)', 26), ('Observações do médico', 30), ('Tem item publicado?', 10), ('Página no site', 16)]
ws.append([c for c, _ in cols])
for i, (_, w) in enumerate(cols, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
for n, d in enumerate(J, 1):
    it = d['itens']
    trat = [nm(i['servico']) for i in it if i['tipo'] == 'Tratamento' and i['nivel'].startswith(OK)]
    exa = [nm(i['servico']) for i in it if i['tipo'] == 'Diagnóstico' and i['nivel'].startswith(OK)]
    duv = [nm(i['servico']) + (' (frase com negação/causa)' if i['nivel'].startswith('Revisar') else ' (apenas citado)') for i in it if not i['nivel'].startswith(OK)]
    r = n + 1
    ws.append([n, d['doenca'], '\n'.join(trat) or '—', '\n'.join(exa) or '—', '\n'.join(duv) or '—', '\n'.join(d['sem_correspondencia']) or '—',
               None, None, None, None, f'=IF(AND(C{r}="—",D{r}="—"),"Não","Sim")', 'abrir'])
    ws.cell(row=r, column=12).hyperlink = SITE + slug(d['doenca']) + '.html'
last = ws.max_row
for row in ws.iter_rows(min_row=1, max_row=last):
    for c in row:
        c.font = base; c.alignment = wrap; c.border = box
        if c.row == 1:
            c.font = hfont; c.fill = hfill; c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        elif 7 <= c.column <= 10:
            c.fill = yel
        elif c.column in (1, 11, 12):
            c.alignment = Alignment(horizontal='center', vertical='top')
    if row[0].row > 1:
        row[1].font = bold; row[11].font = Font(name=F, size=10, color='0563C1', underline='single')
ws.row_dimensions[1].height = 42; ws.freeze_panes = 'C2'
ws.auto_filter.ref = f'A1:L{last}'
dv = DataValidation(type='list', formula1='"Sim,Não,Com ajustes"', allow_blank=True); dv.error = 'Escolha Sim, Não ou Com ajustes'; ws.add_data_validation(dv); dv.add(f'G2:G{last}')
ws.page_setup.orientation = 'landscape'; ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.print_title_rows = '1:1'; ws.print_area = f'A1:J{last}'
ws.oddFooter.center.text = 'Skin Prime · revisão médica doenças × tratamentos · página &P de &N'
ws.page_margins.left = ws.page_margins.right = .4; ws.page_margins.top = ws.page_margins.bottom = .5

# ------------------------------------------------------------ Modalidades a confirmar
w2 = wb.create_sheet('Modalidades a confirmar')
mods = {}
for d in J:
    for g in d['sem_correspondencia']:
        mods.setdefault(g, []).append(d['doenca'])
w2.append(['Modalidade citada nos textos das doenças', 'Nº de doenças', 'Doenças em que é citada', 'A clínica oferece? (Sim / Não)', 'Observações'])
for i, (m, ds) in enumerate(sorted(mods.items(), key=lambda x: -len(x[1])), 2):
    w2.append([m, f'=LEN(C{i})-LEN(SUBSTITUTE(C{i},";",""))+1', '; '.join(ds), None, None])
for i, w in enumerate([38, 10, 90, 16, 36], 1):
    w2.column_dimensions[get_column_letter(i)].width = w
for row in w2.iter_rows():
    for c in row:
        c.font = base; c.alignment = wrap; c.border = box
        if c.row == 1:
            c.font = hfont; c.fill = hfill
        elif c.column >= 4:
            c.fill = yel
dv2 = DataValidation(type='list', formula1='"Sim,Não"', allow_blank=True); w2.add_data_validation(dv2); dv2.add(f'D2:D{w2.max_row}')
w2.freeze_panes = 'A2'; w2.page_setup.orientation = 'landscape'; w2.page_setup.fitToWidth = 1; w2.page_setup.fitToHeight = 0; w2.sheet_properties.pageSetUpPr.fitToPage = True

# ------------------------------------------------------------ Trechos de apoio
w3 = wb.create_sheet('Trechos de apoio')
w3.append(['Doença', 'Serviço da clínica', 'Tipo', 'Situação', 'Publicado no site?', 'Trecho do texto da doença'])
for d in J:
    for i in d['itens']:
        w3.append([d['doenca'], nm(i['servico']), i['tipo'], i['nivel'], 'Sim' if i['nivel'].startswith(OK) else 'Não', i['trecho']])
for i, w in enumerate([28, 32, 12, 28, 10, 100], 1):
    w3.column_dimensions[get_column_letter(i)].width = w
for row in w3.iter_rows():
    for c in row:
        c.font = base; c.alignment = wrap
        if c.row == 1:
            c.font = hfont; c.fill = hfill
w3.freeze_panes = 'B2'; w3.auto_filter.ref = f'A1:F{w3.max_row}'
wb.save(sys.argv[1])
print('ok', len(J), 'doencas ·', len(mods), 'modalidades a confirmar ·', w3.max_row - 1, 'trechos')
