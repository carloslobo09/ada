# ADA

Plataforma de Auditoria Documental Automatizada mediante Inteligencia Artificial Generativa.

## Sobre el proyecto

Este repositorio acompana el Trabajo Final de Graduacion de la Licenciatura en Informatica de la Universidad Siglo 21. Autor: Carlos Ignacio Lobo, 2026.

El sistema toma documentos enviados por sistemas integradores, extrae los campos relevantes con un modelo de lenguaje, los valida contra reglas determinasticas y datos de referencia, y emite una decision automatica (aprobado o rechazado) con su trazabilidad completa para auditoria. Un proceso posterior de Re Control humano supervisa la calidad del sistema sobre los casos ya emitidos.

El caso de demostracion para esta entrega es el Documento Nacional de Identidad argentino, pero el modelo de configuracion (tipos documentales, versiones de prompt con campos a extraer y reglas de validacion cruzada) es generico para cualquier tipo de documento.

## Componentes

```
ada/
├── back/    Backend FastAPI + SQLAlchemy + Gemini (puerto adaptador)
├── front/   Frontend React + TypeScript + Tailwind
├── docker-compose.yml
└── README.md
```

## Roles

- **cliente**: envia documentos via API y consulta sus propios casos con una vista resumida (decision + motivos + datos extraidos).
- **entrenador**: opera la bandeja de Re Control, supervisa las decisiones, configura versiones del perfil de validacion.
- **admin**: ademas de lo anterior, administra tipos documentales y usuarios.

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

### Modo de extraccion

Por defecto el sistema corre con `EXTRACTOR_MODE=mock` en `back/.env`: no invoca ningun modelo y devuelve respuestas de ejemplo, asi se puede recorrer toda la plataforma sin API key ni costo. Para procesar documentos reales, generar una API key gratuita en https://aistudio.google.com y cambiar a `EXTRACTOR_MODE=gemini` (pasos detallados en [back/README.md](back/README.md)). Tener en cuenta que el tier gratuito de Gemini puede no estar disponible en momentos de alta demanda; habilitar facturacion con un limite mensual bajo resuelve ese problema.

## Documentacion por servicio

- [back/README.md](back/README.md)
- [front/README.md](front/README.md)

## Video demostrativo

> https://youtu.be/qeI18M619cs
