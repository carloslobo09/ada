# ADA Backend

API del prototipo de la Plataforma de Auditoria Documental Automatizada.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy 2 + SQLite
- Pydantic v2 + pydantic-settings
- PyJWT + bcrypt (autenticacion)
- google-genai (cliente Gemini, SDK actual)

## Arquitectura

Layered con un puerto/adaptador hexagonal en el punto de integracion con el LLM.

```
app/
├── api/routers/                Endpoints HTTP delgados
├── services/                   Orquestacion del pipeline, decision, metricas
│   ├── extraction/             Puerto Extractor con adaptadores GeminiExtractor y MockExtractor
│   ├── cross_validation/       Normalizadores + comparadores + motor de validacion cruzada
│   └── rules/                  Motor de reglas + registry por tipo documental
├── repositories/               Acceso a datos (SQLAlchemy)
├── models/                     Entidades persistentes
├── schemas/                    Contratos Pydantic (incluye vistas separadas por rol)
├── domain/                     Tipos puros del dominio (NormalizedExtraction, CrossField, etc.)
└── storage/                    Persistencia de archivos en disco
```

### Genericidad por tipo documental

Cada `VersionPrompt` define su propia lista `extraction_fields` (nombre tecnico + etiqueta) que se usa para construir dinamicamente el `response_schema` que se le pide al modelo. Asi, el mismo backend procesa cualquier tipo documental sin tocar codigo.

Las reglas internas (`numero_dni_format`, `tipo_documento_es_dni`, etc.) son inherentemente especificas y se asignan por tipo via `services/rules/registry.py`. Si un tipo no tiene reglas registradas, el motor de reglas opera vacio y la decision depende solo de la validacion cruzada y la confianza.

### Pipeline de `POST /cases`

1. El router valida MIME y tamano del archivo.
2. `CasoService.process` resuelve la version de prompt publicada para el tipo documental.
3. Si el cliente envio datos de referencia (`expected`), se hace preflight: si falta un campo requerido o llega uno no configurado, el caso se rechaza sin invocar al modelo.
4. `FilesystemStorage` persiste el archivo en `UPLOAD_DIR`. `Documento` registra `nombre_original`, `ubicacion_s3`, `hash_integridad`, `content_type` y `file_size`.
5. El extractor (Gemini o Mock) devuelve la salida cruda del modelo con `value`, `confidence` y `status` por campo segun `extraction_fields`.
6. `normalize_extraction` hace un trim por campo y arma `NormalizedExtraction { values, confidences, raw }`.
7. El motor de reglas evalua las reglas registradas para el tipo (en DNI: formato, vencimiento, confianza, etc.).
8. El motor de validacion cruzada compara cada campo extraido contra el esperado: aplica primero la lista ordenada de normalizadores configurados por campo, despues el comparador (`equals`, `fuzzy_60`, `fuzzy_70`, `contains`).
9. El agregador de decision combina reglas criticas y validaciones cruzadas criticas: cualquiera que falle deja el caso en `rejected`. Si todo pasa, queda en `approved`. Las reglas no criticas que fallan se reportan como observaciones pero no cambian la decision.
10. El caso persiste con `Documento`, `Decision` y todas las evidencias intermedias para auditoria.

### Errores del extractor

Cada adaptador traduce los errores de su SDK a la jerarquia `ExtractorError`:

| Error del dominio | HTTP devuelto |
|---|---|
| `ExtractorUnavailableError` (LLM 5xx) | 503 |
| `ExtractorRateLimitedError` (LLM 429) | 429 |
| `ExtractorAuthError` (LLM 401/403) | 502 |
| `ExtractorInvalidResponseError` (JSON o contrato roto) | 502 |

Los mensajes son legibles y se propagan al frontend sin perder informacion.

## Autenticacion

Login emite un JWT (HS256). Tres roles: `cliente`, `entrenador`, `admin`. Para el demo se crean tres usuarios seed al primer arranque (ver README raiz).

Hay dos endpoints de login:

- `POST /auth/login` recibe JSON `{email, password}` y devuelve `{access_token, token_type, user}`. Usado por el frontend.
- `POST /auth/token` recibe `OAuth2PasswordRequestForm` (`username` + `password`) y devuelve `{access_token, token_type}`. Permite al boton "Authorize" de Swagger funcionar nativamente.

El admin no puede modificar su propio rol/estado ni resetearse la propia contrasena via la API de gestion (anti lockout).

### Vistas por rol en cases

`GET /cases/{id}` y `GET /cases` devuelven:

- Para cliente: vista resumida con decision, motivos, campos extraidos, validaciones cruzadas y datos del archivo. Sin ids internos, sin hash, sin estado de Re Control, sin evidencias del LLM.
- Para entrenador y admin: vista completa con toda la trazabilidad.

## Endpoints principales

| Metodo | Path | Rol requerido | Descripcion |
|---|---|---|---|
| POST | `/auth/login` | publico | Login (JSON) |
| POST | `/auth/token` | publico | Login (OAuth2 form, para Swagger) |
| GET | `/auth/me` | autenticado | Usuario activo |
| POST | `/cases` | autenticado | Sube documento, procesa y devuelve la decision |
| GET | `/cases` | autenticado | Lista (cliente solo ve los propios) |
| GET | `/cases/{id}` | autenticado | Detalle |
| PATCH | `/cases/{id}/review` | entrenador o admin | Marca el caso en Re Control |
| GET | `/document-types` | autenticado | Lista de tipos documentales |
| POST | `/document-types` | admin | Alta |
| PATCH | `/document-types/{id}` | admin | Edicion (nombre, descripcion, estado) |
| DELETE | `/document-types/{id}` | admin | Baja |
| GET | `/prompt-versions` | autenticado | Lista de versiones |
| POST | `/prompt-versions` | entrenador o admin | Crea version en estado borrador |
| PATCH | `/prompt-versions/{id}/publish` | entrenador o admin | Publica (archiva la anterior) |
| DELETE | `/prompt-versions/{id}` | entrenador o admin | Elimina (solo si no esta publicada) |
| POST | `/prompt-versions/{id}/simulate` | entrenador o admin | Ejecuta el pipeline sin persistir |
| GET | `/users` | admin | Lista de usuarios |
| POST | `/users` | admin | Alta de usuario |
| PATCH | `/users/{id}` | admin | Edicion (nombre, rol, estado) |
| POST | `/users/{id}/reset-password` | admin | Setea nueva contrasena |
| GET | `/metrics/dashboard` | entrenador o admin | KPIs, distribucion, acuerdo IA/humano, top motivos, serie diaria (acepta filtro `desde` y `hasta`) |

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

Ver `.env.example` con notas y el comando para regenerar `JWT_SECRET`.

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

Cubren: autenticacion y permisos por rol, vista resumida del cliente, gestion de usuarios y salvaguardas anti lockout, reglas DNI, agregador de decision, normalizadores, comparadores, motor de validacion cruzada, endpoints de tipos documentales, versiones de prompt, casos, revision y simulacion. Todo contra `MockExtractor`.
