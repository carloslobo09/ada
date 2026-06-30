# ADA Frontend

Aplicacion de operacion y supervision del prototipo de la Plataforma de Auditoria Documental Automatizada.

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
| `/casos` | cliente | Bandeja de casos. El cliente ve su lista propia; entrenador y admin ven el dashboard de metricas mas la bandeja con tabs Sin revisar / Con observacion / Todos |
| `/casos/:caseId` | cliente | Detalle del caso. El cliente ve vista resumida; entrenador y admin ven la vista completa con evidencias y el panel de Re Control |
| `/configuracion` | entrenador | Lista de tipos documentales. Las acciones de alta/edicion/baja solo aparecen para admin |
| `/configuracion/tipos/:tipoId` | entrenador | Detalle del tipo con sus versiones de prompt |
| `/configuracion/tipos/:tipoId/versiones/nueva` | entrenador | Alta de version en estado borrador |
| `/configuracion/tipos/:tipoId/versiones/:versionId` | entrenador | Detalle de version, publicacion, eliminacion y simulacion |
| `/usuarios` | admin | Gestion de usuarios (alta, edicion, reset de contrasena, activar/desactivar) |

El menu de navegacion se filtra por rol: el cliente solo ve "Mis casos"; entrenador agrega "Re Control" y "Configuracion"; admin agrega ademas "Usuarios".

## Estructura

```
src/
├── components/                Componentes compartidos (Button, Alert, Spinner, ConfirmDialog, Layout)
├── contexts/                  Providers globales (ConfirmContext con useConfirm)
├── features/
│   ├── auth/                  Login, AuthContext, ProtectedRoute
│   ├── cases/                 Bandeja, detalle, Re Control, vista cliente
│   ├── document-types/        CRUD admin de tipos documentales
│   ├── prompts/               Configuracion de versiones (extraction_fields, normalizaciones, comparadores, simulacion)
│   ├── metrics/               Dashboard con KPIs, distribucion, acuerdo IA/humano, top motivos, serie diaria
│   └── users/                 Gestion admin de usuarios
├── lib/                       apiClient con interceptor JWT, queryClient, helpers de error
├── styles/                    Tailwind base
├── App.tsx
├── main.tsx
└── routes.tsx
```

### Modal de confirmacion generico

Toda accion destructiva o irreversible (eliminar, desactivar, publicar version, resetear contrasena, etc.) usa el patron unificado `useConfirm()` definido en `contexts/ConfirmContext.tsx`. Reemplaza `window.confirm` con un modal accesible (portal, focus, ESC, click fuera), variantes `primary` o `danger`. Aplicar siempre que se introduzca una nueva accion con efecto irreversible.

### Vista por rol en cases

El detalle y la lista de casos se adaptan segun el rol del usuario logueado: el cliente ve un panel resumido sin trazabilidad interna; entrenador y admin ven el panel completo con evidencias del LLM, reglas evaluadas y todo el ciclo de Re Control.

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
