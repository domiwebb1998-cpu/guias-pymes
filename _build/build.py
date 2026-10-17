#!/usr/bin/env python3
"""Generador estático de Pyme al Día.

Uso:  python3 _build/build.py
Lee _build/config.json, _build/guias/*.html y _build/paginas/*.html
y escribe el sitio publicable en la raíz del repositorio.
"""
import html
import json
import re
import shutil
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_build"
CFG = json.loads((SRC / "config.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def fecha(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} de {MESES[m - 1]} de {y}"


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"Falta el encabezado --- en {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["body"] = m.group(2).strip()
    meta.setdefault("updated", meta.get("date"))
    meta["sources_list"] = []
    for item in meta.get("sources", "").split(";;"):
        if "|" in item:
            t, u = item.split("|", 1)
            meta["sources_list"].append((t.strip(), u.strip()))
    return meta


def add_heading_ids(body):
    toc = []

    def repl(m):
        text = re.sub(r"<[^>]+>", "", m.group(2))
        hid = slugify(text)[:60]
        toc.append((hid, text))
        return f'<h2 id="{hid}"{m.group(1)}>{m.group(2)}</h2>'

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, body, flags=re.S)
    return body, toc


def words(body):
    return len(re.sub(r"<[^>]+>", " ", body).split())


CSS_VERSION = "1"


def layout(title, description, canonical, content, *, kind="website",
           extra_head="", noindex=False):
    full_title = title if title == CFG["site_name"] else f"{title} | {CFG['site_name']}"
    cats = "".join(
        f'<a href="/categoria/{k}/">{html.escape(v)}</a>'
        for k, v in CFG["categories"].items())
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="{CFG['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{CFG['site_name']}">
<meta property="og:locale" content="es_CO">
<meta name="google-adsense-account" content="{CFG['adsense_client']}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/estilos.css?v={CSS_VERSION}">
<link rel="alternate" type="application/rss+xml" title="{CFG['site_name']}" href="/feed.xml">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CFG['adsense_client']}" crossorigin="anonymous"></script>
{extra_head}
</head>
<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="/"><span class="brand-mark">PD</span><span><strong>{CFG['site_name']}</strong><small>{CFG['tagline']}</small></span></a>
    <nav class="main-nav" aria-label="Principal">
      <a href="/guias/">Guías</a>
      <a href="/herramientas/">Herramientas</a>
      <a href="/quienes-somos/">Quiénes somos</a>
      <a href="/contacto/">Contacto</a>
    </nav>
  </div>
  <div class="cat-bar"><div class="wrap cat-scroll">{cats}</div></div>
</header>
<main id="contenido">
{content}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-brand">{CFG['site_name']}</p>
      <p>Guías gratuitas y en lenguaje sencillo para emprendedores, independientes y pequeñas empresas en Colombia.</p>
      <p class="small">El contenido es informativo y no reemplaza la asesoría de un contador, abogado o asesor financiero.</p>
    </div>
    <div>
      <p class="footer-title">Explorar</p>
      <a href="/guias/">Todas las guías</a>
      <a href="/herramientas/">Herramientas gratuitas</a>
      <a href="/quienes-somos/">Quiénes somos</a>
      <a href="/politica-editorial/">Política editorial</a>
      <a href="/contacto/">Contacto</a>
    </div>
    <div>
      <p class="footer-title">Legal</p>
      <a href="/politica-de-privacidad/">Política de privacidad</a>
      <a href="/politica-de-cookies/">Política de cookies</a>
      <a href="/terminos-y-condiciones/">Términos y condiciones</a>
      <a href="/aviso-legal/">Aviso legal</a>
    </div>
  </div>
  <div class="wrap copyright">© {date.today().year} {CFG['site_name']} · Hecho en Colombia</div>
</footer>
</body>
</html>
"""


def card(a, cats):
    return f"""<article class="card">
  <a class="card-cat" href="/categoria/{a['category']}/">{html.escape(cats[a['category']])}</a>
  <h3><a href="/guias/{a['slug']}/">{html.escape(a['title'])}</a></h3>
  <p>{html.escape(a['description'])}</p>
  <p class="meta">{fecha(a['date'])} · {a['reading']} min de lectura</p>
