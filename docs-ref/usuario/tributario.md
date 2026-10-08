# Fiscal y Tributario

El grupo **Fiscal y Tributario** concentra las obligaciones impositivas de la empresa según
la Ley 6380/2019 y la normativa de la DNIT/SET.

> ⚠️ **Manual del ERP traído como referencia.** Describe las pantallas del
> sistema, no lo que la landing puede prometer: para eso manda `content.md`.

## Libro IVA

**Fiscal y Tributario > Libro IVA** registra el IVA débito (ventas) y crédito (compras) del
período. Es un reporte **base**, siempre disponible.

## Retenciones

**Fiscal y Tributario > Retenciones** administra las retenciones de IVA y Renta. Reporte
**base**, siempre disponible.

## Liquidación y Declaraciones (DDJJ)

> Disponibles si la empresa tiene activado el módulo **Tributario**.

- **Liquidación** — calcula la obligación de IRE o IDU del período. El **IRP
  está pendiente**: el liquidador aplica tasas planas (10 % servicios, 8 %
  capital) sin la escala por tramos y suma las retenciones sin distinguir
  categoría, y el propio código lo marca como trabajo sin terminar. **Queda
  afuera de la landing.**
- **Declaraciones (DDJJ)** — genera las declaraciones juradas y las deja listas
  para presentar. **La presentación ante la SET no está verificada**: no se
  promete en la landing hasta que haya una subida real aceptada.

> Requieren los permisos **Ejecutar liquidaciones** y **Crear/presentar DDJJ**.

## Otros (módulo Tributario)

- **Pagos de Impuestos** — registro de pagos a la SET.
- **Distribución de Utilidades** y **Pérdidas Fiscales**.
- **Ajustes Fiscales**.

## Activos Fiscales

> Disponible si la empresa tiene activado el módulo **Activos Fiscales**.

En **Fiscal y Tributario > Activos Fiscales** se cargan los bienes de uso, con su tipo, vida
útil, valor residual y método de depreciación (Decreto 3182/2019). El alta del activo y la
depreciación periódica generan asientos contables automáticos. Los catálogos editables están
en **Tipos de Activo** y **Métodos Deprec.**

## Registro Marangatú

> Disponible si la empresa tiene activado el módulo **Marangatú**.

Exporta los registros de compras y ventas en el formato requerido por el sistema Marangatú
de la SET.
