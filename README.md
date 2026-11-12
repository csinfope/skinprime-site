# Skin Prime — site

Site estático da clínica Skin Prime (Recife), publicado no GitHub Pages.

## Painel administrativo

Endereço: **https://csinfope.github.io/skinprime-site/admin/**

No painel dá para editar, sem programar:

- **Configurações do site:** textos da abertura, telefone, WhatsApp, e-mail, endereço, mapa, CNPJ, redes sociais, link da revista e cores.
- **Fotos dos ambientes da clínica:** incluir, remover, reordenar e legendar.
- **Doenças:** criar, editar e excluir; texto, bibliografia, imagens do atlas e os tratamentos/exames da clínica para cada doença.
- **Tratamentos e News:** criar, editar e excluir publicações, com capa, categorias e texto.
- **Equipe:** incluir, editar, remover e ordenar profissionais, com foto e perfil.

Cada vez que você salva, o painel grava a alteração no repositório e o site é atualizado sozinho em 1 a 3 minutos
(acompanhe em *Actions* no GitHub).

### Como entrar

1. No GitHub, crie um token: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   - *Repository access:* **Only select repositories** → `csinfope/skinprime-site`.
   - *Permissions → Repository permissions → Contents:* **Read and write**.
   - Guarde o token num lugar seguro; ele funciona como uma senha.
2. Abra o painel e clique em **Entrar Usando Token de Acesso** (*Sign In Using Access Token*). Cole o token.
3. O botão “Entrar com GitHub” **não** funciona nesta configuração; use sempre o token.

## Como o site é gerado

- `content/` — todo o conteúdo editável (JSON). É o que o painel altera.
- `build/build.py` — gera as páginas em `site/` a partir de `content/`.
- `build/optimize_images.py` — reduz imagens grandes e cria miniaturas antes de gerar.
- `build/gen_admin.py` — gera a configuração do painel (`site/admin/config.yml`).
- `site/admin/` — o painel (Sveltia CMS 0.253.1, código em `site/admin/vendor/`).
- `.github/workflows/pages.yml` — publica a cada alteração na branch `main`.

Para gerar localmente: `pip install markdown pillow`, depois `python3 build/build.py` e `cd site && python3 -m http.server 8000`.
