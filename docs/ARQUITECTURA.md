# Arquitectura y Estructura del Proyecto — Landing GuaraníSoft

> Documentación técnica del proyecto de landing page para Ñande ERP / GuaraníSoft
> Repo: https://github.com/GuaraniSoft/guaranisoft-landing

---

## Visión general

Landing page pública que presenta el producto Ñande ERP, captura leads mediante un formulario de contacto, y dirige a WhatsApp. Es un proyecto separado del ERP — no comparte código ni base de datos.

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
│  · GET /  → sirve index.html (landing)               │
│  · POST /contacto → envía email vía SMTP             │
│  · GET /health → health check                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼ (solo si alguien llena el formulario)
┌─────────────────────────────────────────────────────┐
│              Gmail SMTP (smtp.gmail.com:587)          │
│  · App Password de Google                            │
│  · Envía email a contacto@guaranisof.com             │
│  · Cloudflare Email Routing → Gmail de Victor         │
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
landing-guaranisoft/
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
| `main.py` | 107 | App completa (3 rutas) |
| `templates/index.html` | 380 | Landing completa (7 secciones) |
| `static/css/landing.css` | 375 | Estilos custom |
| **Total** | **862** | Proyecto liviano y mantenible |

---

## Arquitectura de la app (main.py)

### Rutas

| Método | Path | Función | Descripción |
|--------|------|---------|-------------|
| `GET` | `/` | `index()` | Sirve la landing page. Acepta `?sent=1` para mostrar mensaje de éxito |
| `POST` | `/contacto` | `contacto()` | Procesa el formulario, envía email, redirige |
| `GET` | `/health` | `health()` | Health check para Render. Devuelve `{"status":"ok"}` |

### Flujo del formulario de contacto

```
1. Usuario llena el formulario en index.html
   ↓
2. POST /contacto con: nombre, empresa, telefono, email, mensaje
   ↓
3. Rate limit: ¿pasaron 60s desde el último envío de esta IP?
   ├── SÍ → redirige a /#contacto?sent=rate
   └── NO → continúa
   ↓
4. ¿SMTP_USER y SMTP_PASSWORD configurados?
   ├── SÍ → envía email vía Gmail SMTP a contacto@guaranisof.com
   │       (si falla, logea el error pero no rompe)
   └── NO → salta el envío (modo desarrollo)
   ↓
5. Redirige a /?sent=1#contacto
   ↓
6. Usuario ve mensaje: "¡Gracias! Tu mensaje fue enviado."
```

### Rate Limiting

Sistema simple en memoria:
- Diccionario `_last_sent` guarda `{IP: timestamp}`
- Si la misma IP envía otro formulario antes de 60s, se bloquea
- **Limitación:** se reinicia si la app se reinicia (no persiste)
- Suficiente para una landing con poco tráfico

---

## Estructura del HTML (index.html)

Una sola página con 7 secciones + navbar + footer + WhatsApp flotante:

```
index.html
├── <head> — meta tags, SEO, CSS (Bootstrap + custom)
│
├── Navbar (fixed-top)
│   ├── Logo (logo-compacto.svg)
│   └── Links: Features, Cómo funciona, Precios, Contacto, "Solicitar demo"
│
├── Section: Hero (#top)
│   ├── Logo con eslogan (logo-eslogan.svg)
│   ├── Tagline: "Hecho en Paraguay. Hecho para Paraguay."
│   ├── Subtítulo
│   └── CTAs: Solicitar demo + WhatsApp
│
├── Section: Problema/Solución
│   ├── Columna izquierda: El problema (ERPs extranjeros no sirven)
│   └── Columna derecha: La solución (hecho en Paraguay)
│
├── Section: Features (#features) — 9 cards
│   ├── 📊 Dashboard e Indicadores
│   ├── 🛒 Ventas y Compras
│   ├── 📦 Inventario
│   ├── 🧾 Facturación Electrónica SIFEN
│   ├── ⚖️ Tributario y Fiscal
│   ├── 📚 Contabilidad
│   ├── 💵 Cajas
│   ├── 🏦 Préstamos
│   └── 🏢 Multimoneda y Multisucursal
│
├── Section: Cómo funciona (#como-funciona) — 3 pasos
│   ├── 1. Solicitás demo
│   ├── 2. Te instalamos
│   └── 3. Empezás a usar
│
├── Section: Stats — 4 números
│   ├── 96 tablas de datos
│   ├── 350+ endpoints
│   ├── 7 tipos de DTE SIFEN
│   └── 100% cumplimiento Ley 6380
│
├── Section: Precios (#precios)
│   └── Card: Licencia única + módulos + "Consultá por precio"
│
├── Section: Contacto (#contacto)
│   ├── Formulario (nombre, empresa, teléfono, email, mensaje)
│   └── Info directa: ventas@, soporte@, WhatsApp, LinkedIn
│
├── Footer
│   ├── Ñande ERP por GuaraníSoft
│   └── Links: guaranisof.com, contacto@, WhatsApp
│
├── WhatsApp flotante (fixed bottom-right)
│
└── Scripts
    ├── Bootstrap 5.3.3 (CDN)
    └── IntersectionObserver (fade-in on scroll, sin librerías)
```

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
| `CONTACT_EMAIL` | No (default: `contacto@guaranisof.com`) | Email destino donde llegan los mensajes |
| `PORT` | No (default: `8000`) | Puerto. En Render lo setea automáticamente |

**Si `SMTP_USER` o `SMTP_PASSWORD` no están configuradas**, el formulario igual procesa y muestra el mensaje de éxito, pero no se envía ningún email. Útil para desarrollo local.

---

## SEO

```html
<title>Ñande ERP — ERP paraguayo con facturación electrónica SIFEN | GuaraníSoft</title>
<meta name="description" content="ERP paraguayo con facturación electrónica SIFEN, cumplimiento tributario Ley 6380 y contabilidad. Hecho en Paraguay por GuaraníSoft.">
<meta property="og:title" content="Ñande ERP — ERP paraguayo">
<meta property="og:description" content="Hecho en Paraguay. Hecho para Paraguay. Facturación SIFEN, tributario, contabilidad.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://guaranisof.com">
```

---

## Seguridad

| Medida | Implementación |
|--------|----------------|
| Rate limiting | 1 envío por IP cada 60 segundos (en memoria) |
| SMTP credentials | Variables de entorno, nunca en código |
| Docs deshabilitados | `docs_url=None, redoc_url=None` en FastAPI |
| .env en .gitignore | Credenciales nunca se suben a git |
| Reply-To del formulario | El email del usuario queda como Reply-To |
| Error handling SMTP | Si falla el envío, se loguea pero no se expone el error al usuario |

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
- **No comparten base de datos** — la landing no tiene DB
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
Todo el texto está hardcodeado en `templates/index.html`. No hay CMS ni base de datos. Para cambiar algo, editar el HTML y pushear a git — Render hace redeploy automático.

### Actualizar los logos
1. Copiar los nuevos SVG del ERP a `static/img/`
2. Commit + push
3. Render redeploya solo

---

*Documentado el 2026-06-17 por GLM-5.2 (AutoClaw) para GuaraníSoft / Ñande ERP.*
