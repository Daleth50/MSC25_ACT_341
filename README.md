# Sistema de Gestión de Cuentas Bancarias

Sistema completo de gestión de cuentas bancarias con interfaz gráfica PyQt5, persistencia en MySQL, análisis de datos con Pandas y visualización con Matplotlib.

## Características

### Funcionalidades Principales
- ✅ **Gestión de Cuentas**: Crear, editar, eliminar y buscar cuentas bancarias
- ✅ **Tipos de Cuenta**: Soporte para cuentas normales y cuentas de crédito
- ✅ **Operaciones Bancarias**: Depósitos y retiros con validaciones
- ✅ **Base de Datos MySQL**: Persistencia completa de datos con sincronización automática
- ✅ **Importación/Exportación**: CSV y Excel (XLSX) con validaciones
- ✅ **Análisis de Datos**: Tres filtros avanzados con Pandas
- ✅ **Visualizaciones**: Cuatro tipos de gráficas con Matplotlib/Seaborn

### Filtros de Análisis (Pandas)
1. **Filtro por Rango de Balance**: Filtra cuentas entre un saldo mínimo y máximo
2. **Filtro por Tipo de Cuenta**: Filtra por cuentas normales, de crédito o todas
3. **Filtro por Fecha y Lugar**: Filtra por rango de fechas y/o ubicación geográfica

### Gráficas (Matplotlib/Seaborn)
1. **Histograma de Distribución de Saldos**: Muestra la distribución de saldos con estadísticas
2. **Gráfica de Pastel por Tipo**: Distribución por cantidad y saldo total
3. **Tendencia Temporal**: Análisis de apertura de cuentas en el tiempo
4. **Comparación de Crédito**: Balance vs límite de crédito en cuentas de crédito

## Requisitos del Sistema

- Python 3.8 o superior
- MySQL Server 5.7 o superior
- Sistema Operativo: Windows, macOS o Linux

## Instalación

### 1. Clonar o Descargar el Proyecto

```bash
cd /ruta/al/proyecto/MSC25_ACT_3.1
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar MySQL

#### 4.1 Instalar MySQL Server
- **Windows**: Descargar de [MySQL.com](https://dev.mysql.com/downloads/mysql/)
- **macOS**: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server`

#### 4.2 Iniciar MySQL

```bash
# macOS/Linux
sudo mysql.server start

# Windows (como servicio)
net start MySQL
```

#### 4.3 Crear la Base de Datos

Ejecutar el script SQL proporcionado:

```bash
mysql -u root -p < database/banco_schema.sql
```

O desde el cliente MySQL:

```sql
mysql -u root -p
source /ruta/completa/database/banco_schema.sql
```

Esto creará:
- Base de datos `banco_db`
- Tabla `cuentas` con índices optimizados
- 5 registros de ejemplo para pruebas

### 5. Configurar Credenciales de Base de Datos

Editar el archivo `config/database_config.ini`:

```ini
[mysql]
host = localhost
port = 3306
database = banco_db
user = root
password = TU_PASSWORD_AQUI
pool_size = 5
pool_name = banco_pool

[application]
csv_export_path = exports/
xlsx_export_path = exports/
default_balance = 1000.0
default_credit_limit = 500.0
```

**IMPORTANTE**: Reemplazar `password` con tu contraseña de MySQL.

## Uso del Sistema

### Ejecutar la Aplicación

```bash
cd pktCuentasUI
python main.py
```

### Operaciones Básicas

#### Agregar Cuenta
1. Clic en el botón **Agregar** o menú **Archivo → Agregar**
2. Completar formulario con datos del cliente
3. Seleccionar tipo de cuenta (Normal o Crédito)
4. Clic en **Agregar**

#### Buscar Cuenta
1. Clic en el botón **Buscar** o menú **Archivo → Buscar**
2. Ingresar número de cuenta
3. Ver detalles de la cuenta

#### Editar/Eliminar Cuenta
1. Doble clic en una fila de la tabla
2. Seleccionar operación deseada (Depositar, Retirar, Editar)
3. Para eliminar: seleccionar fila(s) y clic en **Eliminar**

### Importar/Exportar Datos

#### Importar desde CSV
1. Menú **Archivo → Importar CSV**
2. Seleccionar archivo CSV
3. El sistema validará y mostrará resultados (exitosos, duplicados, errores)

**Formato CSV requerido**:
```csv
no_cuenta,apellido_paterno,apellido_materno,nombre,balance,fecha,lugar,tipo_cuenta,limite_credito
1010,García,López,Juan,5000.00,2025-01-15,Ciudad de México,normal,0.00
1011,Martínez,Pérez,María,3000.00,2025-02-20,Guadalajara,credit,2000.00
```

#### Exportar a CSV/Excel
1. Menú **Archivo → Exportar CSV** o **Exportar Excel**
2. Elegir ubicación y nombre de archivo
3. Confirmar exportación

### Aplicar Filtros

#### Filtro por Balance
1. Menú **Análisis → Filtrar por Balance**
2. Ingresar balance mínimo y máximo
3. Ver resultados con estadísticas
4. Opcionalmente exportar resultados

#### Filtro por Tipo
1. Menú **Análisis → Filtrar por Tipo**
2. Seleccionar tipo de cuenta
3. Ver resultados

