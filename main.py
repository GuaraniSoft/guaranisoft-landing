"""
Landing Page — Ñande ERP / GuaraníSoft
Deploy: Railway o Render
Run: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import os
import time
from collections import defaultdict
from pathlib import Path

import db  # Importamos nuestro nuevo módulo
import sheets  # Integración Google Sheets

from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import secrets

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Ñande ERP — GuaraníSoft", docs_url=None, redoc_url=None)

db.init_db() # <--- Agrega esto al iniciar la app

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ── Rate limiting simple ────────────────────────────────────────────────────
_last_sent: dict[str, float] = defaultdict(float)
RATE_LIMIT_SECONDS = 60

# Render bloquea el puerto 587, así que el envío puede colgarse: lo cortamos.
SMTP_TIMEOUT_SECONDS = 10

# auto_error=False para que la falta de cabecera llegue como None en vez de que
# FastAPI corte con un 401 antes de que podamos revisar la configuración. Así
# "sin configurar" se ve siempre como 503, con credenciales o sin ellas.
security = HTTPBasic(auto_error=False)

# Configura esto en tu .env: ADMIN_USER y ADMIN_PASSWORD
def verify_admin(credentials: HTTPBasicCredentials | None = Depends(security)):
    # Sin credenciales configuradas la ruta no autentica a nadie: no hay
    # usuario y contraseña por defecto que alguien pueda adivinar.
    admin_user = os.getenv("ADMIN_USER", "")
    admin_pass = os.getenv("ADMIN_PASSWORD", "")
    if not (admin_user and admin_pass):
        raise HTTPException(
            status_code=503,
            detail="Consulta de leads no configurada (faltan ADMIN_USER y ADMIN_PASSWORD)",
        )

    # credentials es None si no vino la cabecera, o si no se pudo leer — lo que
    # incluye una clave no ASCII, porque el HTTPBasic de FastAPI decodifica la
    # cabecera como ASCII. Por eso ADMIN_PASSWORD tiene que ser ASCII: con una ñ
    # o una tilde esto da 401 incluso con la clave correcta.
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Falta la autenticación",
            headers={"WWW-Authenticate": "Basic"},
        )

    # En bytes, porque compare_digest sobre str revienta con TypeError si el
    # texto no es ASCII. Los dos se evalúan siempre, para no delatar por tiempo
    # cuál de los dos falló.
    correct_user = secrets.compare_digest(credentials.username.encode("utf-8"), admin_user.encode("utf-8"))
    correct_pass = secrets.compare_digest(credentials.password.encode("utf-8"), admin_pass.encode("utf-8"))
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@app.get("/admin/leads")
async def ver_leads(admin: bool = Depends(verify_admin)):
    leads = db.get_all_leads()
    return {"leads": leads}

# ── Respuesta del formulario: JSON para el fetch, redirect para el navegador ─
# Los formularios tienen method y action, así que sin JavaScript el navegador
# postea igual. En ese caso no sirve devolverle JSON crudo: lo mandamos de
# vuelta a la página con ?sent= y ahí se muestra el aviso.
_PAGINA_PRODUCTO = {"erp": "/nande-erp", "tienda": "/nande-tienda", "crm": "/nande-erp"}
_ESTADOS_SENT = ("ok", "error", "rate")


def _sent_valido(sent: str | None) -> str | None:
    """Solo los tres estados que produce /contacto; cualquier otra cosa se ignora."""
    return sent if sent in _ESTADOS_SENT else None


def _respuesta_contacto(request: Request, producto: str, estado: str, status_code: int = 200):
    # El fetch de base.html pide application/json; una navegación normal pide HTML.
    if "application/json" in request.headers.get("accept", ""):
        content = {"ok": estado == "ok"}
        if estado == "rate":
            content["error"] = "rate_limit"
        elif estado == "error":
            content["error"] = "persistencia"
        return JSONResponse(status_code=status_code, content=content)
    return RedirectResponse(
        f"{_PAGINA_PRODUCTO[producto]}?sent={estado}#contacto",
        status_code=303,
    )


# ── Página principal (corporativa GuaraníSoft) ─────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


# ── Landing Ñande ERP ───────────────────────────────────────────────────────
@app.get("/nande-erp", response_class=HTMLResponse)
async def nande_erp(request: Request, sent: str | None = None):
    return templates.TemplateResponse(request, "index.html", {"sent": _sent_valido(sent)})


# ── Landing Ñande Tienda ───────────────────────────────────────────────────
@app.get("/nande-tienda", response_class=HTMLResponse)
async def nande_tienda(request: Request, sent: str | None = None):
    return templates.TemplateResponse(request, "nande-tienda.html", {"sent": _sent_valido(sent)})


# ── Formulario de contacto ─────────────────────────────────────────────────
async def _send_email_async(asunto: str, body: str, reply_to: str = "") -> None:
    """Avisa del lead por mail. Corre como background task, después de la
    respuesta: el lead ya está guardado, así que si esto falla o se cuelga no
    se pierde nada."""
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    if not (smtp_user and smtp_pass):
        return  # modo desarrollo: sin SMTP configurado no se envía nada
    contact_email = os.getenv("CONTACT_EMAIL", "ventas@guaranisof.com")

    try:
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = contact_email
        if reply_to:
            msg["Reply-To"] = reply_to
        msg["Subject"] = asunto
        msg.attach(MIMEText(body, "plain", "utf-8"))

        await asyncio.wait_for(
            aiosmtplib.send(
                msg,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username=smtp_user,
                password=smtp_pass,
            ),
            timeout=SMTP_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        print(f"[SMTP ERROR] timeout tras {SMTP_TIMEOUT_SECONDS}s — el lead ya está guardado")
    except Exception as e:
        print(f"[SMTP ERROR] {e}")


@app.post("/contacto")
async def contacto(
    request: Request,
    background: BackgroundTasks,
    nombre: str = Form(...),
    empresa: str = Form(""),
    telefono: str = Form(""),
    email: str = Form(""),
    mensaje: str = Form(...),
    producto: str = Form("erp"),   # "erp" | "tienda" | "crm": pestaña del Sheet y asunto del mail
    usa_erp: str = Form(""),
):
    if producto not in ("erp", "tienda", "crm"):
        producto = "erp"
    if producto == "tienda" and usa_erp:
        mensaje = f"[Usa Ñande ERP: {usa_erp}] {mensaje}"
    client_ip = request.client.host if request.client else "unknown"

    # Rate limit. La comprobación y la marca van juntas, sin ningún await en el
    # medio: así el event loop no puede meter otro envío de la misma IP entre
    # las dos y colarse un duplicado. Si después no se puede guardar el lead,
    # restauramos la marca anterior para no bloquearle el reintento 60s.
    now = time.time()
    marca_anterior = _last_sent[client_ip]
    if now - marca_anterior < RATE_LIMIT_SECONDS:
        return _respuesta_contacto(request, producto, "rate", status_code=429)
    _last_sent[client_ip] = now

    nombre_producto = {"erp": "Ñande ERP", "tienda": "Ñande Tienda", "crm": "Ñande CRM"}[producto]
    body = f"""\
