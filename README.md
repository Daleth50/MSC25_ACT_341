# Sistema de Gestión de Cuentas Bancarias

Sistema completo para la gestión de cuentas bancarias con interfaz gráfica PyQt5, persistencia en MySQL, análisis de datos con Pandas y visualización con Matplotlib.

## Características

### Funcionalidades principales
- Gestión de cuentas: crear, editar, eliminar y buscar cuentas bancarias
- Tipos de cuenta: soporte para cuentas normales y de crédito
- Operaciones bancarias: depósitos y retiros con validaciones
- Base de datos MySQL: persistencia total y sincronización automática
- Importación/Exportación: archivos CSV y Excel (XLSX) con validaciones
- Análisis de datos: tres filtros avanzados usando Pandas
- Visualización: cuatro tipos de gráficas con Matplotlib/Seaborn

### Filtros de análisis (Pandas)
1. Filtro por rango de saldo: filtra cuentas entre un saldo mínimo y máximo
2. Filtro por tipo de cuenta: filtra por cuentas normales, de crédito o todas
3. Filtro por fecha y lugar: filtra por rango de fechas y/o ubicación geográfica

### Gráficas (Matplotlib/Seaborn)
1. Histograma de distribución de saldos
2. Gráfica de pastel por tipo de cuenta
3. Tendencia temporal de apertura de cuentas
4. Comparación de saldo vs límite de crédito en cuentas de crédito

## Requisitos del sistema

- Python 3.8 o superior
- MySQL Server 5.7 o superior
- Sistema operativo: Windows, macOS o Linux

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd /ruta/al/proyecto/MSC25_ACT_3.1
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar MySQL

