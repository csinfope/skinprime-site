# Achata preview-artifact/ em preview-flat/ com nomes curtos (para publicação da prévia online).
import os,re,glob,posixpath,collections
SRC='preview-artifact'; OUT='preview-flat'; os.makedirs(OUT,exist_ok=True)
allf=sorted(f for f in (os.path.relpath(p,SRC) for p in glob.glob(SRC+'/**/*',recursive=True) if os.path.isfile(p)) if not os.path.basename(f).startswith('_'))
cnt=collections.Counter(); M={}
pre={'html':'p','jpg':'j','png':'g','webp':'b','svg':'v','woff2':'w','css':'c','js':'s'}
for f in allf:
    if f=='index.html': M[f]=f; continue
    e=f.rsplit('.',1)[1]; cnt[e]+=1; M[f]=f'{pre[e]}{cnt[e]}.{e}'
def fix(base):
    def r(m):
        a,x,z=m.group(1),m.group(2),m.group(3)
        if re.match(r'(https?:|mailto:|tel:|data:|#)',x): return m.group(0)
        path,sep,frag=re.match(r'([^#?]*)([#?]?)(.*)',x).groups()
        t=posixpath.normpath(posixpath.join(base,path))
        return a+M[t]+sep+frag+z if t in M else m.group(0)
    return r
for f in allf:
    b=open(f'{SRC}/{f}','rb').read()
    if f.endswith(('.html','.css')):
        s=b.decode('utf-8'); base=posixpath.dirname(f)
        s=re.sub(r'((?:href|src|action)=")([^"]*)(")',fix(base),s)
        s=re.sub(r'(url\()([^)"\']+)(\))',fix(base),s)
        b=s.encode('utf-8')
    open(f'{OUT}/{M[f]}','wb').write(b)
import json
open(f"{OUT}/{M['assets/js/data.js']}",'a',encoding='utf-8').write('\nwindow.SPMAP='+json.dumps(M,separators=(',',':'))+';')
print(dict(cnt)); print(M['assets/css/site.css'],M['assets/js/site.js'])
