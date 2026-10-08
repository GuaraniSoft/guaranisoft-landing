# Arquitectura y Estructura del Proyecto — Landing GuaraníSoft

> Documentación técnica del proyecto de landing page para Ñande ERP / GuaraníSoft
> Repo: https://github.com/GuaraniSoft/guaranisoft-landing

---

## Visión general

Tres páginas públicas — la corporativa de GuaraníSoft, la landing de Ñande ERP y la de Ñande Tienda — que presentan los productos, capturan leads con un formulario de contacto y dirigen a WhatsApp. Es un proyecto separado del ERP: no comparte código ni base de datos con él.

Los leads se guardan en un Google Sheet (almacén primario) con respaldo en un SQLite local, que en Render Free es efímero y se borra en cada deploy.

```
┌─────────────────────────────────────────────────────┐
│                   Usuario (navegador)                 │
│                  https://guaranisof.com               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Cloudflare (DNS + Proxy)                 │
│  · Resuelve guaranisof.com → IP de Render            │
│  · SSL automático (Proxied)                           │
│  · CDN + protección DDoS                              │
│  · Email Routing (ventas@, soporte@, contacto@)      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Render (Hosting Free Tier)               │
│  · Corre la app FastAPI                              │
│  · URL: guaranisoft-landing.onrender.com             │
│  · Se duerme tras 15 min sin tráfico                 │
│  · Despierta en ~30s al primer request               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              App FastAPI (main.py)                    │
│  · GET /  → home.html (corporativa)                  │
│  · GET /nande-erp → index.html                       │
│  · GET /nande-tienda → nande-tienda.html             │
│  · POST /contacto → guarda el lead                   │
│  · GET /health → health check                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼ (solo si alguien llena el formulario)
┌─────────────────────────────────────────────────────┐
│   Google Sheets "Leads GuaraníSoft"  (primario)      │
│  · gspread + service_account.json                    │
│  · Una pestaña por producto                          │
│  ├─ SQLite leads.db (respaldo, efímero en Render)    │
│  └─ Gmail SMTP (aviso, en background, timeout 10s)   │
│     · Render bloquea el puerto 587: hoy no llega     │
└─────────────────────────────────────────────────────┘
```

---

## Stack tecnológico

| Componente | Tecnología | Versión | Por qué |
|------------|-----------|---------|---------|
| Backend | **FastAPI** | 0.137+ | Rápido, moderno, async |
| Servidor | **Uvicorn** | 0.49+ | ASGI server para FastAPI |
| Templates | **Jinja2** | 3.1+ | Motor de templates de Python |
| CSS Framework | **Bootstrap 5** | 5.3.3 (CDN) | Responsive, mobile-first |
| Iconos | **Bootstrap Icons** | 1.11.3 (CDN) | Set de iconos gratuito |
| Email | **aiosmtplib** | 5.1+ | SMTP async para Python |
| Env vars | **python-dotenv** | 1.0+ | Cargar .env en desarrollo local |
| Forms | **python-multipart** | 0.0.9+ | Parsear formularios HTML |
| Lenguaje | **Python** | 3.12+ | Requisito del ERP también |
| Hosting | **Render** | Free tier | Gratis, sin vencimiento |
| DNS | **Cloudflare** | — | Registrar + DNS + Email Routing |
| Dominio | **guaranisof.com** | — | Cloudflare Registrar |

---

## Estructura de archivos

```
guaranisoft-landing/
│
├── main.py                      # App FastAPI — rutas + lógica de contacto
├── requirements.txt             # Dependencias de Python
├── .env.example                 # Template de variables de entorno
├── .gitignore                   # Archivos a ignorar por git
├── readme.md                    # Resumen del proyecto
│
├── docs/                        # Documentación
│   ├── GUIA_DEPLOY_RENDER.md    # Cómo deployar en Render
│   ├── GUIA_DNS_CLOUDFLARE_RENDER.md  # Cómo configurar DNS
│   └── ARQUITECTURA.md          # Este archivo
│
├── templates/
│   └── index.html               # Landing page completa (una sola página)
│
└── static/
    ├── css/
    │   └── landing.css          # Estilos custom sobre Bootstrap 5
    └── img/
        ├── logo-eslogan.svg     # Logo completo con eslogan (P3)
        ├── logo-compacto.svg    # Logo sin eslogan para navbar (P1)
        └── favicon.svg          # Icono para pestaña del navegador (P4)
```

