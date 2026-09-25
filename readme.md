# Landing Page — Ñande ERP / GuaraníSoft

## Deploy

### Railway
1. Crear proyecto en [railway.app](https://railway.app)
2. Conectar este repo
3. Setear variables de entorno:
   - `SMTP_USER` — Gmail para enviar emails
   - `SMTP_PASSWORD` — App Password de Gmail
   - `CONTACT_EMAIL` — contacto@guaranisof.com
4. Deploy automático

### Render
1. Crear Web Service en [render.com](https://render.com)
2. Conectar repo
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Setear variables de entorno

### Local
```bash
python -m venv .venv
source .venv/bin/activate  # Linux
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env  # editar con tus credenciales
uvicorn main:app --reload
```

## Estructura
```
main.py              # FastAPI app + formulario contacto
templates/
  index.html         # Landing completa
static/
  css/landing.css    # Estilos custom
  img/               # Logos y favicon
requirements.txt
.env.example
```

## SMTP (Gmail)
1. Activar 2FA en tu cuenta de Google
2. Crear App Password: https://myaccount.google.com/apppasswords
3. Setear `SMTP_USER` y `SMTP_PASSWORD` en .env

## Dominio
`guaranisof.com` — Cloudflare Registrar

## Stack
- Python 3.14 / FastAPI / Jinja2
- Bootstrap 5 (CDN)
- aiosmtplib para emails
