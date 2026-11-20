# Interfaces de MotoControl Ubaté

Esta carpeta contiene las capturas de pantalla de las interfaces de la aplicación
(agréguelas como `.png` con el nombre indicado en la tabla).

Las plantillas HTML reales que genera cada pantalla están en `templates/`
(Flask exige esa carpeta) y los estilos en `static/style.css`.

| Pantalla | Ruta | Captura | Plantilla |
|---|---|---|---|
| Inicio | `/` | `01_inicio.png` | `templates/modulo.html` |
| Clientes | `/clientes` | `02_clientes.png` | `templates/modulo.html` |
| Motocicletas | `/motos` | `03_motos.png` | `templates/modulo.html` |
| Órdenes de servicio | `/ordenes` | `04_ordenes.png` | `templates/modulo.html` |
| Cola FIFO | `/cola` | `05_cola.png` | `templates/modulo.html` |
| Repuestos | `/repuestos` | `06_repuestos.png` | `templates/modulo.html` |
| Historial | `/historial` | `07_historial.png` | `templates/modulo.html` |
| Recordatorios | `/recordatorios` | `08_recordatorios.png` | `templates/modulo.html` |
| Consejos | `/consejos` | `09_consejos.png` | `templates/modulo.html` |

## Estructura común
- `templates/base.html`: encabezado con el menú de navegación y zona de mensajes.
- `templates/modulo.html`: plantilla genérica de cada módulo (formularios, tabla y lista).
