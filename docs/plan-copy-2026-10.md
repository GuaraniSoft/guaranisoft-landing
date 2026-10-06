# Plan de cambios de copy — guaranisof.com (05/10/2026)

Encargo: `docs/encargo-copy-2026-10-05.md` (aprobado por Victor, sesión de marketing del 05/10/2026).
Rama: `cambios-copy-2026-10`. Orden de aplicación: sección 1 → 2 y 3 → el resto.

Mapa: `/` → `templates/home.html` · `/nande-erp` → `templates/index.html` · `/nande-tienda` → `templates/nande-tienda.html`.
Las líneas son las del estado inicial de la rama (commit base `e9079d8`) y se corren a medida que se aplica cada sección.

## Reglas de esta tarea
- Solo textos, links y las secciones que el encargo manda borrar. Nada de diseño, estilos ni imágenes.
- Nada de "No hacer todavía" (horarios de soporte, ejemplo farmacia, sucursales sin internet, IRE/IDU/IRP/RESIMPLE/Marangatú de `index.html:308`, hero de la home).
- Sin push a `main` ni deploy. Render despliega solo con push a `main`.

---

## Sección 1 — /nande-erp: sacar SIFEN como función terminada (URGENTE) · `templates/index.html`

- [x] 1.1 L88 h1: "Controlá tu negocio. Dormí tranquilo con la DNIT." → "Controlá tu negocio, aunque se corte internet."
- [x] 1.1 L89-93 subtítulo → "Ventas, stock, caja y contabilidad conectados, para una o varias empresas, con sus sucursales y depósitos. Y si algo falla, te atiende directo quien lo programó." (botones y "1 mes de prueba" L96-104 intactos)
- [x] 1.2 L135 → "Hecho para la realidad comercial y fiscal de Paraguay, no adaptado de otro país."
- [x] 1.3 L142 → "Tu operación sigue aunque se corte la conexión." (saco "Sincroniza SIFEN al volver.")
- [x] 1.4 L178-181 borrar etiqueta "Integración SIFEN" · **duda A**: ¿borro también la etiqueta "Ley 6380/2019" (L170-173)?
- [x] 1.5 L227 respuesta → "La sumamos a pedido a tu Ñande ERP. Contanos cuándo te toca y vemos los plazos juntos." (pregunta L226 igual)
- [x] 1.6 L327-340 reemplazar "SIFEN sin dolores de cabeza" por: título "Facturación electrónica, cuando la necesites" + texto nuevo + botón "Consultá por WhatsApp" → link *Facturación electrónica*
- [x] 1.7 L454 → "Si se corta internet no parás: seguís cargando ventas."
- [x] 1.8 L700 → "No. El sistema corre en tu computadora: si se corta internet, seguís vendiendo normalmente."
- [x] 1.9 L6 meta description → "Sistema de gestión para PyMEs en Paraguay. Punto de venta rápido, control de stock, cajas y contabilidad. Funciona sin internet." · **duda B**: el mismo texto se repite en el JSON-LD (L25)

## Sección 2 — /nande-erp: precios · `templates/index.html` L552-621

- [x] Reemplazar h2 "Plan Fundador" (L557) + subtítulo (L558) + toda la tarjeta `precios-fundador` (L560-609: "Cupos limitados", "Plan Fundador — 70% off", montos, "Te ahorrás", cuotas, lista de 6 ítems, 2 botones) + el párrafo "Después de los cupos fundadores…" (L615)
- [x] Contenido nuevo: "¿Cuánto cuesta? Depende de tu negocio." + los 6 párrafos del encargo (precio según empresas/sucursales/módulos/migración · pago único · soporte mensual · 1 mes sin costo · empresas fundadoras · facturación electrónica a pedido)
- [x] Un solo botón: "Pedí tu precio por WhatsApp" → link *Precios ERP*, con "Te respondemos por escrito." debajo. Sacar "Solicitar demo" de esta sección
- [x] Conservar la línea de Ñande Tienda (L617-619)

## Sección 3 — /nande-erp: preguntas frecuentes · `templates/index.html` L624-716

