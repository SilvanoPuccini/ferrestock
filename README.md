# FerreStock — Proyecto Final 1 Django | Conquer Blocks

### 👤 Información del Estudiante

| Campo | Detalle |
|-------|---------|
| **Nombre** | Silvano Puccini |
| **Curso** | Desarrollo Web - Django |
| **Academia** | ConquerBlocks |
| **Módulo** | Django Inicial |
| **Fecha** | Marzo 2026 |

---

### 🌐 Enlaces de Entrega

🔗 **Repositorio:**  
[https://github.com/SilvanoPuccini/ferrestock](https://github.com/SilvanoPuccini/ferrestock)

🚀 **Demo en vivo:**  
[Agregar aquí el enlace público del deploy](https://tu-demo-publica.com)

---

## 📌 Descripción

**FerreStock** es un sistema de inventario profesional desarrollado con **Django** para una ferretería, corralón o negocio con control de stock, compras y movimientos.

El proyecto fue realizado como entrega del módulo de **Django (backend)** en **ConquerBlocks**, tomando como base los contenidos vistos en clase y evolucionándolos hacia una solución más cercana a un producto real.

La aplicación permite gestionar productos, categorías, proveedores, movimientos de stock, órdenes de compra, importación masiva por CSV, dashboard con métricas y gráficos, reportes exportables y control de acceso por roles.

---

## 🎯 Objetivo de la entrega

Aplicar los conceptos del módulo de Django sobre un proyecto completo, poniendo en práctica:

- Entorno de desarrollo profesional con Django.
- Arquitectura **MVT**.
- Modelos y relaciones entre entidades.
- Queries y filtros.
- Formularios y ModelForms.
- Templates y vistas.
- CRUDs completos.
- Gestión de stock.
- Reportes exportables.
- Roles y permisos.
- Organización de proyecto orientada a una entrega seria y escalable.

---

## 🛠️ Stack Tecnológico

- Python 3.12
- Django 5
- PostgreSQL
- Bootstrap 5
- Pillow
- django-environ
- openpyxl
- reportlab

---

## ✅ Funcionalidades principales

- Gestión de productos
- Gestión de categorías
- Gestión de proveedores
- Movimientos de stock:
  - entrada
  - salida
  - ajuste
- Alertas de stock bajo
- Relaciones producto-proveedor
- Órdenes de compra
- Recepción de órdenes con actualización automática de stock
- Importación masiva por CSV
- Dashboard con métricas y gráficos
- Reportes exportables en:
  - CSV
  - Excel
  - PDF
- Sistema de roles:
  - Administrador
  - Operador
  - Consulta
- Auditoría básica de acciones sensibles
- Tests automáticos

---

## 👥 Roles del sistema

### Administrador
Acceso completo al sistema.

### Operador
Puede registrar movimientos y trabajar con compras, pero no gestiona configuración crítica.

### Consulta
Puede visualizar stock, movimientos, compras y reportes, sin modificar datos.

---

## 👨‍💻 Usuarios demo

Después de ejecutar los comandos de setup, el sistema genera estos usuarios de prueba:

- `admin_demo` / `Admin12345!`
- `operador_demo` / `Operador12345!`
- `consulta_demo` / `Consulta12345!`

---

## 📍 Módulos principales del sistema

### Inventario
- Productos
- Categorías
- Stock actual
- Stock mínimo
- Filtros y búsqueda

### Movimientos
- Registro de entradas
- Registro de salidas
- Ajustes
- Historial de movimientos

### Proveedores y compras
- Gestión de proveedores
- Relación producto-proveedor
- Órdenes de compra
- Recepción de compras

### Reportes
- Reporte de stock
- Reporte de movimientos
- Reporte de compras

### Seguridad y control
- Roles y permisos
- Auditoría básica
- Restricción de acciones por perfil

---

## 🧱 Estructura funcional del proyecto

```bash
ferrestock/
├── apps/
│   ├── core/
│   ├── dashboard/
│   ├── inventory/
│   ├── movements/
│   ├── reports/
│   └── suppliers/
├── config/
├── docs/
├── media/
├── static/
├── templates/
├── .env.example
├── manage.py
├── README.md
└── requirements.txt
```
```
📂 Organización por apps

apps/inventory: productos y categorías

apps/suppliers: proveedores y compras

apps/movements: movimientos de stock

apps/dashboard: panel principal

apps/reports: reportes exportables

apps/core: utilidades, auditoría y roles
```
```
⚙️ Instalación local

1. Clonar el repositorio
git clone https://github.com/SilvanoPuccini/ferrestock.git
cd ferrestock

2. Crear y activar entorno virtual
python3.12 -m venv venv
source venv/bin/activate

3. Instalar dependencias
pip install -r requirements.txt

4. Crear base de datos PostgreSQL
CREATE DATABASE ferrestock_db;
CREATE USER ferrestock_user WITH PASSWORD 'ferrestock_pass';
GRANT ALL PRIVILEGES ON DATABASE ferrestock_db TO ferrestock_user;
ALTER ROLE ferrestock_user CREATEDB;

5. Configurar variables de entorno
Crear un archivo .env a partir de .env.example.
Ejemplo:

SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://ferrestock_user:ferrestock_pass@localhost:5432/ferrestock_db

6. Ejecutar migraciones y datos base
python manage.py migrate
python manage.py setup_roles
python manage.py create_demo_users
python manage.py createsuperuser

7. Ejecutar servidor
python manage.py runserver
```
```
📊 Reportes

El sistema incluye:

Reporte de stock

Reporte de movimientos

Reporte de compras

Todos exportables en:

CSV

Excel

PDF
```
```
🧪 Tests
python manage.py test apps.core apps.reports
```
```
📱 Experiencia de uso

El sistema fue evolucionando desde una base académica hacia una experiencia más cercana a un entorno real de trabajo:

Dashboard orientado a operación

Alertas de productos críticos

Compras pendientes de recepción

Acciones rápidas por producto

Filtros en listados

Flujo de trabajo por roles
```
```
🚀 Deploy básico

Se incluye guía de despliegue en:

docs/DEPLOY_DROPLET.md
Resumen de deploy

Ubuntu 24.04

Python 3.12

PostgreSQL

Nginx

entorno virtual

variables de entorno

migraciones

collectstatic
```
```
💻 Para demo simple:

python manage.py runserver 0.0.0.0:8000

Para producción real, la evolución recomendada es:

Gunicorn

Nginx

systemd

HTTPS con Let's Encrypt
```
---

## ✅ Estado del proyecto

Proyecto funcional tipo MVP avanzado, preparado para:

entrega académica

portfolio profesional

presentación técnica

demostración funcional

futuras mejoras orientadas a producto real

## 🔮 Mejoras futuras

permisos más granulares por módulo

reportes avanzados de valorización

alertas por productos sin movimiento

deploy productivo con Gunicorn + Nginx

tests de integración adicionales

mejoras de UX operativa

dashboard más avanzado por rol

---

## 👨‍💻 Autor

Silvano Puccini

GitHub: @SilvanoPuccini

---
## 📄 Licencia

Este proyecto es parte del programa educativo de ConquerBlocks Academy.
Uso exclusivamente académico y de portfolio.