Nuevo contacto desde la landing page de {nombre_producto}

Nombre:    {nombre}
Empresa:   {empresa or '—'}
Teléfono:  {telefono or '—'}
Email:     {email or '—'}

Mensaje:
{mensaje}
"""
    # 1. GUARDAR EN GOOGLE SHEETS (almacén primario)
    # 2. BACKUP en SQLite local (efímero en Render Free)
    # Las dos son funciones síncronas: van a un thread para no bloquear el
    # event loop, que es lo que haría esperar a /health y al resto del sitio.
    sheet_saved = await run_in_threadpool(
        sheets.append_to_sheet, nombre, empresa, telefono, email, mensaje, producto=producto
    )
    db_saved = await run_in_threadpool(
        db.save_lead, nombre, empresa, telefono, email, f"[{nombre_producto}] {mensaje}"
    )

    if not (sheet_saved or db_saved):
        # No se guardó en ningún lado: no confirmamos un mensaje que perdimos,
        # y devolvemos el rate limit a como estaba para que pueda reintentar ya.
        # Solo si la marca sigue siendo la nuestra: un guardado que tardó más de
        # 60s puede haber dejado entrar otro envío, y ese ya puso la suya. Pisarla
        # con nuestra marca vieja le abriría la puerta a un tercero.
        if _last_sent[client_ip] == now:
            _last_sent[client_ip] = marca_anterior
        print(f"[LEAD PERDIDO] {nombre} — {telefono or email or 's/contacto'}: falló Sheets y falló SQLite")
        return _respuesta_contacto(request, producto, "error", status_code=500)

    if sheet_saved:
        print(f"[SHEETS] Lead guardado: {nombre} — {email}")
    else:
        print(f"[SHEETS ERROR] Lead guardado solo en SQLite, que es efímero en Render: {nombre}")

    # 3. Aviso por mail: al fondo de la cola, después de responder.
    background.add_task(
        _send_email_async,
        f"Contacto landing {nombre_producto} — {nombre}",
        body,
        email,
    )

    return _respuesta_contacto(request, producto, "ok")


# ── Static root files ──────────────────────────────────────────────────────
@app.get("/robots.txt")
async def robots():
    return FileResponse(BASE_DIR / "static" / "robots.txt")


@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse(BASE_DIR / "static" / "sitemap.xml")


# ── Health check (para Railway/Render) ──────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