### Tamaño del proyecto

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `main.py` | 256 | App completa (8 rutas) |
| `sheets.py` | 72 | Google Sheets (almacén primario) |
| `db.py` | 57 | SQLite (respaldo local) |
| `templates/base.html` | 179 | Layout común: navbar, footer, GA4, JS del formulario |
| `templates/home.html` | 222 | Corporativa GuaraníSoft |
| `templates/index.html` | 739 | Landing Ñande ERP |
| `templates/nande-tienda.html` | 534 | Landing Ñande Tienda |
| `templates/_aviso_contacto.html` | 14 | Aviso del formulario sin JavaScript |
| `static/css/landing.css` | 1482 | Estilos custom (CRLF) |
| **Total** | **~3555** | Proyecto liviano y mantenible |

---

## Arquitectura de la app (main.py)

### Rutas

| Método | Path | Función | Descripción |
|--------|------|---------|-------------|
| `GET` | `/` | `home()` | Corporativa GuaraníSoft (`home.html`) |
| `GET` | `/nande-erp` | `nande_erp()` | Landing Ñande ERP (`index.html`). Acepta `?sent=ok\|rate\|error` |
| `GET` | `/nande-tienda` | `nande_tienda()` | Landing Ñande Tienda. Acepta el mismo `?sent=` |
| `POST` | `/contacto` | `contacto()` | Procesa el formulario de las tres páginas |
| `GET` | `/admin/leads` | `ver_leads()` | Lee los leads del SQLite. Basic Auth; **503** si falta configuración |
| `GET` | `/robots.txt` | `robots()` | Sirve `static/robots.txt` |
| `GET` | `/sitemap.xml` | `sitemap()` | Sirve `static/sitemap.xml` |
| `GET` | `/health` | `health()` | Health check para Render. Devuelve `{"status":"ok"}` |

FastAPI además expone `/openapi.json` (el esquema de la API). `/docs` y `/redoc`
están apagados con `docs_url=None, redoc_url=None`.

### Flujo del formulario de contacto

Los tres formularios postean a `/contacto`. El campo oculto `producto`
(`erp` | `tienda` | `crm`) decide la pestaña del Sheet y el asunto del mail.

```
1. Usuario llena el formulario (index.html o nande-tienda.html)
   ↓
2. JS de base.html: fetch POST /contacto con Accept: application/json
   (sin JS, el form tiene method y action: postea igual, como navegación)
   ↓
3. Rate limit: ¿pasaron 60s desde el último envío de esta IP?
   ├── NO → 429 / ?sent=rate
   └── SÍ → reserva la marca acá mismo (sin await en el medio) y continúa
   ↓
4. Google Sheets (run_in_threadpool, timeout 5/10s) → pestaña del producto
   ↓
5. SQLite leads.db (run_in_threadpool) — respaldo, efímero en Render
   ↓
6. ¿Se guardó en alguno de los dos?
   ├── NO → 500 {"ok": false, "error": "persistencia"} / ?sent=error
   │        y libera la marca que reservó, para que pueda reintentar ya —
   │        pero solo si sigue siendo la suya (un guardado de más de 60s
   │        puede haber dejado entrar otro envío que ya puso la propia)
   └── SÍ → deja la marca puesta y sigue
   ↓
7. BackgroundTasks: aviso por mail (Gmail SMTP, timeout 10s)
   Render bloquea el 587, así que hoy falla y solo queda en el log
   ↓
8. Respuesta según el header Accept:
   ├── application/json → {"ok": true}  → showToast() verde
   └── text/html        → 303 a /nande-erp?sent=ok#contacto
```

El aviso del camino sin JavaScript se renderiza desde el servidor en
`templates/_aviso_contacto.html`, que las dos landings incluyen arriba del
formulario. El valor de `sent` se valida contra los tres estados conocidos antes
de llegar al template.

### Rate Limiting

