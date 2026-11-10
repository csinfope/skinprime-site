# Skin Prime — site

Site estático (HTML/CSS/JS, sem dependências) da clínica Skin Prime, Recife.

- `site/` — o site pronto. É esta pasta que vai ao ar (GitHub Pages publica a cada alteração na branch `main`).
- `build/build.py` — gerador das páginas. Edite textos/equipe nele ou os dados em `build/data/*.json` e rode `python3 build/build.py`.
- `build/data/posts.json` — 88 publicações de Tratamentos/News. `build/data/doencas.json` — 214 doenças.
- `site/assets/js/fx.js` — partículas 3D; `tour.js` — tour 3D simulado dos ambientes; `site.js` — demais interações.

Pré-visualizar localmente:

    cd site && python3 -m http.server 8000

O formulário de contato abre o WhatsApp da clínica com a mensagem preenchida; não requer servidor.
