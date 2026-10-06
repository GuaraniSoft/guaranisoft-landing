# Guía: mantener el sitio despierto en Render Free

> Por qué el sitio tarda en abrir después de un rato sin visitas, y cómo lo resolvimos sin pagar.
> Decidido con Victor el 06/10/2026.

---

## El problema

Render apaga un servicio del plan **Free** cuando pasa **15 minutos sin recibir tráfico**. El siguiente
visitante dispara el arranque y espera entre **30 segundos y 1 minuto** con la pantalla en blanco.

Para una landing es caro: el que llega desde un anuncio o desde un link de WhatsApp es justo el que no
va a esperar.

## El límite que de verdad manda: 750 horas

Render regala **750 horas de instancia por workspace y por mes** (no por servicio: por *workspace*).
Un servicio despierto las 24 horas consume:

| Mes | Horas | De 750 |
|---|---|---|
| 30 días | 720 h | queda margen de 30 h |
| 31 días | 744 h | queda margen de **6 h** |

Y el detalle importante: **si se agotan las horas, Render suspende todos los servicios Free del
workspace hasta el primer día del mes siguiente.** Por eso no lo mantenemos despierto las 24 horas: si
algún día sumamos un segundo servicio Free, un mes de 31 días nos deja sin sitio.

## La solución: un ping en horario comercial

Un servicio externo gratis le pega a `/health` cada 10 minutos, **de 7:15 a 21:00 hora de Paraguay**.

- **Consumo:** ~13 h 50 min por día → **unas 428 horas al mes de las 750**.
- **Fuera de la ventana** (21:00 a 7:15) el sitio duerme. Si entra alguien de madrugada, espera el
  arranque. Es el precio de no gastar el pozo.

### Por qué cada 10 minutos y no cada 14

Render apaga a los 15 minutos de inactividad. Con 10 minutos, si un ping falla o se atrasa, el
siguiente todavía llega antes del apagado. Con 14 no hay segunda oportunidad.

### Por qué `/health` y no la portada

`/health` (en `main.py`) devuelve `{"status": "ok"}` en 15 bytes, sin tocar Google Sheets ni SQLite ni
renderizar plantillas. Pegarle a la portada funcionaría igual, pero gasta más de todo sin ningún
beneficio.

---

## Configuración en cron-job.org

1. Cuenta gratis en [cron-job.org](https://cron-job.org) → **Create cronjob**.
2. **URL:** `https://guaranisof.com/health`
3. **Zona horaria del job: `America/Asuncion`.** Así se cargan los horarios tal cual, sin convertir a
   UTC y sin depender de que Paraguay no vuelva a tener horario de verano.
4. Se crean **dos** jobs, porque el primer ping va a las 7:15 y los demás caen en minutos redondos
   (con un solo job el primero saldría 7:05):

| | Job 1 — el arranque | Job 2 — el resto del día |
|---|---|---|
| Minutos | 15, 25, 35, 45, 55 | 0, 10, 20, 30, 40, 50 |
| Horas | 7 | 8 a 20 |
| Días | todos | todos |

En expresión cron, siempre en hora de Paraguay:

```
15,25,35,45,55 7 * * *      # primer ping 7:15
*/10 8-20 * * *             # cada 10 min hasta las 20:50
```

El último ping de 20:50 mantiene el sitio despierto hasta cerca de las 21:05.

5. Activar el **aviso por mail ante fallo**. Como le pega cada 10 minutos, si el sitio se cae te
   enterás mucho antes que por un cliente.

> Si el servicio que uses solo trabaja en UTC: Paraguay es UTC−3, así que la ventana es de **10:15 a
> 00:00 UTC** (`15,25,35,45,55 10 * * *` y `*/10 11-23 * * *`).

---

## Cómo verificar que funciona

- Abrir el sitio a las 9 de la mañana: tiene que responder al instante, sin la pausa del arranque.
- `curl -s -o /dev/null -w "%{time_total}\n" https://guaranisof.com/health` dentro de la ventana:
  despierto da menos de 1 segundo; dormido, 30 segundos o más.
- En el panel de Render, las métricas del servicio no deberían mostrar apagados entre las 7:15 y
  las 21:00.

---

## Alternativas que descartamos

| Opción | Por qué no |
|---|---|
| **Cron Job de Render** | Los cron jobs de Render se cobran aparte y consumen del mismo workspace. |
| **GitHub Actions** | Un ping cada 10 minutos son ~4.300 ejecuciones al mes y Actions factura por minuto arrancado: se pasa de los 2.000 minutos gratis. Además GitHub desactiva los workflows programados si el repo queda inactivo. |
| **Cron en la PC de Victor** | Solo funciona con la computadora prendida. |
| **Worker de Cloudflare** | Gratis y en infraestructura propia (el dominio ya está en Cloudflare), pero hay que instalar Node y wrangler y hacer un login interactivo. Queda como plan B si algún día no queremos depender de un tercero. |

## Cuándo dejar de hacer todo esto

El plan **Starter de Render (US$ 7 por mes)** no se duerme nunca y no tiene tope de horas. En ese
momento se borran los dos cron jobs y esta guía queda como historia. Mientras la landing sea de bajo
tráfico, el ping alcanza.
