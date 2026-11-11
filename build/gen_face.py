#!/usr/bin/env python3
"""Gera o rosto 3D do fundo animado: site/assets/js/face.js + site/assets/img/brand/face.webp

Entrada: foto frontal de rosto (fundo claro) e os pontos 3D do rosto (MediaPipe FaceMesh) em JSON.
Saída:
  - face.webp: recorte da foto com fundo transparente;
  - face.js: (1) relevo 3D da foto em grade, com o deslocamento do estado "antes" (terço inferior mais
    pesado); (2) duas nuvens de pontos sobre a malha facial (antes/depois) para as partículas.

Uso: python3 build/gen_face.py FOTO.jpg PONTOS.json [previa.png]
"""
import sys, json, base64
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

N, GX, GY, SC = 15000, 84, 96, 8000
rng = np.random.default_rng(7)
img = Image.open(sys.argv[1]).convert('RGB')
lm = json.load(open(sys.argv[2]))
W, H = img.size
rgb = np.asarray(img, dtype=np.float32) / 255
P = np.array(lm['lm'], dtype=np.float64)[:468]
X, Y, D = P[:, 0] * W, P[:, 1] * H, -P[:, 2] * W          # D positivo = mais perto da câmera
top_y, chin_y = Y[10], Y[152]; fh = chin_y - top_y; fw = X.max() - X.min()
cx, cy = (X.max() + X.min()) / 2, (top_y + chin_y) / 2
k = 1.3 / fh                                              # unidades do motor por pixel
YOFF = .1

# recorte e transparência
x0 = int(max(0, cx - fw * 1.02)); x1 = int(min(W, cx + fw * 1.02))
y0 = int(max(0, top_y - fh * .5)); y1 = int(min(H, chin_y + fh * .62))
white = rgb.min(axis=2) > .93
lab, _ = ndimage.label(white)
el = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
sizes = ndimage.sum(white, lab, index=np.arange(lab.max() + 1))
bgm = np.isin(lab, list(el)) | (white & (sizes[lab] > 120))          # inclui vãos brancos entre os dedos
bgm = ndimage.binary_dilation(bgm, iterations=2)
fg = ndimage.gaussian_filter((~bgm).astype(np.float32), 2.2)
fg = np.clip((fg - .35) / .5, 0, 1)
yy, xx = np.mgrid[0:H, 0:W]
fade = np.clip((chin_y + fh * .5 - yy) / (fh * .34), 0, 1) ** 1.4                      # some para baixo (colo)
fade *= np.clip((xx - x0) / (fw * .16), 0, 1) * np.clip((x1 - xx) / (fw * .16), 0, 1)
fade *= np.clip((yy - y0) / (fh * .17), 0, 1)
alpha = ndimage.gaussian_filter(fg, 2.5) * fg * fade
crop = np.dstack([rgb, alpha])[y0:y1, x0:x1]
tex = Image.fromarray((crop * 255).astype(np.uint8), 'RGBA')
tw = 720; tex = tex.resize((tw, round(tw * crop.shape[0] / crop.shape[1])), Image.LANCZOS)
tex.save('site/assets/img/brand/face.webp', quality=86, method=6)

# profundidade em toda a imagem
lin = LinearNDInterpolator(np.c_[X, Y], D)
depth = lin(xx, yy); inside = ~np.isnan(depth)
near = NearestNDInterpolator(np.c_[X, Y], D)(xx, yy)
dist = ndimage.distance_transform_edt(~inside)
outd = near - np.minimum(dist * .38, fw * .26)
depth = ndimage.gaussian_filter(np.where(inside, depth, outd), 5)
z0 = np.percentile(D, 55)

ym = -(Y[13] - cy) * k + YOFF; yc = -(chin_y - cy) * k + YOFF; yb = -(Y[105] - cy) * k + YOFF; hw = fw * k / 2
gs = lambda v, c, s: np.exp(-((v - c) / s) ** 2)

def before(B):
    """Deslocamento do estado 'antes' para pontos B (n,3)."""
    x, y = B[:, 0], B[:, 1]; d = np.zeros_like(B)
    jowl = gs(np.abs(x), hw * .66, hw * .3) * gs(y, yc + (ym - yc) * .4, (ym - yc) * .95)
    d[:, 1] -= .075 * jowl; d[:, 0] += x * .1 * jowl; d[:, 2] += .03 * jowl
    sub = gs(x, 0, hw * .7) * gs(y, yc - .07, .09)                        # papada
    d[:, 1] -= .055 * sub; d[:, 2] += .04 * sub
    cheek = gs(np.abs(x), hw * .55, hw * .3) * gs(y, (ym + yb) / 2 + .04, .16)
    d[:, 2] -= .035 * cheek; d[:, 1] -= .028 * cheek
    brow = gs(y, yb, .1) * gs(np.abs(x), hw * .5, hw * .5)
    d[:, 1] -= .026 * brow
    return d

def to3d(px, py, pz):
    return np.c_[(px - cx) * k, -(py - cy) * k + YOFF, (pz - z0) * k * 1.1]

# 1) grade do relevo da foto
gx = np.linspace(x0, x1 - 1, GX); gy = np.linspace(y0, y1 - 1, GY)
GXX, GYY = np.meshgrid(gx, gy)
gz = depth[GYY.astype(int), GXX.astype(int)]
G = to3d(GXX.ravel(), GYY.ravel(), gz.ravel()); Gd = before(G)
grid = np.c_[G, Gd]

