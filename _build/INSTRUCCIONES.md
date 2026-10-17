# Instrucciones para publicar una guía nueva

1. Abre `_build/TEMAS.md` y toma el primer tema en "Pendientes".
2. Investiga en fuentes primarias colombianas (dian.gov.co, cámaras de comercio, mintrabajo.gov.co, sic.gov.co, funcionpublica.gov.co, secretariasenado.gov.co). Verifica cada cifra, tope, plazo y nombre de norma vigente a la fecha de publicación. Si no puedes confirmar un dato, no lo publiques o preséntalo como verificable en la fuente oficial.
3. Escribe el archivo `_build/guias/AAAA-MM-DD-slug-corto.html` con este encabezado:

```
---
title: Título claro, con la palabra clave al inicio (máx. ~70 caracteres)
slug: slug-en-minusculas-sin-tildes
description: Resumen de 140–160 caracteres que diga qué aprenderá el lector.
category: una de: finanzas, impuestos, formalizacion, ventas, operacion, legal, digital
date: AAAA-MM-DD
sources: Título de la fuente|https://url ;; Otra fuente|https://url
---
```

4. Cuerpo en HTML (sin <h1>; el título lo pone la plantilla). Requisitos:
   - 1.500 a 2.500 palabras útiles, sin relleno. Español de Colombia, tuteo, lenguaje sencillo.
   - Párrafo inicial que plantee el problema real del lector.
   - Secciones con <h2> y, si hace falta, <h3>. Pasos numerados cuando aplique.
   - Al menos un ejemplo con cifras en pesos colombianos dentro de `<div class="example">`, con la aritmética verificada (calcúlala con Python).
   - Usa `<table>`, `<span class="formula">`, `<div class="callout"><strong>Título</strong>texto</div>` y `<blockquote>` cuando ayuden.
   - Sección "Errores comunes", sección "Preguntas frecuentes" (2–4 preguntas con <h3>) y "Resumen" final en viñetas.
   - 2 a 4 enlaces internos a guías ya publicadas (`/guias/slug/`) o a `/herramientas/`.
   - Fuentes oficiales en `sources:`; nada copiado textualmente de otros sitios (parafrasea siempre).
   - No vendas servicios de Domiwebb dentro de las guías.
5. Marca el tema en `TEMAS.md` como `[x] AAAA-MM-DD · categoría · tema` y muévelo a "Publicados".
6. Ejecuta `python3 _build/build.py` y comprueba que no haya errores.
7. Commit y push a `main`. Hostinger publica automáticamente.