- [x] L629 subtítulo → "Respuestas al grano"
- [x] Agregar como primera: "¿Cuánto cuesta Ñande ERP?" (id `faq0`, para no renumerar el resto)
- [x] L632-643 "¿El precio de la licencia es pago único o anual?" → "¿Es pago único?" + respuesta nueva (incluye hora de soporte Gs. 100.000)
- [x] L652 respuesta de "¿Cuántas computadoras puedo conectar?" → "Todas las que necesites: las computadoras y los depósitos no suman costo. El precio cambia solo según cuántas empresas y sucursales manejás."
- [x] Agregar después: "¿Sirve si tengo más de una empresa?" (id `faq2b`)

## Sección 4 — /nande-erp: varias empresas · `templates/index.html` L149

- [x] → "Una o varias empresas, con todas sus sucursales y depósitos, en el mismo sistema. Ventas, stock, caja y contabilidad conectados."

## Sección 5 — frases que suponen clientes

- [x] `index.html` L126 → "Por qué Ñande ERP"
- [x] `index.html` L127 → "Cuatro razones para probarlo"
- [x] `index.html` L350 → "Así se usa en tu rubro"
- [x] `nande-tienda.html` L436 → "Respuestas al grano"

## Sección 6 — /nande-erp: "¿Quién está detrás?" · `templates/index.html` L531-545

- [x] L532 h3 → "¿Quién te atiende?"
- [x] L533-544 los dos párrafos → el párrafo en primera persona del encargo
- [x] L545 botón "Hablar con nosotros" → "Escribime por WhatsApp", link *ERP, bloque de Victor*
- [x] Foto/iniciales (L526-530) sin tocar

## Sección 7 — /nande-erp: borrados

- [x] L384-433 toda la sección "El antes y el después de tener Ñande ERP" (no tiene link en el menú)
- [x] L468-502 bloque de 4 ítems "Instalación local / Backup automático / Cumplimiento fiscal real / Soporte sin bots". Ojo: es una `<section aria-label="Garantías del sistema">` aparte, después de "Tu puesta en marcha", no dentro. Los 3 pasos (L442-464) quedan

## Sección 8 — Home · `templates/home.html`

- [x] 8.1 L72 borrar botón "Conocé Ñande Tienda"
- [x] 8.1 L85-108 las 4 cifras → 3: "Sin internet / Seguís vendiendo aunque se corte la conexión", "0 call centers / Te responde quien lo programó", "1 mes de prueba / Sin costo, en tu negocio" · **duda C** (clases de grilla)
- [x] 8.2 L44 (menú) y L117 (h2): "Quiénes somos" → "Quién está detrás" (el ancla `#quienes-somos` se deja para no romper links)
- [x] 8.2 L127-144 h3 "Lic. Victor Román — Fundador" + 3 párrafos → el párrafo nuevo en primera persona
- [x] 8.2 L145 botón → "Escribime por WhatsApp" (link *Home, bloque de Victor*) + link chico "Mi perfil en LinkedIn" → https://www.linkedin.com/in/victor-roman-226bb155/
- [x] 8.2 L166-184 borrar "Números que nos respaldan" · **duda C**
- [x] 8.2 L161 `tel:+595992504620` → `https://wa.me/595992504620`
- [x] 8.3 L189-227 borrar sección "Por qué GuaraníSoft" + su link del menú (L45)
- [x] 8.3 L262-348 borrar "Qué incluye Ñande ERP" (ahí se va también la celda "SIFEN · Facturación electrónica")
- [x] 8.4 L361-393 formulario + nota "¿Querés una demo personalizada…?" → botón grande "Escribinos por WhatsApp" → link *Home, contacto*
- [x] 8.4 L407-410 borrar el `<li>` de LinkedIn (quedan correo y WhatsApp)
- [x] 8.4 L426-436 borrar el `page_scripts` que inicializa ese formulario, o la página tira error de JS · **duda D**. `POST /contacto` en `main.py` queda intacto: lo usa el formulario de /nande-erp

## Sección 9 — /nande-tienda: precios · `templates/nande-tienda.html` L347-428

