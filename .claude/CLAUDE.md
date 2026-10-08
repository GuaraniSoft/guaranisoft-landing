# CLAUDE.md — Landing GuaraníSoft

## Context
This is the landing page for Ñande ERP, a Paraguayan ERP system built by GuaraníSoft.
The landing is a separate project from the ERP itself — different repo, different deploy.

## Quick start
```bash
cd /home/victor/Proyectos/guaranisoft-landing
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env  # edit with real credentials
.venv/bin/uvicorn main:app --reload
```

## Architecture
- **FastAPI** app with 8 routes: `/` (corporativa GuaraníSoft), `/nande-erp` (landing producto), `/nande-tienda` (landing Ñande Tienda, e-commerce satélite del ERP — código en `/home/victor/nande-tienda/`), `POST /contacto`, `/admin/leads`, `/robots.txt`, `/sitemap.xml`, `/health`
- **Jinja2** templates: `templates/base.html` (layout: navbar, footer, GA4, JS del formulario) + `templates/home.html` (corporativa) + `templates/index.html` (landing Ñande ERP) + `templates/nande-tienda.html` (landing Ñande Tienda) + `templates/_aviso_contacto.html` (aviso del formulario sin JS)
- **Bootstrap 5** via CDN + custom CSS (`static/css/landing.css`)
- **Google Analytics 4** — tag `gtag.js` (ID `G-QWBG8NPSMW`) en `templates/base.html`, una sola vez para las tres páginas
- **Google Sheets** (primary persistence via gspread)
- **SQLite** (fallback, local only — not persistent on Render Free)
- **SMTP** (Gmail, `BackgroundTasks` with 10s timeout — se envía después de responder)

## Key files
- `main.py` — FastAPI app, routes, email logic
- `sheets.py` — Google Sheets integration (gspread)
- `db.py` — SQLite fallback
- `templates/index.html` — Full landing page (7 sections, AJAX form)
- `static/css/landing.css` — Custom styles
- `static/img/` — Logo SVGs (from ERP branding v2.0)

## Form flow
1. User fills form → `fetch('/contacto', {POST, Accept: application/json})`
2. `sheets.append_to_sheet(..., producto)` en `run_in_threadpool` (es síncrono: bloquearía el event loop) → Google Sheet "Leads GuaraníSoft", pestaña según campo oculto `producto`: "Ñande ERP" (default), "Ñande Tienda", "Ñande CRM". **La pestaña "Ñande Tienda" hay que crearla a mano con las mismas columnas.** Timeout de gspread: 5s conexión / 10s lectura.
3. `db.save_lead()` → SQLite (local fallback), también en threadpool
4. **Si fallaron los dos** → 500 `{"ok": false, "error": "persistencia"}` y el rate limit **no** se marca, así puede reintentar enseguida. No se confirma un mensaje que se perdió.
5. `BackgroundTasks` → `_send_email_async()`, SMTP con timeout de 10s, después de responder
6. Returns `{"ok": true}` JSON → el JS muestra el toast verde y resetea el form
7. Rate limit: 60s per IP (429, toast amarillo). La marca se pone **después** de guardar
8. Sin JavaScript: los forms tienen `method="post" action="/contacto"`, así que postean igual. `/contacto` negocia por `Accept` y devuelve un 303 a `/nande-erp?sent=ok|rate|error#contacto`; el aviso lo renderiza `templates/_aviso_contacto.html`

## Environment variables
```
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
CONTACT_EMAIL=contacto@guaranisof.com
ADMIN_USER=admin
ADMIN_PASSWORD=change_this   # solo ASCII: con ñ o tilde, /admin/leads da 401 siempre
```
Sin `ADMIN_USER` y `ADMIN_PASSWORD`, `/admin/leads` responde 503 — no hay
credenciales por defecto. El resto del sitio funciona igual.

## Secret Files
- `service_account.json` — Google Cloud service account key
- On Render: uploaded as Secret File → lives in `/etc/secrets/`
- On local: placed in project root
- **NEVER commit this file** (it's in .gitignore)
- `sheets.py` searches both locations automatically

## Deploy (Render)
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free (512MB RAM, spins down after 15min idle)
- **Auto-deploy:** on push to `main` branch
- **Custom domain:** guaranisof.com (via Cloudflare DNS)

## Known issues
- **Render blocks SMTP port 587** — emails don't send in production. Leads still save to Google Sheets. Need alternative: SendGrid free, Mailgun, or similar.
- **Render Free cold start** — Render apaga el servicio tras 15 min sin tráfico y el siguiente visitante espera 30-50s. Mitigado con un ping externo a `/health` cada 10 min, de 7:15 a 21:00 (hora PY): ver `docs/GUIA_MANTENER_DESPIERTO_RENDER.md`. Fuera de esa ventana el arranque sigue existiendo. **Ojo:** el workspace tiene 750 horas Free por mes y, si se agotan, Render suspende todos los servicios Free hasta el mes siguiente.
- **SQLite not persistent** — Render Free disk is ephemeral. Google Sheets is the primary store.
- **Rate limit is in-memory** — resets on app restart. Not a problem for low traffic.

## Branding
- **Logo:** Ñ pixelada (morado #5B2A86) + "ande ERP" text + mburucuyá watermark. La Ñ sola (`static/img/marca-n.svg`) es la marca GuaraníSoft: idéntica en todos los productos, sin agregados. Ñande Tienda usa Ñ + texto "ande Tienda" (clase `.tienda-wordmark`).
- **Colors:** morado #5B2A86, verde #4A7C59, gris #F5F7FA
- **Slogan:** "Hecho en Paraguay. Hecho para Paraguay."
- **Do not change colors or logo without owner authorization**

## Owner
Victor Roman — victor.roman.czu@gmail.com — +595 992 504 620

## Related repos
- **ERP:** `/home/victor/erp-system/` (private, local only)
- **Landing:** this repo — https://github.com/GuaraniSoft/guaranisoft-landing

## Documentation
- `docs/GUIA_DEPLOY_RENDER.md` — Step-by-step Render deploy guide
- `docs/GUIA_DNS_CLOUDFLARE_RENDER.md` — DNS configuration guide
- `docs/GUIA_MANTENER_DESPIERTO_RENDER.md` — Por qué el sitio se duerme, el límite de 750 horas y el ping que lo mantiene despierto
- `docs/ARQUITECTURA.md` — Full architecture documentation
- `content.md` — Content source of truth de la landing del ERP (features, sections); Ñande Tienda se documenta en `/home/victor/nande-tienda/docs/`

## Git conventions
- Branch: `main`
- Commits in Spanish, conventional commits format
- Never commit: `.env`, `service_account.json`, `leads.db`, `.venv/`