</article>"""


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def build():
    cats = CFG["categories"]
    articles = []
    for p in sorted((SRC / "guias").glob("*.html")):
        a = parse(p)
        for key in ("title", "slug", "description", "category", "date"):
            if not a.get(key):
                raise SystemExit(f"{p.name}: falta '{key}'")
        if a["category"] not in cats:
            raise SystemExit(f"{p.name}: categoría desconocida {a['category']}")
        if a["date"] > date.today().isoformat():
            continue  # programado para el futuro
        a["body"], a["toc"] = add_heading_ids(a["body"])
        a["words"] = words(a["body"])
        a["reading"] = max(3, round(a["words"] / 220))
        articles.append(a)
    articles.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)

    # Limpia salidas generadas anteriores
    for d in ("guias", "categoria"):
        shutil.rmtree(ROOT / d, ignore_errors=True)

    # Artículos
    for a in articles:
        url = f"{BASE}/guias/{a['slug']}/"
        related = [x for x in articles if x["slug"] != a["slug"] and x["category"] == a["category"]]
        related += [x for x in articles if x["slug"] != a["slug"] and x not in related]
        toc = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in a["toc"])
        sources = ""
        if a["sources_list"]:
            items = "".join(
                f'<li><a href="{html.escape(u)}" rel="noopener" target="_blank">{html.escape(t)}</a></li>'
                for t, u in a["sources_list"])
            sources = f'<section class="sources"><h2>Fuentes consultadas</h2><ul>{items}</ul></section>'
        upd = ""
        if a["updated"] != a["date"]:
            upd = f' · Actualizada el {fecha(a["updated"])}'
        schema = {
            "@context": "https://schema.org", "@type": "Article",
            "headline": a["title"], "description": a["description"],
            "datePublished": a["date"], "dateModified": a["updated"],
            "inLanguage": "es-CO", "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": f"Equipo editorial de {CFG['site_name']}", "url": f"{BASE}/quienes-somos/"},
            "publisher": {"@type": "Organization", "name": CFG["site_name"], "url": BASE + "/"},
        }
        crumbs = {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": cats[a["category"]], "item": f"{BASE}/categoria/{a['category']}/"},
                {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
            ]}
        head = (f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n'
                f'<script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>')
        rel_cards = "".join(card(x, cats) for x in related[:3])
        content = f"""<div class="wrap article-layout">
<article class="article">
  <nav class="crumbs" aria-label="Ruta"><a href="/">Inicio</a> / <a href="/categoria/{a['category']}/">{html.escape(cats[a['category']])}</a></nav>
  <h1>{html.escape(a['title'])}</h1>
  <p class="lead">{html.escape(a['description'])}</p>
  <p class="meta">Por el equipo editorial de {CFG['site_name']} · {fecha(a['date'])}{upd} · {a['reading']} min de lectura</p>
  <details class="toc" open><summary>En esta guía</summary><ol>{toc}</ol></details>
  <div class="prose">
{a['body']}
  </div>
  {sources}
  <aside class="disclaimer">Esta guía es informativa y se basa en la normativa y las fuentes vigentes en la fecha de publicación. Las normas cambian: antes de tomar una decisión tributaria, laboral o legal, confírmala con la fuente oficial o con un profesional.</aside>
</article>
</div>
<section class="wrap related"><h2>Sigue leyendo</h2><div class="grid">{rel_cards}</div></section>"""
        write(f"guias/{a['slug']}/index.html",
              layout(a["title"], a["description"], url, content, kind="article", extra_head=head))

    # Listado de guías
    allcards = "".join(card(a, cats) for a in articles)
    write("guias/index.html", layout(
        "Todas las guías", "Guías prácticas sobre finanzas, impuestos, trámites, ventas y operación para pymes en Colombia.",
        f"{BASE}/guias/",
        f'<section class="wrap page-head"><h1>Todas las guías</h1><p>{len(articles)} guías publicadas, de la más reciente a la más antigua.</p></section><section class="wrap grid">{allcards}</section>'))

    # Categorías
    for k, v in cats.items():
        items = [a for a in articles if a["category"] == k]
        body = "".join(card(a, cats) for a in items) or '<p class="empty">Muy pronto publicaremos guías en esta sección.</p>'
        write(f"categoria/{k}/index.html", layout(
            v, f"Guías de {v.lower()} para pequeños negocios en Colombia.", f"{BASE}/categoria/{k}/",
            f'<section class="wrap page-head"><p class="eyebrow">Categoría</p><h1>{html.escape(v)}</h1></section><section class="wrap grid">{body}</section>',
            noindex=not items))

    # Portada
    featured = articles[0] if articles else None
    hero_card = ""
    if featured:
        hero_card = f"""<a class="feature" href="/guias/{featured['slug']}/">
  <span class="card-cat">{html.escape(cats[featured['category']])} · Nueva</span>
  <span class="feature-title">{html.escape(featured['title'])}</span>
  <span class="feature-desc">{html.escape(featured['description'])}</span>
  <span class="feature-link">Leer la guía →</span></a>"""
    def n_guias(k):
        n = sum(1 for a in articles if a["category"] == k)
        return "Próximamente" if n == 0 else ("1 guía" if n == 1 else f"{n} guías")
    cat_tiles = "".join(
        f'<a class="tile" href="/categoria/{k}/"><strong>{html.escape(v)}</strong><span>{n_guias(k)}</span></a>'
        for k, v in cats.items())
    latest = "".join(card(a, cats) for a in articles[1:7])
    home = f"""<section class="hero"><div class="wrap hero-grid">
  <div>
    <p class="eyebrow">Para emprendedores y pymes en Colombia</p>
    <h1>Lo que necesitas saber para manejar tu negocio, explicado sin rodeos.</h1>
    <p class="lead">Costos, precios, impuestos, trámites y herramientas: guías paso a paso con ejemplos en pesos colombianos y enlaces a las fuentes oficiales.</p>
    <a class="btn" href="/guias/">Ver todas las guías</a>
  </div>
  {hero_card}