Sistema simple en memoria:
- Diccionario `_last_sent` guarda `{IP: timestamp}`
- Si la misma IP envía otro formulario antes de 60s, se bloquea
- La comprobación y la marca van juntas, sin ningún `await` entre las dos: el
  event loop no puede meter otro envío de la misma IP en el medio y colarse un
  duplicado
- Si el guardado falla, se restaura la marca anterior, así el visitante puede
  reintentar en el acto en vez de esperar 60s por un mensaje que nunca se guardó
- La restauración solo corre si la marca sigue siendo la que reservó esa
  solicitud: un guardado que tarde más de 60s puede haber dejado entrar otro
  envío, y pisar su marca con la vieja le abriría la puerta a un tercero
- **Limitación:** se reinicia si la app se reinicia (no persiste)
- Suficiente para una landing con poco tráfico

---

## Estructura del HTML

Las tres páginas extienden `base.html`, que trae el navbar, el footer, el
WhatsApp flotante, el tag de Google Analytics 4 y el JS del formulario. Cada
página define su `{% block content %}` y los bloques de marca y navegación.

`index.html` (Ñande ERP) tiene 10 secciones, más el navbar, el footer y el
WhatsApp flotante que hereda de `base.html`:

```
index.html
├── <head> — meta tags y SEO propios (bloque head_extra de base.html)
│
├── Navbar (de base.html; fixed-top)
│   ├── Logo (marca-n.svg + "ande ERP")
│   └── Links: Por qué Ñande, Módulos, Precios, Contacto,
│              Ñande Tienda, GuaraníSoft, "Solicitar demo"
│
├── Section: Hero (hero-split)
│   ├── H1: "Controlá tu negocio, aunque se corte internet."
│   ├── CTAs: Solicitar demo + WhatsApp
│   └── Imagen: static/img/dashboard.png
│
├── Section: Pilares (#por-que) — 4 pilares
│   ├── Diseñado para Paraguay
│   ├── Sin depender de internet
│   ├── Control total en un solo lugar
│   └── Soporte directo del que lo programó
│
├── Section: Problemas — "¿Sabés realmente cómo está tu negocio?"
│
├── Section: Módulos (#modulos) — 4 cards
│   ├── Punto de Venta y Facturación
│   ├── Control de Inventario
│   ├── Gestión de Cajas
│   └── Contabilidad Automática
│
├── Section: Casos de uso — "Así se usa en tu negocio"
│   └── Ferretería / varios locales / distribuidora
│
├── Section: Cómo funciona (#como-funciona) — 3 pasos
│   ├── 1. Nos conocemos
│   ├── 2. Instalación en tu computadora
│   └── 3. Acompañamiento
│
├── Section: Prueba social — "¿Quién te atiende?"
│   └── (los testimonios están comentados hasta tener clientes reales)
│
├── Section: Precios (#precios)
│   └── "¿Cuánto cuesta? Depende de tu negocio." — se cotiza, sin precio fijo
│
├── Section: FAQ (#faq) — acordeón de Bootstrap
│
├── Section: Contacto (#contacto)
│   ├── Aviso sin JS (_aviso_contacto.html, solo si llega ?sent=)
│   ├── Formulario (nombre, teléfono, mensaje) → POST /contacto
│   └── Info directa: ventas@, soporte@, WhatsApp, LinkedIn
│
├── Footer (de base.html)
│
├── WhatsApp flotante (de base.html; fixed bottom-right)
│
└── Scripts (de base.html)
    ├── Bootstrap 5.3.3 (CDN)
    ├── initFormularioContacto() + showToast()
    └── IntersectionObserver (fade-in on scroll, sin librerías)
```

> La landing **no** promete facturación electrónica SIFEN como función lista:
> se implementa a pedido, con plazo y costo a cotizar. La regla y la lista
> completa de lo que no se puede presentar como terminado están en `content.md`.

---

## Diseño y paleta de marca

### Colores

| Variable CSS | Hex | Uso |
|---------------|-----|-----|
| `--morado` | `#5B2A86` | Color primario — botones, títulos, acentos |
| `--verde` | `#4A7C59` | Color secundario — botones alternativos, checks |
| `--gris-fondo` | `#F5F7FA` | Fondo de secciones alternadas |
| `--gris-texto` | `#2D2D2D` | Texto principal |
| `--gris-claro` | `#6B7280` | Texto secundario, descripciones |

