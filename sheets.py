"""
Integración Google Sheets — Leads GuaraníSoft
Guarda cada lead del formulario en una hoja de Google Sheets compartida.
Requiere: service_account.json (no subir a git)

Sheet: "Leads GuaraníSoft"
  - Pestaña "Ñande ERP"  → leads del producto ERP
  - Pestaña "Ñande CRM"  → leads del producto CRM (futuro)
"""

import os
import gspread
from datetime import datetime

SHEET_NAME = "Leads GuaraníSoft"
WORKSHEET_ERP = "Ñande ERP"
WORKSHEET_CRM = "Ñande CRM"
WORKSHEET_TIENDA = "Ñande Tienda"   # crear la pestaña en el Sheet con las mismas columnas

# (conexión, lectura) en segundos. Sin esto, un Sheets lento cuelga el request
# del formulario sin límite: gspread no trae ningún timeout por defecto.
SHEETS_TIMEOUT = (5, 10)

# Buscar el JSON en múltiples ubicaciones (local + Render)
_SA_PATHS = [
    'service_account.json',                    # Local (raíz)
    '/etc/secrets/service_account.json',       # Render Secret Files
    os.path.join(os.getcwd(), 'service_account.json'),
]

def _get_sa_path():
    for p in _SA_PATHS:
        if os.path.exists(p):
            return p
    return 'service_account.json'  # default, aunque no exista (para ver el error)


def _get_worksheet(name):
    """Conecta al Sheet y devuelve la worksheet especificada."""
    sa_path = _get_sa_path()
    gc = gspread.service_account(filename=sa_path)
    gc.set_timeout(SHEETS_TIMEOUT)
    sh = gc.open(SHEET_NAME)
    try:
        return sh.worksheet(name)
    except Exception:
        # Si la pestaña no existe, la crea con encabezados
        ws = sh.add_worksheet(title=name, rows=1000, cols=10)
        ws.append_row(["Fecha", "Nombre", "Empresa", "Teléfono", "Email", "Mensaje"])
        return ws


def append_to_sheet(nombre, empresa, telefono, email, mensaje, producto="erp"):
    """
    Agrega una fila al Google Sheet.
    producto: "erp" → pestaña Ñande ERP, "crm" → pestaña Ñande CRM, "tienda" → pestaña Ñande Tienda
    Retorna True si tuvo éxito, False si falló.
    """
    try:
        if producto == "crm":
            ws = _get_worksheet(WORKSHEET_CRM)
        elif producto == "tienda":
            ws = _get_worksheet(WORKSHEET_TIENDA)
        else:
            ws = _get_worksheet(WORKSHEET_ERP)

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([fecha, nombre, empresa, telefono, email, mensaje])
        return True
    except Exception as e:
        print(f"[GOOGLE SHEETS ERROR] {e}")
        return False