- [x] Reemplazar h2 "Plan Fundador Tienda" (L352) + subtítulo "Precio fundador de por vida" (L353) + toda la tarjeta (L355-420: "Cupos limitados", las 3 cajas de montos, "de por vida", lista de 6 ítems, 2 botones)
- [x] Contenido nuevo: "¿Cuánto cuesta?" + párrafo (se cotiza con el ERP; nube con mensualidad fija o PC con pago único; sin comisión por venta) + botón "Consultá por WhatsApp" → link *Tienda, precio*
- [x] L425 borrar "Después de los cupos fundadores… pago único en tu computadora." y conservar "¿Todavía no tenés Ñande ERP? Empezá por ahí…"
- [x] L28 JSON-LD con los precios viejos · **duda B**

---

## Links de WhatsApp (usar exactamente estos)

| Uso | URL |
|---|---|
| Precios ERP | `https://wa.me/595992504620?text=Hola%2C%20quiero%20saber%20cu%C3%A1nto%20me%20sale%20%C3%91ande%20ERP.%20Mi%20negocio%20es%3A%20` |
| Facturación electrónica | `https://wa.me/595992504620?text=Hola%2C%20me%20toca%20la%20facturaci%C3%B3n%20electr%C3%B3nica%20y%20quiero%20saber%20si%20%C3%91ande%20ERP%20me%20sirve.` |
| Home, bloque de Victor | `https://wa.me/595992504620?text=Hola%20Victor%2C%20vi%20la%20p%C3%A1gina%20de%20Guaran%C3%ADSoft%20y%20quiero%20hacerte%20una%20consulta.` |
| ERP, bloque de Victor | `https://wa.me/595992504620?text=Hola%20Victor%2C%20tengo%20una%20consulta%20sobre%20%C3%91ande%20ERP.` |
| Home, contacto | `https://wa.me/595992504620?text=Hola%2C%20quiero%20hablar%20sobre%20mi%20empresa.` |
| Tienda, precio | `https://wa.me/595992504620?text=Hola%2C%20quiero%20saber%20el%20precio%20de%20%C3%91ande%20Tienda.` |

## Dudas resueltas (OK de Victor, 06/10/2026)

- **A — Etiquetas destacadas (1.4).** Resuelto: se borran las dos, "Integración SIFEN" y "Ley 6380/2019".
  Quedan "Punto de Venta Rápido" e "Inventario Centralizado". La Ley 6380 sigue nombrada en el módulo
  Tributario, así que el dato no se pierde.
- **B — JSON-LD con precios y SIFEN.** Resuelto: se actualiza la `description` con el texto nuevo y se
  borran los bloques `offers` de las dos páginas (`index.html` publicaba `price: 4500000`;
  `nande-tienda.html`, el Plan Fundador). El precio ya no es público, se cotiza.
- **C — Grillas con huecos.** Resuelto: las 3 cifras de la home pasan a `col-6 col-md-4` (se reparten
  el ancho y en celular siguen de dos en dos, como antes). "Dónde estamos" queda en su `col-md-5`, sin
  tocar la fila.
- **D — JS del formulario de la home.** Resuelto: se borra el bloque `page_scripts` de `home.html`.
  `POST /contacto` en `main.py` queda intacto (lo usan /nande-erp y /nande-tienda).

## Agregados de esta sesión (06/10/2026)

- Comentarios HTML que quedaban desfasados tras los cambios: "Quiénes somos" → "Quién está detrás"
  (`home.html`), "¿Quién está detrás?" → "¿Quién te atiende?" (`index.html`), "Donde estamos + Numeros"
  → "Donde estamos".
- `.claude/skills/marketing-nande-erp/SKILL.md`: copia de la skill de marketing en el repo, con tres
  correcciones para que no contradiga este encargo (SIFEN pasa a "se implementa a pedido", mensaje
  núcleo sin facturación electrónica como eje, y el dominio corregido a guaranisof.com).
- Entorno: acceso a GitHub por SSH (`git@github.com:GuaraniSoft/guaranisoft-landing.git`) en lugar de
  HTTPS + `gh`.

## Al cerrar

- [x] Lista final: página, sección, antes → después, y lo que no se pudo aplicar
- [x] Búsqueda en todo el sitio de "SIFEN", "Dormí tranquilo", "70%", "Cupos limitados", "de por vida" y "equipo", e informe de dónde quedó alguno
