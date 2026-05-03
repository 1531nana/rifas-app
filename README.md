# Rifas App

Sistema web para digitalizar el ciclo completo de una rifa: desde su creacion y publicacion, pasando por la seleccion y pago de numeros, hasta el registro del ganador. Los compradores acceden mediante un enlace publico sin necesidad de crear cuenta y pueden pagar con tarjeta, PSE o efectivo. El organizador gestiona todo desde un panel de control.

---

## Stack tecnologico

| Capa | Tecnologia |
|------|-----------|
| Backend | Python + FastAPI |
| Frontend | React + Vite + TailwindCSS |
| Base de datos | PostgreSQL + Alembic |
| Pagos | Wompi (tarjeta de credito y PSE) |
| Notificaciones | Meta Cloud API (WhatsApp Business) |
| Imagenes | Cloudinary |
| Despliegue backend | Railway |
| Despliegue frontend | Vercel |

---

## Arquitectura


rifas-app/
├── backend/          # API REST con FastAPI
└── frontend/         # SPA con React + Vite + TailwindCSS


El sistema es *multi-organizador*: cada admin gestiona sus propias rifas de forma aislada. Los compradores acceden a cada rifa mediante un public_token opaco unico, sin necesidad de registrarse.

### Modulos principales

- *Rifas* — CRUD de rifas, generacion de token publico, estados active / closed
- *Numeros* — Estados calculados dinamicamente: available, reserved, sold
- *Reservas* — Timeout de 48h para pagos digitales, 5 dias para efectivo; expiracion lazy + job periodico
- *Pagos* — Wompi via webhook para digital; confirmacion manual del admin para efectivo
- *Notificaciones* — Templates de WhatsApp aprobados por Meta: confirmacion de pago, recordatorio 15 dias antes del sorteo, notificacion al ganador
- *Archivos* — Subida de imagen del premio a Cloudinary (campo opcional, max 5MB, formatos JPG/PNG/WebP)

---

## Configuracion local

### Requisitos

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### Backend

bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # completar variables
alembic upgrade head
uvicorn app.main:app --reload


Verificar: GET http://localhost:8000/health debe retornar {"status": "ok"}

### Frontend

bash
cd frontend
npm install
cp .env.example .env            # completar variables
npm run dev


Verificar: abrir http://localhost:5173 en el navegador.

### Variables de entorno

Ver backend/.env.example y frontend/.env.example para la lista completa de variables requeridas.

---

## Flujo del comprador

1. El admin comparte el enlace /r/{public_token} de la rifa
2. El comprador ve la informacion de la rifa y la grilla de numeros (verde=disponible, rojo=vendido, amarillo=reservado)
3. Selecciona un numero disponible — queda reservado inmediatamente para otros
4. Completa el formulario con nombre, celular y email opcional
5. Elige metodo de pago: tarjeta/PSE (Wompi) o efectivo
6. Recibe confirmacion por WhatsApp una vez completado el pago

---

## Flujo del admin

1. Se registra con email y contrasena
2. Crea una rifa con nombre, premio, fecha, valor de boleta y tipo de loteria
3. Comparte el enlace publico generado automaticamente
4. Monitorea ventas en tiempo real desde el dashboard
5. Confirma pagos en efectivo manualmente
6. Registra el numero ganador para cerrar la rifa

---

## Despliegue

| Servicio | Plataforma |
|----------|-----------|
| Backend + BD | Railway |
| Frontend | Vercel |

---

## Flujo de desarrollo aplicado

Este proyecto sigue un flujo estructurado de ingenieria de software que parte de la solicitud del cliente y llega hasta tareas de desarrollo concretas y trazables:


Brief del cliente  →  PRD  →  Issues  →  Feature branch  →  Pull Request  →  main


### 1. Brief del cliente
El cliente describe el problema y sus necesidades en lenguaje natural, sin tecnicismos.
Archivo: [client-brief.md](client-brief.md)

### 2. PRD (Product Requirements Document)
A partir del brief se elabora un documento estructurado que define el problema, la solucion, las historias de usuario, las decisiones tecnicas y lo que queda fuera de alcance. Sirve como fuente de verdad del proyecto.
Archivo: [issues/prd.md](issues/prd.md)

### 3. Issues
El PRD se descompone en issues independientes y accionables. Cada issue tiene: descripcion de que construir, criterios de aceptacion medibles y dependencias explicitas (bloqueado por). Esto permite asignar y desarrollar cada tarea de forma aislada sin ambiguedad.
Carpeta: [issues/](issues/)

### 4. Feature branches y Pull Requests
Cada issue se desarrolla en una rama propia (feature/<nombre>). Al terminar se abre un Pull Request hacia main, lo que permite revision de codigo y trazabilidad entre el codigo entregado y el issue que lo origino.

---

## Issues del proyecto

Las tareas de desarrollo estan documentadas en la carpeta issues/. El PRD completo esta en [issues/prd.md](issues/prd.md).

| # | Issue | Bloqueado por |
|---|-------|---------------|
| 001 | Scaffold del proyecto | — |
| 002 | Autenticacion del admin | 001 |
| 003 | CRUD de rifas | 002 |
| 004 | Vista publica de la rifa | 003 |
| 005 | Grilla de numeros | 004 |
| 006 | Reserva de numeros | 005 |
| 007 | Pago con Wompi | 006 |
| 008 | Pago en efectivo | 006 |
| 009 | Expiracion de reservas | 006 |
| 010 | Imagen del premio | 003 |
| 011 | Notificaciones WhatsApp | 008 |
| 012 | Recordatorio de pago | 011 |
| 013 | Registro del ganador | 011 |
| 014 | Dashboard de estadisticas | 007, 008 |

---

## Fuera de alcance

- Generador automatico de numeros ganadores (el sorteo siempre es fisico)
- Notificaciones por email
- Aplicacion movil nativa
- Soporte para multiples ganadores por rifa
- Reventa o transferencia de boletas