### Tipografía

- Familia: `'Segoe UI', system-ui, -apple-system, sans-serif`
- Tamaños: h1=2.8rem, h2=2rem, h3=1.2rem, body=1rem
- Responsive: en mobile h1 baja a 1.8rem

### Componentes custom

| Clase CSS | Descripción |
|-----------|-------------|
| `.btn-morado` | Botón primario morado con hover |
| `.btn-verde` | Botón secundario verde con hover |
| `.btn-outline-morado` | Botón outline morado |
| `.feature-card` | Card de feature con hover (sube + sombra) |
| `.paso` | Step de "Cómo funciona" con número circular |
| `.stat-item` | Número grande + label en sección stats |
| `.precios-card` | Card centrada de precios |
| `.contacto-form` | Card con el formulario |
| `.whatsapp-float` | Botón flotante de WhatsApp |
| `.fade-in` | Animación de aparición al hacer scroll |

### Animaciones

- **Fade-in on scroll:** usa IntersectionObserver nativo (sin librerías). Los elementos con clase `.fade-in` aparecen suavemente al entrar en viewport.
- **Hover en cards:** `transform: translateY(-4px)` + sombra más fuerte
- **Hover en botones:** `translateY(-1px)` + sombra de color
- **WhatsApp float:** `scale(1.1)` en hover

---

## Assets (SVG)

Los 3 logos vienen del ERP (Ñande ERP branding v2.0):

| Archivo | Origen | Uso en landing |
|---------|--------|----------------|
| `logo-eslogan.svg` | P3 del branding | Hero centrado — logo + eslogan |
| `logo-compacto.svg` | P1 del branding | Navbar — logo sin eslogan |
| `favicon.svg` | P4 del branding | Pestaña del navegador |

Todos usan la paleta morado `#5B2A86` + verde `#4A7C59`.

---

## Variables de entorno

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `SMTP_USER` | Sí (para emails) | Gmail desde donde se envían los emails del formulario |
| `SMTP_PASSWORD` | Sí (para emails) | App Password de Gmail (16 caracteres) |
| `CONTACT_EMAIL` | No (default: `ventas@guaranisof.com`) | Email destino donde llegan los mensajes |
| `ADMIN_USER` | Sí (para `/admin/leads`) | Usuario del Basic Auth de `/admin/leads` |
| `ADMIN_PASSWORD` | Sí (para `/admin/leads`) | Clave del Basic Auth. **Solo ASCII** (ver Seguridad) |
| `PORT` | No (default: `8000`) | Puerto. En Render lo setea automáticamente |
| `RENDER_DATA_DIR` | No (default: la raíz del proyecto) | Directorio donde vive `leads.db` |

**Si `SMTP_USER` o `SMTP_PASSWORD` no están configuradas**, el formulario igual
guarda el lead y responde éxito, pero no se envía ningún email. Útil para
desarrollo local.

**Si `ADMIN_USER` o `ADMIN_PASSWORD` no están configuradas**, `/admin/leads`
responde 503 y no deja entrar a nadie. El resto del sitio funciona igual.

**La cuenta de servicio de Google** no es una variable de entorno: es el archivo
`service_account.json`, que `sheets.py` busca en la raíz del proyecto (local) y
en `/etc/secrets/` (Secret File de Render). Sin él, los leads van solo al SQLite.

---

## SEO

Cada página define sus propios meta en el bloque `head_extra`. Los de
`/nande-erp` (sin mencionar SIFEN, que no es una función terminada):

```html
<title>Ñande ERP — Punto de Venta, Inventario y Contabilidad | GuaraníSoft</title>
<meta name="description" content="Sistema de gestión para PyMEs en Paraguay. Punto de venta rápido, control de stock, cajas y contabilidad. Funciona sin internet.">
<meta property="og:title" content="Ñande ERP — El sistema que ordena tu empresa">
<meta property="og:description" content="Punto de venta, stock, cajas y contabilidad. Funciona sin internet y te atiende quien lo programó.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://guaranisof.com/nande-erp">
<meta property="og:image" content="https://guaranisof.com/static/img/og-image.png?v=2">
<link rel="canonical" href="https://guaranisof.com/nande-erp">
```

