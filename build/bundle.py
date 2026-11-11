# Empacota a prévia (preview-flat/) em UM único arquivo HTML navegável: preview-single/index.html
# As páginas ficam embutidas e são trocadas por um pequeno roteador; imagens viram data URIs.
import os, re, glob, json, base64, io
from PIL import Image

SRC = 'preview-flat'; OUT = 'preview-single'
os.makedirs(OUT, exist_ok=True)


def b64(data, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode())


assets = {}
for f in sorted(glob.glob(SRC + '/*')):
    n = os.path.basename(f); e = n.rsplit('.', 1)[-1]
    if e == 'jpg':
        im = Image.open(f).convert('RGB')
        big = im.size[0] >= 800          # fotos da clínica ficam maiores
        im.thumbnail((900, 900) if big else (420, 420))
        o = io.BytesIO(); im.save(o, 'JPEG', quality=72 if big else 68, optimize=True)
        assets[n] = b64(o.getvalue(), 'image/jpeg')
    elif e == 'png':
        assets[n] = b64(open(f, 'rb').read(), 'image/png')
    elif e == 'webp':
        im = Image.open(f); im.thumbnail((900, 900)); o = io.BytesIO(); im.save(o, 'WEBP', quality=80)
        assets[n] = b64(o.getvalue(), 'image/webp')
    elif e == 'woff2':
        assets[n] = b64(open(f, 'rb').read(), 'font/woff2')

css = open(SRC + '/c1.css', encoding='utf-8').read()
css = re.sub(r'url\((w\d\.woff2|j\d+\.jpg)\)', lambda m: 'url(%s)' % assets[m.group(1)], css)
JSN = sorted(os.path.basename(f) for f in glob.glob(SRC + '/s*.js'))
js = {n: open(f'{SRC}/{n}', encoding='utf-8').read() for n in JSN}
# no pacote único, os caminhos de imagem usados pelo JavaScript apontam direto para os data URIs
smap = json.loads(re.search(r'window\.SPMAP=(\{.*\});', js['s1.js'], re.S).group(1))
smap = {k: (assets.get(v, v)) for k, v in smap.items() if v.endswith('.html') or v in assets}
js['s1.js'] = re.sub(r'window\.SPMAP=\{.*\};', lambda m: 'window.SPMAP=' + json.dumps(smap, separators=(',', ':')) + ';', js['s1.js'], flags=re.S)

pages = {}
for f in glob.glob(SRC + '/*.html'):
    n = os.path.basename(f)[:-5]
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<body>(.*)</body>', s, re.S)
    body = m.group(1) if m else s[s.index('<canvas'):]
    t = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
    body = re.sub(r'<script src="s\d+\.js" defer></script>\s*', '', body)
    # miniaturas do atlas ficam fora do pacote único (pesariam mais de 10 MB)
    body = re.sub(r'<div class="gal">.*?</div>', '<p class="note">As imagens do atlas desta doença não foram incluídas nesta prévia leve; elas estão no site completo.</p>', body, flags=re.S)
    body = re.sub(r'<img src="data:image/jpeg[^"]*"', '<img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="', body)
    pages[n] = [t, body]

boot = r'''
(function(){
var A=__ASSETS__,P=__PAGES__,CSS=__CSS__,JS=__JS__;
function fill(h){return h.replace(/(src|href)="((?:j|g|b)\d+\.(?:jpg|png|webp))"/g,function(m,a,n){return A[n]?a+'="'+A[n]+'"':m});}
var NAV='<scr'+'ipt>(function(){document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("a[href]"):null;if(!a||a.target)return;var h=a.getAttribute("href");var m=/^(index|p\\d+)\\.html(?:\\?[^#]*)?(#.*)?$/.exec(h);if(!m)return;e.preventDefault();e.stopPropagation();window.SPGO(m[1],m[2]||"");},true);})();</scr'+'ipt>';
window.SPGO=function(n,frag){
  var p=P[n]||P.index;if(!P[n])n='index';
  try{history.replaceState(null,'','#'+n)}catch(e){}
  var skip='';try{if(sessionStorage.getItem('sp-boot'))skip=' skip-boot'}catch(e){}
  var h='<!doctype html><html lang="pt-BR" data-root="" class="js'+skip+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>'+p[0]+'</title><style>'+CSS+'</style></head><body>'+fill(p[1])+NAV+JS.map(function(x){return '<scr'+'ipt>'+x+'</scr'+'ipt>'}).join('')+'</body></html>';
  document.open();document.write(h);document.close();
  window.scrollTo(0,0);
  if(frag&&frag.length>1)setTimeout(function(){var el=document.getElementById(decodeURIComponent(frag.slice(1)));if(el)el.scrollIntoView();},400);
};
var start=(location.hash||'').slice(1);
window.SPGO(P[start]?start:'index','');
})();
'''


def J(o):
    return json.dumps(o, ensure_ascii=True, separators=(',', ':')).replace('</', '<\\/')


boot = (boot.replace('__ASSETS__', J(assets)).replace('__PAGES__', J(pages)).replace('__CSS__', J(css))
        .replace('__JS__', J([js[n] for n in JSN])))
html = ('<title>Skin Prime</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<style>:root{color-scheme:light}body{margin:0;background:#f7f7f7;color:#1d2b2d;font:300 16px system-ui,sans-serif;'
        'padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}</style>\n'
        '<p style="padding-block:40vh 0;text-align:center;letter-spacing:.2em;text-transform:uppercase;font-size:12px;color:#4a7079">Skin Prime · carregando</p>\n'
        '<script>' + boot + '</script>\n')
open(OUT + '/index.html', 'w', encoding='utf-8').write(html)
print('paginas:', len(pages), '· imagens:', len(assets), '· tamanho: %.1f MB' % (len(html.encode()) / 1e6))