# 2) partículas sobre a malha facial: arestas da tesselação + contorno do rosto reforçado
tess = np.array(lm['tess']); tess = np.unique(np.sort(tess, axis=1), axis=0)
oval = np.array(lm['oval'])
L3 = to3d(X, Y, D)
def sample(edges, n):
    a, b = L3[edges[:, 0]], L3[edges[:, 1]]
    ln = np.linalg.norm(a - b, axis=1); e = rng.choice(len(edges), size=n, p=ln / ln.sum())
    t = rng.random(n)[:, None]
    return a[e] * (1 - t) + b[e] * t
nv = int(N * .06); no = int(N * .2); ne = int(N * .34); nr = N - nv - no - ne
verts = L3[rng.integers(0, 468, nv)] + rng.normal(0, .003, (nv, 3))
face_pts = np.vstack([sample(tess, ne), sample(oval, no) + rng.normal(0, .004, (no, 3)), verts])
face_pts[:, 2] += .012                                                   # levemente à frente da foto
# órbitas de escaneamento ao redor da cabeça (não cobrem o rosto)
th = rng.random(nr) * 2 * np.pi; ring = rng.integers(0, 3, nr)
rad = np.array([1.02, 1.16, 1.3])[ring] + rng.normal(0, .006, nr)
tilt = np.array([.18, -.3, .5])[ring]; hgt = np.array([.42, -.02, -.5])[ring]
rx_, rz_ = rad * np.cos(th), rad * np.sin(th)
orb = np.c_[rx_, hgt + rx_ * np.sin(tilt) * .5 + rng.normal(0, .004, nr), rz_ - .35]
B = np.vstack([face_pts, orb])
A = B + np.vstack([before(face_pts), np.zeros((nr, 3))])
perm = rng.permutation(N); A, B = A[perm], B[perm]

enc = lambda a: base64.b64encode(np.clip(np.round(a * SC), -32767, 32767).astype('<i2').tobytes()).decode()
open('site/assets/js/face.js', 'w').write(
    '/* gerado por build/gen_face.py */\nwindow.SPFACE={n:%d,s:%d,a:"%s",b:"%s",gx:%d,gy:%d,g:"%s",tex:"assets/img/brand/face.webp"};\n'
    % (N, SC, enc(A), enc(B), GX, GY, enc(grid)))
# pontos do mapa facial interativo (índices do MediaPipe FaceMesh)
PTS = {'testa': 151, 'olhos': 450, 'macas': 205, 'labios': 13, 'mandibula': 397, 'papada': 152}
pts = {}
for kname, ix in PTS.items():
    v = L3[ix].copy(); v[2] += .03
    if kname == 'papada':
        v[1] -= .09
    pts[kname] = [round(float(t), 4) for t in v]
_f = open('site/assets/js/face.js', encoding='utf-8').read().replace('tex:"assets/img/brand/face.webp"}', 'tex:"assets/img/brand/face.webp",pts:' + json.dumps(pts) + '}')
open('site/assets/js/face.js', 'w', encoding='utf-8').write(_f)
print('face.js ok · textura', tex.size, '· recorte', (x0, y0, x1, y1))

if len(sys.argv) > 3:
    def render(Pts, off, yaw=0, col=(111, 227, 240)):
        c, s = np.cos(yaw), np.sin(yaw)
        xr = Pts[:, 0] * c + Pts[:, 2] * s; zr = -Pts[:, 0] * s + Pts[:, 2] * c
        z = 3.2 - zr; u = (xr / z * 2.1 * 330 + 300).astype(int); v = (330 - Pts[:, 1] / z * 2.1 * 330).astype(int)
        return u, v
    sheet = Image.new('RGB', (1800, 700), (3, 8, 10))
    S = 330 * 2.1 / 3.2
    for i, (st, yaw) in enumerate([(1, 0), (0, 0), (1, .4)]):
        can = Image.new('RGB', (600, 700), (3, 8, 10))
        GG = G + Gd * (1 - st)
        u, v = render(GG, 0, yaw)
        # textura deformada (aproximação por pontos da grade, só para conferência)
        tw_, th_ = tex.size; ta = np.asarray(tex).astype(np.float32) / 255
        dense = Image.new('RGB', (600, 700), (3, 8, 10)); dp = np.asarray(dense).astype(np.float32) / 255
        uu = np.linspace(0, GX - 1, tw_); vv = np.linspace(0, GY - 1, th_)
        from scipy.ndimage import map_coordinates
        UU, VV = np.meshgrid(uu, vv)
        U2 = map_coordinates(u.reshape(GY, GX).astype(float), [VV, UU], order=1)
        V2 = map_coordinates(v.reshape(GY, GX).astype(float), [VV, UU], order=1)
        ui = np.clip(U2.astype(int), 0, 599); vi = np.clip(V2.astype(int), 0, 699)
        dp[vi, ui] = dp[vi, ui] * (1 - ta[..., 3:4]) + ta[..., :3] * ta[..., 3:4]
        can = Image.fromarray((dp * 255).astype(np.uint8))
        arr = np.asarray(can).astype(np.float32)
        PT = A if st == 0 else B
        pu, pv = render(PT, 0, yaw); ok = (pu > 0) & (pu < 599) & (pv > 0) & (pv < 699)
        add = np.zeros((700, 600), np.float32); np.add.at(add, (pv[ok], pu[ok]), .5)
        add = np.clip(ndimage.gaussian_filter(add, .6) * 1.6, 0, 1)[..., None]
        arr = np.clip(arr + add * np.array([111, 227, 240], np.float32), 0, 255)
        sheet.paste(Image.fromarray(arr.astype(np.uint8)), (i * 600, 0))
    sheet.save(sys.argv[3])