Más un bloque `application/ld+json` por página. `og:url` y el `canonical`
apuntan a la URL de cada página, no a la raíz.

---

## Seguridad

| Medida | Implementación |
|--------|----------------|
| Rate limiting | 1 envío por IP cada 60 segundos (en memoria). La marca se reserva junto a la comprobación, sin `await` en el medio, para que dos envíos simultáneos no se cuelen; si el guardado falla se libera, pero solo si todavía es la que reservó esa solicitud |
| `/admin/leads` | Basic Auth con `ADMIN_USER` y `ADMIN_PASSWORD`. **Sin valores por defecto**: si faltan, 503 con o sin cabecera de autenticación (`HTTPBasic(auto_error=False)`, para que la configuración se revise antes que las credenciales) |
| Comparación de credenciales | `secrets.compare_digest` sobre bytes, los dos campos siempre evaluados (sin fuga por tiempo) |
| SMTP credentials | Variables de entorno, nunca en código |
| Cuenta de servicio | `service_account.json` en `.gitignore`; en Render, Secret File en `/etc/secrets/` |
| Docs deshabilitados | `docs_url=None, redoc_url=None` en FastAPI (`/openapi.json` sí queda expuesto) |
| .env en .gitignore | Credenciales nunca se suben a git |
| Reply-To del formulario | El email del usuario queda como Reply-To |
| Validación de `?sent=` | Solo `ok`, `rate` y `error`; cualquier otro valor se descarta antes del template |
| Error handling SMTP | Si falla el envío, se loguea pero no se expone el error al usuario |

> **`ADMIN_PASSWORD` tiene que ser ASCII.** El `HTTPBasic` de FastAPI decodifica
> la cabecera `Authorization` como ASCII, así que una clave con ñ o tilde no
> llega nunca a `verify_admin` y la ruta siempre responde 401, incluso con la
> clave correcta.

---

## Relación con el ERP

```
┌─────────────────────┐         ┌─────────────────────────┐
│  Landing Page       │         │  ERP (Ñande ERP)         │
│  guaranisof.com     │         │  localhost:8000          │
│  (Render, público)  │         │  (WSL, local)            │
├─────────────────────┤         ├─────────────────────────┤
│  · Marketing        │         │  · App principal          │
│  · Captura de leads │  ───→   │  · 96 tablas MySQL        │
│  · Info del producto│         │  · SIFEN, Tributario     │
│  · WhatsApp link    │         │  · Contabilidad, Cajas   │
└─────────────────────┘         └─────────────────────────┘
```

- **No comparten código** — son repos separados
- **No comparten base de datos** — la landing solo guarda leads (Google Sheets + un SQLite de respaldo); no toca la base del ERP
- **Comparten branding** — los SVG se copiaron del ERP a la landing
- **Comparten dominio** — guaranisof.com es de GuaraníSoft (la empresa)
- El ERP se deployará después (con Docker) cuando esté listo para demo

---

## Cómo extender

### Agregar una sección nueva
1. Agregar el HTML en `templates/index.html` (siguiendo el patrón de `<section>`)
2. Agregar estilos en `static/css/landing.css` si necesita algo custom
3. Si tiene su propia ruta, agregar en `main.py`

### Agregar una página nueva (ej: /privacidad)
1. Crear `templates/privacidad.html`
2. Agregar ruta en `main.py`:
   ```python
   @app.get("/privacidad", response_class=HTMLResponse)
   async def privacidad(request: Request):
       return templates.TemplateResponse(request, "privacidad.html")
   ```
3. Link en el navbar o footer

### Cambiar el contenido
Todo el texto está hardcodeado en los templates (`home.html`, `index.html`,
`nande-tienda.html`). No hay CMS: la única base de datos guarda leads. Para
cambiar algo, editar el HTML y pushear a git — Render hace redeploy automático.
La fuente de verdad de lo que la landing del ERP puede prometer es `content.md`.

### Actualizar los logos
1. Copiar los nuevos SVG del ERP a `static/img/`
2. Commit + push
3. Render redeploya solo

---

*Documentado el 2026-06-17 por GLM-5.2 (AutoClaw) para GuaraníSoft / Ñande ERP.*
