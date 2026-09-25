# Guía de Deploy en Render — Paso a Paso

> Cómo deployar un proyecto FastAPI en Render (gratis, sin vencimiento)
> Basado en la experiencia real deployando la landing de Ñande ERP / GuaraníSoft

---

## ¿Qué es Render?

Render es un servicio de hosting en la nube. Te permite tener tu app corriendo 24/7 sin tu PC prendida. El plan **Free** es gratis para siempre, pero la app se "duerme" tras 15 minutos sin visitas. Cuando alguien entra, despierta (puede tardar ~30 segundos el primer request).

---

## Requisitos previos

1. **Repo en GitHub** con tu código
2. **`requirements.txt`** en la raíz del repo
3. **Start Command** correcto: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Variables de entorno** listas (SMTP, etc.)

---

## Paso a paso

### 1. Subir el código a GitHub

```bash
cd /home/victor/mi-proyecto
git init
git add -A
git commit -m "init: mi proyecto"
git remote add origin https://github.com/TU_USUARIO/mi-proyecto.git
git branch -M main   # IMPORTANTE: GitHub espera "main", no "master"
git push -u origin main
```

**⚠️ Antes de commitear:** asegurate de tener `.gitignore` con:
```
.venv/
__pycache__/
*.pyc
.env
```

Si no, vas a subir miles de archivos de Python innecesarios (nos pasó: 1900 archivos del .venv).

### 2. Crear cuenta en Render

1. Entrá a https://render.com
2. Click en **"Sign Up"** → **"Sign Up with GitHub"**
3. Autorizá Render a acceder a tus repos

### 3. Crear el Web Service

1. Click en **"New +"** (arriba a la derecha)
2. Elegí **"Web Service"** ⚠️ NO "Static Site"
   - Static Site = solo HTML/CSS suelto (no corre Python)
   - Web Service = corre código backend (FastAPI, Flask, Django, etc.)
3. Seleccioná tu repo de GitHub
4. Click **"Continue"**

### 4. Configurar el servicio

| Campo | Valor |
|-------|-------|
| **Name** | mi-proyecto (o el nombre que quieras) |
| **Project** | (opcional, podés dejarlo vacío) |
| **Environment** | Production |
| **Language** | Python 3 |
| **Branch** | main |
| **Region** | Oregon (US West) — el más cercano gratis |
| **Root Directory** | (dejar vacío) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free ($0/month) |

**⚠️ El Start Command es lo más importante.** Si lo dejás como viene por defecto (`gunicorn your_application.wsgi`) va a fallar con `gunicorn: command not found`.

### 5. Variables de entorno

Más abajo en la misma pantalla, en **"Environment Variables"**:

| Name | Value | Descripción |
|------|-------|-------------|
| `SMTP_USER` | tu_email@gmail.com | Gmail para enviar emails del formulario |
| `SMTP_PASSWORD` | abcd efgh ijkl mnop | App Password de Gmail (ver abajo) |
| `CONTACT_EMAIL` | contacto@guaranisof.com | Email donde llegan los mensajes del formulario |

Click en **"Add Environment Variable"** por cada una.

### 6. Deploy

1. Click en **"Create Web Service"** (abajo de todo)
2. Render empieza a construir:
   - Clona el repo
   - Instala Python 3.14
   - Corre `pip install -r requirements.txt`
   - Corre el Start Command
3. Cuando termine, vas a ver **"Live"** en verde
4. Tu URL será: `https://mi-proyecto.onrender.com`

### 7. Si necesitas cambiar algo después

- **Start Command:** Settings → Start Command → editar → Save (redeploy automático)
- **Variables de entorno:** Settings → Environment → agregar/editar
- **Redeploy manual:** Manual Deploy → "Deploy latest commit"
- **Ver logs:** click en el servicio → "Logs" (izquierda)

---

## App Password de Gmail

Para que el formulario de contacto envíe emails reales, necesitás un App Password:

1. Entrá a https://myaccount.google.com
2. **Seguridad** → Activá **Verificación en 2 pasos** (si no lo tenés)
3. Entrá a https://myaccount.google.com/apppasswords
4. Nombre: "Render Landing" (o lo que quieras)
5. Click **"Crear"**
6. Te da algo como: `abcd efgh ijkl mnop`
7. Copialo **sin espacios**: `abcdefghijklmnop`
8. Ese es tu `SMTP_PASSWORD`

---

## Apuntar el dominio (Cloudflare → Render)

Una vez que la app esté funcionando en `mi-proyecto.onrender.com`:

1. Entrá a https://dash.cloudflare.com
2. Seleccioná tu dominio (ej: `guaranisof.com`)
3. **DNS** → **Records** → **Add Record**
4. Tipo: **CNAME**
5. Name: `@` (o `www`)
6. Target: `mi-proyecto.onrender.com`
7. Proxy status: **Proxied** (naranja)
8. **Save**

Después en Render:
1. Settings → **Custom Domains** → **Add Custom Domain**
2. Escribí: `guaranisof.com`
3. Render te va a decir que agregues un CNAME (que ya hiciste en Cloudflare)
4. Esperá unos minutos a que se propague el DNS

---

## Errores comunes y soluciones

### `gunicorn: command not found`
**Causa:** El Start Command no se cambió del default.
**Solución:** Settings → Start Command → `uvicorn main:app --host 0.0.0.0 --port $PORT`

### `Your service has not been deployed because the GitHub repository is empty`
**Causa:** El repo no tiene código en la rama `main`.
**Solución:** Verificar que el push se hizo a `main` (no `master`):
```bash
git branch -M main
git push -u origin main
```

### SSH push a GitHub falla
**Causa:** SSH keys no configuradas en WSL.
**Solución:** Usar HTTPS en vez de SSH:
```bash
git remote set-url origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

### El build tarda mucho o se queda colgado
**Causa:** Se subió el `.venv` o `__pycache__` al repo.
**Solución:** Agregar `.gitignore` y remover del cache:
```bash
echo '.venv/' > .gitignore
echo '__pycache__/' >> .gitignore
git rm -r --cached .venv __pycache__
git commit -m "fix: gitignore"
git push
```

### La app se duerme (cold start de 30+ segundos)
**Causa:** Plan Free de Render — se duerme tras 15 min sin tráfico.
**Solución:** Es normal. Para producción seria,升级 a Starter ($7/mes). Para una landing con pocas visitas, está bien.

---

## Reproducir el deploy de la landing

```bash
# 1. Clonar el repo
git clone https://github.com/GuaraniSoft/guaranisoft-landing.git
cd guaranisoft-landing

# 2. Crear venv e instalar
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Probar local
cp .env.example .env  # editar con tus credenciales
.venv/bin/uvicorn main:app --reload

# 4. Deployar en Render
# Seguir los pasos de arriba con este repo
```

---

## Resumen visual

```
GitHub (código) → Render (hosting) → Cloudflare DNS (dominio)
     ↓                  ↓                    ↓
github.com/...   mi-proyecto.onrender.com   guaranisof.com
```

1. Subís código a GitHub
2. Render lee el repo, instala dependencias, corre la app
3. Cloudflare apunta tu dominio a Render
4. Usuario entra a `guaranisof.com` → llega a Render → ve tu página

---

*Documentado el 2026-06-17 basado en el deploy real de la landing de Ñande ERP / GuaraníSoft.*
