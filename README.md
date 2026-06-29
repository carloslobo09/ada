# ADA

Plataforma de Auditoria Documental Automatizada mediante Inteligencia Artificial Generativa.

## Sobre el proyecto

Este repositorio acompana el Trabajo Final de Graduacion de la Licenciatura en Informatica de la Universidad Siglo 21. Autor: Carlos Ignacio Lobo, 2026.

El sistema toma documentos enviados por sistemas integradores, extrae los campos relevantes con un modelo de lenguaje, los valida contra reglas y datos de referencia, y emite una decision (aprobado o rechazado) con su trazabilidad completa para auditoria.

El caso de demostracion para esta entrega es el Documento Nacional de Identidad argentino, pero el modelo de configuracion (tipos documentales + versiones de prompt + reglas de validacion cruzada) es generico para cualquier tipo de documento.

## Componentes

```
ada/
├── back/    Backend FastAPI + SQLAlchemy + Gemini
├── front/   Frontend React + TypeScript + Tailwind
├── docker-compose.yml
└── README.md
```

## Levantar el demo

```bash
cp back/.env.example back/.env
cp front/.env.example front/.env
docker compose up --build
```

- Frontend en http://localhost:3000
- API en http://localhost:8000
- Swagger UI en http://localhost:8000/docs

Usuarios seed (rol entre parentesis):

- `admin@ada.local` (admin)
- `entrenador@ada.local` (entrenador)
- `cliente@ada.local` (cliente)

Contrasena por defecto: la definida en `back/.env` como `SEED_PASSWORD`.

## Documentacion por servicio

- [back/README.md](back/README.md)
- [front/README.md](front/README.md)

## Video demostrativo

> _Pendiente link al video con un recorrido por el sistema.

`<https://...>`
