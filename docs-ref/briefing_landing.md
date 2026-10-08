# Briefing — Landing Page GuaraniSoft

> ⚠️ **Briefing original, ya superado.** Es el encargo con el que se construyó
> la primera versión de la landing y conserva stats y promesas que después se
> bajaron (entre ellas SIFEN y los números de prueba social). La fuente de
> verdad del copy es `content.md`; el rediseño que corrigió esto está en
> `propuesta_rediseño_landing.md`.

## Objetivo
Crear una landing page para `guaranisof.com` que presente el producto **Ñande ERP** a potenciales clientes paraguayos. El objetivo es que el visitante entienda qué es, confíe en el producto y tome acción (demo o contacto).

## Stack tecnológico
- Python / FastAPI
- Jinja2 (templates)
- Bootstrap 5
- Deploy: Railway o Render (gratis)

## Dominio
`guaranisof.com` — registrado en Cloudflare

## Emails configurados
- `ventas@guaranisof.com`
- `soporte@guaranisof.com`
- `contacto@guaranisof.com`
Todos redirigen a `victor.roman.czu@gmail.com` via Cloudflare Email Routing.

## WhatsApp de contacto
`+595992504620`

## Estructura de secciones propuesta
1. **Hero** — Nombre + tagline + botón "Solicitar demo" + botón WhatsApp
2. **Problema/Solución** — Por qué existe GuaraniSoft / Ñande ERP
3. **Features** — Cards con las funcionalidades principales del ERP
4. **Cómo funciona** — 3 pasos: Solicitás demo → Te instalamos → Empezás a usar
5. **Prueba social** — Testimonios o indicador de clientes actuales
6. **Precios** — Sección "Consultá por precio" sin mostrar números
7. **Contacto/CTA** — Formulario: nombre, empresa, teléfono, email, mensaje → envía a `contacto@guaranisof.com`

## Tareas para AutoClaw
- [ ] Revisar el proyecto ERP para extraer los features reales del sistema
- [ ] Escribir el contenido de cada sección basado en lo que el ERP realmente hace
- [ ] Crear la estructura FastAPI + Jinja2 para la landing
- [ ] Diseñar con Bootstrap 5, estilo moderno y profesional
- [ ] Formulario de contacto funcional que envíe email
- [ ] Botón WhatsApp flotante
- [ ] Responsive mobile-first (clientes paraguayos usan celular)
- [ ] SEO básico: meta tags, título, descripción

## Notas importantes
- El producto se llama **Ñande ERP** (puede incluir futura suite: Ñande CRM, Ñande Contador)
- La empresa se llama **GuaraniSoft**
- Mercado objetivo: pequeñas y medianas empresas paraguayas
- Modelo de venta: licencia única + mantenimiento mensual
- Instalación local en Windows (no SaaS), portable MySQL
- El tono debe transmitir: confianza, cercanía, hecho para Paraguay
- No inventar features — extraerlos del código del proyecto

## Entregable esperado
Proyecto FastAPI listo para deployar en Railway/Render con:
- `main.py`
- `templates/index.html`
- `static/` (CSS adicional si aplica)
- `requirements.txt`
- `README.md` con instrucciones de deploy

---

## Contenido real (adjunto por Victor)

El archivo `landing_content.md` contiene todo el contenido extraído del ERP real:
- Tagline, subtítulo y CTAs del Hero
- Texto de Problema/Solución
- 9 features con iconos y descripciones reales
- 3 pasos de "Cómo funciona"
- Stats de prueba social (96 tablas, 350+ endpoints, 7 DTE SIFEN)
- Estructura de precios (licencia única + módulos)
- Datos de contacto completos

## Paleta de colores
- Morado: `#5B2A86`
- Verde: `#4A7C59`
- Gris claro: `#F5F7FA`

## Assets
- Logo: `/static/img/logo-eslogan.svg`

## SEO meta description
"ERP paraguayo con facturación electrónica SIFEN, cumplimiento tributario Ley 6380 y contabilidad. Hecho en Paraguay por GuaraníSoft."

## Notas críticas
- Botón WhatsApp flotante fijo bottom-right → `https://wa.me/595992504620`
- Mobile-first obligatorio
- Formulario funcional → envía a `contacto@guaranisof.com`
- NO inventar features — usar solo lo del landing_content.md
