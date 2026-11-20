# MotoControl Ubaté

Aplicación web para la gestión de un taller de motocicletas en Ubaté (Cundinamarca).

**Integrantes:** _(escriba aquí los nombres del equipo)_

## Objetivo del proyecto
Controlar de forma sencilla la operación de un taller de motos: registrar clientes y
motocicletas, atender las órdenes de servicio en orden de llegada, llevar el historial
de mantenimiento, controlar el inventario de repuestos y programar recordatorios de
mantenimiento preventivo.

## Tecnologías
- Python 3 y Flask (servidor web)
- MySQL / MariaDB de XAMPP (base de datos)
- HTML con plantillas Jinja y CSS

## Instrucciones de ejecución
1. Instale Python 3 y XAMPP. En XAMPP inicie solo el módulo **MySQL**.
2. Clone el repositorio y entre a la carpeta del proyecto:
   ```powershell
   git clone https://github.com/USUARIO/REPOSITORIO.git
   cd REPOSITORIO
   ```
3. Instale las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
4. Cree la base de datos y las tablas (solo la primera vez):
   ```powershell
   python init_db.py
   ```
5. Inicie la aplicación:
   ```powershell
   python app.py
   ```
6. Abra http://127.0.0.1:5000 en el navegador. La aplicación no requiere inicio de sesión.

Si MySQL tiene contraseña para `root`, defínala antes de ejecutar:
```powershell
$env:DB_PASS = "su_contraseña"
```
Otras variables opcionales: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`.

## Estructura del proyecto
```
app.py            rutas y lógica de la aplicación
modelos.py        clases POO (Entidad, Cliente, Motocicleta, Repuesto, OrdenServicio, Recordatorio)
tad.py            TAD Cola FIFO con nodos enlazados (órdenes pendientes)
db.py             clase BaseDatos (conexión a MySQL)
init_db.py        crea la base de datos y las tablas
schema.sql        definición de las tablas
templates/        plantillas HTML (Jinja)
static/           hoja de estilos
interfaces/       capturas y descripción de las interfaces
BITACORA.md       bitácora de commits
```

## Descripción de módulos
| Módulo | Ruta | Descripción |
|---|---|---|
| Inicio | `/` | Pantalla de bienvenida. |
| Clientes | `/clientes` | Registra y lista clientes (nombre, teléfono, correo). |
| Motos | `/motos` | Registra motocicletas asociadas a un cliente; la placa es única. |
| Órdenes | `/ordenes` | Crea órdenes de servicio, atiende la siguiente orden (FIFO) y registra el trabajo realizado, lo que finaliza la orden y actualiza el kilometraje. |
| Cola | `/cola` | Muestra las órdenes pendientes en el orden en que serán atendidas (TAD cola FIFO). |
| Repuestos | `/repuestos` | Registra repuestos y entradas de unidades al inventario. |
| Historial | `/historial` | Consulta los trabajos realizados, con filtro por motocicleta. |
| Recordatorios | `/recordatorios` | Programa mantenimientos por fecha y kilometraje (el km objetivo no puede ser menor al actual). |
| Consejos | `/consejos` | Consejos de mantenimiento preventivo. |

### Flujo de uso recomendado
Cliente → Moto → Orden de servicio → Atender siguiente (pasa a "En proceso") →
Registrar trabajo realizado (orden "Finalizada") → Consultar historial → Crear recordatorio.

## Problemas encontrados y soluciones aplicadas
> Edite esta sección con los problemas reales de su equipo.

| Problema | Solución |
|---|---|
| Error de conexión a la base de datos al iniciar la app. | MySQL no estaba iniciado en XAMPP; se inició el módulo MySQL y se volvió a ejecutar. |
| `python init_db.py` o `pip install -r requirements.txt` fallaban por "archivo no encontrado". | Se estaba ejecutando desde la carpeta superior; hay que entrar a la carpeta del proyecto con `cd` antes de ejecutar. |
| PowerShell interpretaba una ruta o el texto `PS C:\...>` como comando. | Escribir solo el comando (sin copiar el prompt) y usar `cd` para cambiar de carpeta. |
| Error al guardar una moto: dato repetido. | La placa es única en la base de datos; se muestra un mensaje claro al usuario en lugar de un error. |
| El inicio de sesión y los roles complicaban el uso y las pruebas. | Se eliminó el login, los roles y la tabla `usuarios`; todos los módulos quedan disponibles. |
