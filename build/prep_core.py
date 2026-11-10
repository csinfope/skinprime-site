# Prepara imagens principais (logo, clínica, equipe) a partir dos originais baixados.
import sys,os
from PIL import Image,ImageOps
SRC=sys.argv[1]; OUT='site/assets/img'
def p(i,ext): return f'{SRC}/96b8be_{i}.{ext}'
# logo -> versões clara e teal (usa o canal alpha)
lg=Image.open(p('73a1bcac7e964365954ca8e00ba82919','png')).convert('RGBA')
bb=lg.getchannel('A').getbbox(); lg=lg.crop(bb); a=lg.getchannel('A')
# normaliza alpha (o original é semi-transparente)
mx=max(a.getdata()); a=a.point(lambda v:min(255,int(v*255/mx)))
for name,col in [('logo-bone',(236,231,222)),('logo-ink',(16,38,42))]:
    im=Image.new('RGBA',lg.size,col+(0,)); im.putalpha(a); im.save(f'{OUT}/brand/{name}.png')
print('logo',lg.size,mx)
clinic=['428d9781c00c432b9c094a71f1dfe294','3917f76c4ea44477acfa5ecbe5ed470d','9b5c3b60dcaa4d23b8d226451fc0493d','2e7f53ff0eeb43e9b5002464ee59dd2e','b29f7f622cf544b9837cebe51cbc623a','1fc87c6de8c141fa852b50779600591e','df1f6b5828e5496d967bc1ebc7017400','f4939297c6304bba9589268c2a713bd1','ce6961b3aaba446da89760d8414bab4b','fd2e3715bbe4457383dc3ba3202f4bd3']
names=['vista','lounge','recepcao','espera','cafe','consultorio','sala-laser','sala-procedimentos','capilar','detalhe']
for i,n in zip(clinic,names):
    im=Image.open(p(i,'jpg')).convert('RGB')
    for w,suf in [(1800,''),(900,'-m')]:
        t=im.copy(); t.thumbnail((w,w)); t.save(f'{OUT}/clinic/{n}{suf}.jpg',quality=80,optimize=True,progressive=True)
im=Image.open(p('6c4f6eab69cc4146ba366f1fa32ea8c1f000','jpg')).convert('RGB'); im.save(f'{OUT}/brand/hero.jpg',quality=84,progressive=True)
im=Image.open(p('a6bd033ad4274c729dc89867c34d680e','png')).convert('RGB'); im.save(f'{OUT}/brand/maos.jpg',quality=86)
im=Image.open(p('f735af4e967846a7a1f07484f7db408f','png')); im=im.crop(im.getchannel('A').getbbox()); im.save(f'{OUT}/team/equipe.webp',quality=88)
im=Image.open(p('dceeca6f26c64469bac62b0bfe311837','png')); im=im.crop(im.getchannel('A').getbbox()); im.thumbnail((1400,1400)); im.save(f'{OUT}/brand/revista.webp',quality=88)
# retratos: (arquivo, cx, cy, r)
team=[('emmanuel','2d3f20aa9ed5411c8310e384c082f39a',None),('francisco','22ca66a7f9c44626808721505dff7009',None),('daniela','b2b59e30255c4713a9d7dad7aefd57a1',None),
      ('yana','04f8693558eb46c686f03dc2a21b4a09',(518,572,255)),('andre','0cd17bffccea473c84b25a46a397737b',(590,572,255)),('aleksana','8b08308f557543a5af1e2e7bc15d9e5a',(518,572,255))]
for n,i,c in team:
    im=Image.open(p(i,'png')).convert('RGBA')
    if c is None:
        w,h=im.size; r=int(w*(0.40 if n=='daniela' else 0.335)); cx=w//2; cy=int(w*(0.47 if n=='daniela' else 0.465)); c=(cx,cy,r)
    cx,cy,r=c
    bg=Image.new('RGBA',im.size,(240,238,234,255)); bg.alpha_composite(im)
    t=bg.crop((cx-r,cy-r,cx+r,cy+r)).convert('RGB').resize((640,640),Image.LANCZOS); t.save(f'{OUT}/team/{n}.jpg',quality=86)
