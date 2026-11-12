#!/usr/bin/env python3
"""Prepara as imagens enviadas pelo painel antes de gerar o site (roda na publicação automática).

- reduz fotos grandes (lado maior > 1800 px) para carregar rápido;
- cria versões menores "-m" das fotos de capa e da clínica, usadas nos cartões e no carrossel.
Só altera a cópia usada na publicação; os originais enviados continuam no repositório.
"""
import os, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'site', 'assets', 'img')
EXT = ('.jpg', '.jpeg', '.png', '.webp')
THUMB_DIRS = {'posts': 640, 'clinic': 900, 'uploads': 900}
MAX = 1800
changed = made = 0
for folder in ('uploads', 'posts', 'clinic', 'team', 'atlas'):
    base = os.path.join(IMG, folder)
    if not os.path.isdir(base):
        continue
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name)
        stem, ext = os.path.splitext(name)
        if ext.lower() not in EXT or stem.endswith('-m'):
            continue
        try:
            with Image.open(path) as im:
                w, h = im.size
                big = max(w, h) > MAX
                need_thumb = folder in THUMB_DIRS and not os.path.exists(os.path.join(base, stem + '-m' + ext))
                if not big and not need_thumb:
                    continue
                im = ImageOps.exif_transpose(im)
                if im.mode not in ('RGB', 'RGBA'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                fmt = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}[ext.lower()]
                opts = {'quality': 82, 'optimize': True} if fmt in ('JPEG', 'WEBP') else {'optimize': True}
                if fmt == 'JPEG' and im.mode == 'RGBA':
                    im = im.convert('RGB')
                if big:
                    im.thumbnail((MAX, MAX), Image.LANCZOS)
                    im.save(path, fmt, **opts); changed += 1
                if need_thumb:
                    t = im.copy(); t.thumbnail((THUMB_DIRS[folder], THUMB_DIRS[folder]), Image.LANCZOS)
                    t.save(os.path.join(base, stem + '-m' + ext), fmt, **opts); made += 1
        except Exception as e:  # imagem corrompida não deve impedir a publicação
            print('aviso: não consegui processar', path, '-', e, file=sys.stderr)
print(f'imagens reduzidas: {changed} · miniaturas criadas: {made}')