#### 4.1 Instalar MySQL Server
- Windows: Descargar desde [MySQL.com](https://dev.mysql.com/downloads/mysql/)
- macOS: `brew install mysql`
- Linux: `sudo apt-get install mysql-server`

#### 4.2 Iniciar MySQL

```bash
# macOS/Linux
sudo mysql.server start

# Windows (como servicio)
net start MySQL
```

#### 4.3 Crear la base de datos

Ejecuta el script SQL proporcionado:

```bash
mysql -u root -p < database/banco_schema.sql
```

O desde el cliente de MySQL:

```sql
mysql -u root -p
source /ruta/completa/database/banco_schema.sql
```

Esto crea:
- Base de datos `banco_db`
- Tabla `accounts` con índices optimizados
- 5 registros de ejemplo para pruebas

### 5. Configurar credenciales de la base de datos

Edita `config/database_config.ini`:

```ini
[mysql]
host = localhost
port = 3306
database = banco_db
user = root
password = TU_CONTRASEÑA_AQUÍ
pool_size = 5
pool_name = banco_pool

[application]
csv_export_path = exports/
xlsx_export_path = exports/
default_balance = 1000.0
default_credit_limit = 500.0
```

**IMPORTANTE**: Reemplaza `password` por tu contraseña de MySQL.

## Uso del sistema

### Ejecutar la aplicación

```bash
cd pktCuentasUI
python main.py
```

### Operaciones básicas

#### Agregar cuenta
1. Haz clic en **Agregar** o en el menú **Archivo → Agregar**
2. Llena el formulario del cliente
3. Selecciona el tipo de cuenta (Normal o Crédito)
4. Haz clic en **Agregar**

#### Buscar cuenta
1. Haz clic en **Buscar** o en el menú **Archivo → Buscar**
2. Ingresa el número de cuenta
3. Visualiza los detalles de la cuenta

#### Editar/Eliminar cuenta
1. Haz doble clic en una fila de la tabla
2. Selecciona la operación deseada (Depositar, Retirar, Editar)
3. Para eliminar: selecciona la(s) fila(s) y haz clic en **Eliminar**

### Importar/Exportar datos

#### Importar desde CSV
1. Menú **Archivo → Importar CSV**
2. Selecciona el archivo CSV
3. El sistema validará y mostrará los resultados (éxito, duplicados, errores)

**Formato requerido de CSV**:
```csv
account_no,last_name,middle_name,first_name,balance,date,location,account_type,credit_limit
1010,Garcia,Lopez,Juan,5000.00,2025-01-15,Mexico City,normal,0.00
1011,Martinez,Perez,Maria,3000.00,2025-02-20,Guadalajara,credit,2000.00
```

#### Exportar a CSV/Excel
1. Menú **Archivo → Exportar CSV** o **Exportar Excel**
2. Elige ubicación y nombre de archivo
3. Confirma la exportación

### Aplicar filtros

#### Filtro por saldo
1. Menú **Análisis → Filtrar por Balance**
2. Ingresa el saldo mínimo y máximo
3. Visualiza los resultados y estadísticas
4. Opcionalmente exporta los resultados

#### Filtro por tipo
1. Menú **Análisis → Filtrar por Tipo**
2. Selecciona el tipo de cuenta
3. Visualiza los resultados

#### Filtro por fecha/lugar
1. Menú **Análisis → Filtrar por Fecha y Lugar**
2. Activa el filtro de fechas y/o ingresa el lugar
3. Visualiza los resultados

### Visualizar gráficas

1. Menú **Gráficas → [Tipo de gráfica]**
2. Espera la generación de la gráfica
3. Guarda la imagen (PNG, PDF, SVG)

## Estructura del proyecto

```
MSC25_ACT_3.1/
├── config/
│   └── database_config.ini          # Configuración de la base de datos
├── database/
│   └── banco_schema.sql            # Script de inicialización SQL
├── exports/                        # Carpeta de exportación (se crea automáticamente)
├── Iconos/                         # Iconos de la interfaz
├── pktCuentas/                     # Lógica de negocio
│   ├── account.py                  # Clase base de cuenta
│   ├── credit_account.py           # Clase de cuenta de crédito
│   ├── bank_herencia.py            # Gestor de cuentas
│   ├── database_manager.py         # Gestor MySQL
│   ├── data_manager.py             # Importación/exportación CSV/XLSX
│   ├── analytics.py                # Filtros con Pandas
│   └── charts.py                   # Gráficas con Matplotlib
├── pktCuentasUI/                   # Interfaz gráfica
│   ├── main.py                     # Ventana principal
│   ├── mwVentana.ui                # Diseño Qt
│   ├── add_account_dialog.py       # Diálogo de agregar/editar
│   ├── filter_dialogs.py           # Diálogos de filtros
│   └── results_dialogs.py          # Diálogos de resultados
├── requirements.txt                # Dependencias de Python
└── README.md                       # Este archivo
```

## Arquitectura del sistema

### Patrones de diseño
- Singleton: `DatabaseManager` usa Singleton para la gestión de conexiones
- MVC: Separación entre lógica de negocio (`pktCuentas`) y presentación (`pktCuentasUI`)
- Pool de conexiones: Pool de conexiones MySQL para mejor rendimiento

### Flujo de datos
1. Usuario → Interfaz (PyQt5) → Gestor de cuentas → Gestor de base de datos → MySQL
2. Sincronización automática entre memoria y base de datos
3. Validaciones en múltiples capas

### Buenas prácticas
- Separación de responsabilidades
- Manejo robusto de excepciones
- Validación de datos de entrada
- Transacciones con rollback
- Código documentado con docstrings
- Gestión de recursos (conexiones, cursores)
- Retroalimentación visual al usuario
- Configuración externa (INI)

## Base de datos

### Esquema de la tabla `accounts`

| Campo            | Tipo             | Descripción                    |
|------------------|------------------|--------------------------------|
| id               | INT (PK, AI)     | ID interno autoincremental     |
| account_no       | INT (UNIQUE)     | Número de cuenta único         |
| last_name        | VARCHAR(100)     | Apellido paterno del cliente   |
| middle_name      | VARCHAR(100)     | Apellido materno del cliente   |
| first_name       | VARCHAR(100)     | Nombre del cliente             |
| balance          | DECIMAL(15,2)    | Saldo actual                   |
| date             | DATE             | Fecha de apertura              |
| location         | VARCHAR(200)     | Lugar de apertura              |
| account_type     | ENUM             | 'normal' o 'credit'            |
| credit_limit     | DECIMAL(15,2)    | Límite de crédito (si aplica)  |
| created_at       | TIMESTAMP        | Fecha de creación              |
| updated_at       | TIMESTAMP        | Fecha de última actualización  |

### Índices
- `idx_account_no`: Búsqueda rápida por número de cuenta
- `idx_account_type`: Filtros por tipo
- `idx_date`: Filtros temporales
- `idx_last_name`: Búsqueda por nombre

## Solución de problemas

### Error: "No se puede conectar a la base de datos"

**Causa**: MySQL no está corriendo o credenciales incorrectas

**Solución**:
1. Verifica que MySQL esté corriendo: `mysql.server status`
2. Verifica credenciales en `config/database_config.ini`
3. Prueba la conexión manual: `mysql -u root -p`

### Error: "La tabla 'accounts' no existe"

**Causa**: No se ejecutó el script SQL

**Solución**:
```bash
mysql -u root -p < database/banco_schema.sql
```

### Error de importación de módulos Python

**Causa**: No se instalaron las dependencias

**Solución**:
```bash
pip install -r requirements.txt
```

### Las gráficas no se muestran correctamente

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