#### Filtro por Fecha/Lugar
1. Menú **Análisis → Filtrar por Fecha y Lugar**
2. Activar filtro de fechas y/o ingresar lugar
3. Ver resultados

### Visualizar Gráficas

1. Menú **Gráficas → [Tipo de Gráfica]**
2. Esperar generación de gráfica
3. Usar toolbar para zoom, pan, etc.
4. Guardar imagen (PNG, PDF, SVG)

## Estructura del Proyecto

```
MSC25_ACT_3.1/
├── config/
│   └── database_config.ini          # Configuración de BD
├── database/
│   └── banco_schema.sql              # Script SQL de inicialización
├── exports/                          # Carpeta para exportaciones (creada automáticamente)
├── Iconos/                           # Iconos de la interfaz
├── pktCuentas/                       # Lógica de negocio
│   ├── account.py                    # Clase Account base
│   ├── credit_account.py             # Clase CreditAccount
│   ├── bank_herencia.py              # Gestor de cuentas (actualizado)
│   ├── database_manager.py           # Gestor de MySQL (nuevo)
│   ├── data_manager.py               # Importar/Exportar CSV/XLSX (nuevo)
│   ├── analytics.py                  # Filtros con Pandas (nuevo)
│   └── charts.py                     # Gráficas con Matplotlib (nuevo)
├── pktCuentasUI/                     # Interfaz gráfica
│   ├── main.py                       # Ventana principal (actualizada)
│   ├── mwVentana.ui                  # Diseño Qt
│   ├── add_account_dialog.py        # Diálogo agregar/editar
│   ├── filter_dialogs.py            # Diálogos de filtros (nuevo)
│   └── results_dialogs.py           # Diálogos de resultados (nuevo)
├── requirements.txt                  # Dependencias Python
└── README.md                         # Este archivo
```

## Arquitectura del Sistema

### Patrón de Diseño
- **Singleton**: `DatabaseManager` usa patrón Singleton para gestión de conexiones
- **MVC**: Separación entre lógica de negocio (`pktCuentas`) y presentación (`pktCuentasUI`)
- **Pool de Conexiones**: MySQL connection pooling para rendimiento

### Flujo de Datos
1. **Usuario** → **UI (PyQt5)** → **Bank Manager** → **Database Manager** → **MySQL**
2. Sincronización automática entre memoria y base de datos
3. Validaciones en múltiples capas

### Mejores Prácticas Implementadas
✅ Separación de responsabilidades (SoC)
✅ Manejo robusto de excepciones
✅ Validación de datos en entrada
✅ Transacciones de BD con rollback
✅ Código documentado con docstrings
✅ Gestión de recursos (conexiones, cursores)
✅ Feedback visual al usuario (cursores de espera)
✅ Configuración externalizada (INI)

## Base de Datos

### Esquema de la Tabla `cuentas`

| Campo            | Tipo             | Descripción                    |
|------------------|------------------|--------------------------------|
| id               | INT (PK, AI)     | ID interno autoincremental     |
| no_cuenta        | INT (UNIQUE)     | Número de cuenta único         |
| apellido_paterno | VARCHAR(100)     | Apellido paterno del cliente   |
| apellido_materno | VARCHAR(100)     | Apellido materno del cliente   |
| nombre           | VARCHAR(100)     | Nombre del cliente             |
| balance          | DECIMAL(15,2)    | Saldo actual                   |
| fecha            | DATE             | Fecha de apertura              |
| lugar            | VARCHAR(200)     | Lugar de apertura              |
| tipo_cuenta      | ENUM             | 'normal' o 'credit'            |
| limite_credito   | DECIMAL(15,2)    | Límite de crédito (si aplica)  |
| created_at       | TIMESTAMP        | Fecha de creación del registro |
| updated_at       | TIMESTAMP        | Fecha de última actualización  |

### Índices
- `idx_no_cuenta`: Para búsquedas rápidas por número de cuenta
- `idx_tipo_cuenta`: Para filtros por tipo
- `idx_fecha`: Para filtros temporales
- `idx_apellido_paterno`: Para búsquedas por nombre

## Solución de Problemas

### Error: "No se pudo conectar a la base de datos"

**Causa**: MySQL no está corriendo o credenciales incorrectas

**Solución**:
1. Verificar que MySQL esté corriendo: `mysql.server status`
2. Verificar credenciales en `config/database_config.ini`
3. Probar conexión manual: `mysql -u root -p`

### Error: "Table 'cuentas' doesn't exist"

**Causa**: No se ejecutó el script SQL

**Solución**:
```bash
mysql -u root -p < database/banco_schema.sql
```

### Error al importar módulos de Python

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

### Gráficas no se muestran correctamente

**Causa**: Backend de matplotlib incorrecto

**Solución**:
```bash
pip install --upgrade matplotlib PyQt5
```

## Créditos

**Proyecto**: Sistema de Gestión de Cuentas Bancarias
**Curso**: MSC25 - Actividad 3.1
**Fecha**: Diciembre 2025
**Tecnologías**: Python 3, PyQt5, MySQL, Pandas, Matplotlib

## Licencia

Este proyecto es para fines educativos.

