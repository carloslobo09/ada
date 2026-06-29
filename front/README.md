# ADA Frontend

Aplicacion de configuracion y supervision del prototipo de la Plataforma de Auditoria Documental Automatizada.

## Stack

- React 18 + TypeScript estricto
- Vite
- React Router v6
- TanStack Query
- React Hook Form + Zod
- Tailwind CSS
- Axios

## Pantallas

| Ruta | Rol minimo | Descripcion |
|---|---|---|
| `/login` | publico | Login con email y contrasena |
| `/casos` | cliente | Bandeja de casos (los clientes solo ven los propios) |
| `/casos/:caseId` | cliente | Detalle del caso con extraccion, reglas, validacion cruzada y decision |
| `/re-control` | entrenador | Bandeja de Re Control con pestanas Pendiente, Incorrecto y Todos |
| `/configuracion` | entrenador | Listado de versiones del perfil de validacion |
| `/configuracion/nueva` | entrenador | Alta de una version nueva en estado borrador |
| `/configuracion/:versionId` | entrenador | Detalle de una version, publicacion, eliminacion y simulacion |

El menu de navegacion se filtra por rol: el cliente solo ve la bandeja de casos.

## Estructura

```
src/
├── components/                Componentes compartidos
├── features/
│   ├── auth/                  Login, AuthContext, ProtectedRoute
│   ├── cases/                 Bandeja, detalle, Re Control
│   └── prompts/               Configuracion (versiones del prompt y simulacion)
├── lib/                       apiClient con interceptor JWT, queryClient, helpers de error
├── styles/                    Tailwind base
├── App.tsx
├── main.tsx
└── routes.tsx
```

## Configuracion (variables de entorno)

| Variable | Default | Descripcion |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` en dev, `/api` en Docker | URL base del backend |

## Levantar en local sin Docker

```bash
cd front
npm install
cp .env.example .env
npm run dev
```

Frontend en http://localhost:5173. El backend debe estar corriendo en `VITE_API_URL`.

## Levantar con Docker

Desde `ada/`:

```bash
docker compose up --build front
```

El frontend queda en http://localhost:3000. Nginx hace proxy de `/api/*` al backend interno.

## Build de produccion

```bash
npm run build
```

Genera `dist/` listo para servir con cualquier servidor estatico.
