# Pyme al Día

Sitio estático de guías para pymes en Colombia.

- Las guías fuente están en `_build/guias/` (encabezado `---` + cuerpo HTML).
- Las páginas fijas están en `_build/paginas/`.
- Para regenerar el sitio: `python3 _build/build.py`
- Hostinger despliega la rama `main` automáticamente.
- Para cambiar de dominio: edita `base_url` en `_build/config.json` y vuelve a construir.