</div></section>
<section class="wrap"><h2 class="section-title">Explora por tema</h2><div class="tiles">{cat_tiles}</div></section>
<section class="wrap"><h2 class="section-title">Guías recientes</h2><div class="grid">{latest}</div></section>"""
    write("index.html", layout(CFG["site_name"],
          "Guías prácticas y gratuitas para emprendedores y pymes en Colombia: finanzas, impuestos, DIAN, trámites, ventas y herramientas.",
          BASE + "/", home))

    # Páginas estáticas
    pages = []
    for p in sorted((SRC / "paginas").glob("*.html")):
        pg = parse(p)
        pg["body"] = pg["body"].replace("{{EMAIL}}", CFG["contact_email"]).replace(
            "{{SITE}}", CFG["site_name"]).replace("{{BASE}}", BASE).replace("{{WHATSAPP}}", CFG["whatsapp"])
        url = f"{BASE}/{pg['slug']}/"
        upd = f'<p class="meta">Última actualización: {fecha(pg["updated"])}</p>' if pg.get("updated") else ""
        write(f"{pg['slug']}/index.html", layout(
            pg["title"], pg["description"], url,
            f'<div class="wrap narrow page"><h1>{html.escape(pg["title"])}</h1>{upd}<div class="prose">{pg["body"]}</div></div>',
            extra_head=pg.get("head", "")))
        pages.append(pg)

    # 404
    write("404.html", layout("Página no encontrada", "La página que buscas no existe.", BASE + "/404.html",
          '<div class="wrap narrow page"><h1>No encontramos esta página</h1><p>Puede que la guía haya cambiado de dirección. <a href="/guias/">Ver todas las guías</a>.</p></div>',
          noindex=True))

    # sitemap
    urls = [(BASE + "/", articles[0]["updated"] if articles else date.today().isoformat()),
            (BASE + "/guias/", articles[0]["updated"] if articles else date.today().isoformat())]
    urls += [(f"{BASE}/guias/{a['slug']}/", a["updated"]) for a in articles]
    urls += [(f"{BASE}/categoria/{k}/", None) for k in cats if any(a["category"] == k for a in articles)]
    urls += [(f"{BASE}/{pg['slug']}/", pg.get("updated")) for pg in pages]
    sm = "".join(f"<url><loc>{u}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')

    # RSS
    items = "".join(
        f"<item><title>{html.escape(a['title'])}</title><link>{BASE}/guias/{a['slug']}/</link>"
        f"<guid>{BASE}/guias/{a['slug']}/</guid><pubDate>{a['date']}</pubDate>"
        f"<description>{html.escape(a['description'])}</description></item>" for a in articles[:20])
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{CFG["site_name"]}</title>'
          f'<link>{BASE}/</link><description>{CFG["tagline"]}</description><language>es-co</language>{items}</channel></rss>\n')

    write("robots.txt", f"User-agent: *\nDisallow: /_build/\nSitemap: {BASE}/sitemap.xml\n")
    pub = CFG["adsense_client"].replace("ca-", "")
    write("ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")

    total = sum(a["words"] for a in articles)
    print(f"OK: {len(articles)} guías ({total} palabras), {len(pages)} páginas, {len(urls)} URLs en sitemap")


if __name__ == "__main__":
    build()
