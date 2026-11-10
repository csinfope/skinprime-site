# Gera uma versão leve do site para pré-visualização online (miniaturas do atlas embutidas).
import os,re,glob,base64,io,json,shutil
from PIL import Image
SRC='site'; OUT='preview-artifact'
os.makedirs(OUT,exist_ok=True)
cache={}
def thumb(n):
    if n not in cache:
        im=Image.open(f'{SRC}/assets/img/atlas/{n}.jpg').convert('RGB'); im.thumbnail((150,150))
        b=io.BytesIO(); im.save(b,'JPEG',quality=58,optimize=True)
        cache[n]='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
    return cache[n]
files={}
for f in glob.glob(SRC+'/**/*.html',recursive=True):
    rel=os.path.relpath(f,SRC)
    if rel=='404.html': continue
    s=open(f,encoding='utf-8').read()
    s=re.sub(r'<a href="\.\./assets/img/atlas/[^"]+\.jpg" data-lb="atlas" data-alt="[^"]*">','<a>',s)
    s=re.sub(r'src="\.\./assets/img/atlas/([^"]+)\.jpg"',lambda m:'src="%s"'%thumb(m.group(1)),s)
    s=re.sub(r'(assets/img/posts/[0-9a-f]+)\.jpg',r'\1-m.jpg',s)
    s=re.sub(r'(assets/img/clinic/[a-z-]+?)(-m)?\.jpg',r'\1-m.jpg',s)
    if rel=='index.html':
        head=re.search(r'<title>.*?</title>',s,re.S).group(0)
        body=re.search(r'<body>(.*)</body>',s,re.S).group(1)
        s='<title>Skin Prime</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<script>document.documentElement.className="js"</script>\n<link rel="stylesheet" href="assets/css/site.css">\n'+body
    os.makedirs(os.path.dirname(f'{OUT}/{rel}') or OUT,exist_ok=True)
    open(f'{OUT}/{rel}','w',encoding='utf-8').write(s)
    if rel!='index.html': files[rel]=rel
keep=glob.glob(SRC+'/assets/css/*')+glob.glob(SRC+'/assets/js/*')+glob.glob(SRC+'/assets/fonts/*')+glob.glob(SRC+'/assets/img/brand/*')+glob.glob(SRC+'/assets/img/team/*')+glob.glob(SRC+'/assets/img/clinic/*-m.jpg')+glob.glob(SRC+'/assets/img/posts/*-m.jpg')
for f in keep:
    rel=os.path.relpath(f,SRC); os.makedirs(os.path.dirname(f'{OUT}/{rel}'),exist_ok=True); shutil.copy(f,f'{OUT}/{rel}'); files[rel]=rel
ks=sorted(files, key=lambda k:(k.endswith('.html'),k))
json.dump([dict((k,k) for k in ks[i:i+240]) for i in range(0,len(ks),240)],open(OUT+'/_batches.json','w'))
print(len(files), [len(b) for b in json.load(open(OUT+'/_batches.json'))])
