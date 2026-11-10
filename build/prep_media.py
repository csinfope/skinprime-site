# Otimiza imagens do blog e do atlas. uso: prep_media.py <postimg_dir> <dimg_dir>
import sys,os,glob
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
OUT='site/assets/img'
def one(a):
    f,dst,mx=a
    if os.path.exists(dst): return 1
    try:
        im=Image.open(f); im.load()
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); im=bg
        im=im.convert('RGB'); im.thumbnail((mx,mx),Image.LANCZOS)
        im.save(dst,quality=80,optimize=True,progressive=True); return 1
    except Exception as e:
        print('ERR',f,e); return 0
def name(f): return os.path.basename(f).split('.')[0].replace('_mv2','').replace('96b8be_','')
jobs=[]
for f in glob.glob(sys.argv[1]+'/*'):
    jobs.append((f,f'{OUT}/posts/{name(f)}.jpg',1280)); jobs.append((f,f'{OUT}/posts/{name(f)}-m.jpg',640))
for f in glob.glob(sys.argv[2]+'/*'):
    jobs.append((f,f'{OUT}/atlas/{name(f)}.jpg',1000))
if __name__=='__main__':
    with ProcessPoolExecutor(4) as ex: r=list(ex.map(one,jobs,chunksize=20))
    print(sum(r),len(jobs))
