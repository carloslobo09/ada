# ADA Backend

API del prototipo de la Plataforma de Auditoria Documental Automatizada.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy 2 + SQLite
- Pydantic v2 + pydantic-settings
- PyJWT + bcrypt (autenticacion)
- google-genai (cliente Gemini)

## Arquitectura

Layered con un puerto/adaptador hexagonal en el punto de integracion con el LLM.

```
app/
├── api/routers/       Endpoints HTTP delgados
├── services/          Orquestacion del pipeline, reglas, normalizacion, decision
│   └── extraction/    Puerto Extractor con adaptadores GeminiExtractor y MockExtractor
├── repositories/      Acceso a datos (SQLAlchemy)
├── models/            Entidades persistentes
├── schemas/           Contratos Pydantic (request/response)
├── domain/            Tipos puros del dominio
└── storage/           Persistencia de archivos en disco
```

Flujo de `POST /cases`:

1. El router valida MIME y tamano del archivo.
2. `CasoService.process` resuelve la version de prompt publicada para el tipo documental.
3. `FilesystemStorage` persiste el archivo en `UPLOAD_DIR`.
4. El extractor (Gemini o Mock) devuelve la salida cruda del modelo con `value`, `confidence` y `status` por campo.
5. La normalizacion convierte la salida cruda a la representacion canonica.
6. El motor de reglas evalua reglas determinasticas (formato, vencimiento, confianza, etc.).
7. La validacion cruzada compara campos extraidos contra los valores esperados que envia el sistema integrador.
8. El agregador de decision combina reglas y validacion cruzada y emite el veredicto.
9. El caso persiste con `Documento`, `Decision` y todas las evidencias intermedias para auditoria.

## Autenticacion

Login emite un JWT (HS256). Tres roles:

- `cliente`: crea casos y consulta los propios.
- `entrenador`: ademas administra versiones de prompt y revisa casos en Re Control.
- `admin`: ademas administra tipos documentales y usuarios.

Para el demo se crean tres usuarios seed al primer arranque (ver README raiz).

## Endpoints principales

| Metodo | Path | Rol requerido | Descripcion |
|---|---|---|---|
| POST | `/auth/login` | publico | Login con JSON `{email, password}` |
| POST | `/auth/token` | publico | Login con form OAuth2 (para el boton Authorize de Swagger) |
| GET | `/auth/me` | autenticado | Devuelve el usuario activo |
| POST | `/cases` | autenticado | Sube documento, procesa y devuelve la decision |
| GET | `/cases` | autenticado | Lista paginada (los clientes solo ven los propios) |
| GET | `/cases/{id}` | autenticado | Detalle del caso con evidencias |
| PATCH | `/cases/{id}/review` | entrenador o admin | Marca el caso en Re Control |
| GET | `/document-types` | autenticado | Lista de tipos documentales |
| POST | `/document-types` | admin | Alta de tipo documental |
| PATCH | `/document-types/{id}` | admin | Edicion de tipo documental |
| DELETE | `/document-types/{id}` | admin | Baja de tipo documental |
| GET | `/prompt-versions` | autenticado | Lista de versiones |
| POST | `/prompt-versions` | entrenador o admin | Crea nueva version en borrador |
| PATCH | `/prompt-versions/{id}/publish` | entrenador o admin | Publica la version (archiva la anterior) |
| DELETE | `/prompt-versions/{id}` | entrenador o admin | Elimina version (solo si no esta publicada) |
| POST | `/prompt-versions/{id}/simulate` | entrenador o admin | Ejecuta el pipeline sin persistir el caso |

## Configuracion (variables de entorno)

| Variable | Default | Descripcion |
|---|---|---|
| `EXTRACTOR_MODE` | `mock` | `mock` o `gemini` |
| `GEMINI_API_KEY` | (vacio) | API key de Google AI Studio. Requerida si `EXTRACTOR_MODE=gemini` |
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Modelo de la familia Gemini |
| `DB_URL` | `sqlite:///./data/ada.db` | URL SQLAlchemy |
| `UPLOAD_DIR` | `./data/uploads` | Carpeta donde se persisten los archivos subidos |
| `LOG_LEVEL` | `INFO` | Nivel de log |
| `JWT_SECRET` | (placeholder) | Secreto HS256. Regenerar antes de cualquier deploy |
| `JWT_EXPIRE_MINUTES` | `480` | Vida del token |
| `SEED_PASSWORD` | `ada2026` | Contrasena de los usuarios seed al primer arranque |

Ver `.env.example` con notas y comandos para regenerar `JWT_SECRET`.

## Levantar en local sin Docker

```bash
cd back
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate # macOS / Linux
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

API en http://localhost:8000, Swagger UI en http://localhost:8000/docs.

## Levantar con Docker

Desde `ada/`:

```bash
docker compose up --build back
```

## Tests

```bash
cd back
pip install -e ".[dev]"
pytest
```

Cubren: autenticacion y permisos por rol, reglas DNI, agregador de decision, comparadores y motor de validacion cruzada, endpoints de tipos documentales, prompt versions, casos, revision y simulacion, todos contra `MockExtractor`.
