# Design: File Management (Download/Upload)

## Context

TDSM es un bot de Telegram que gestiona sesiones de desarrollo (tmux) y permite ejecutar comandos en el host. El working directory de cada sesión vive en el sistema de archivos del servidor. Actualmente no existe transferencia de archivos: el usuario no puede bajar un build o un log ni subir un script. Este diseño añade descarga (archivo o carpeta como ZIP) y subida (archivo(s) o carpeta vía ZIP) respetando el contexto de la sesión actual y con controles de seguridad.

## Goals / Non-Goals

**Goals:**

- Permitir descargar un archivo del host por ruta (relativa al cwd de la sesión o absoluta dentro de allowed paths).
- Permitir descargar una carpeta como un único archivo ZIP.
- Permitir subir uno o más archivos (documentos de Telegram) a una ruta de destino.
- Permitir subir una carpeta enviando un ZIP que se descomprime en la ruta de destino.
- Resolver rutas en el contexto del working directory de la sesión actual (o sesión indicada).
- Validar rutas para evitar path traversal y aplicar límites de tamaño y, si se desea, restricciones por tipo.

**Non-Goals:**

- Sincronización bidireccional o “sync” continuo.
- Edición remota de archivos en tiempo real.
- Soporte para protocolos distintos a Telegram (p. ej. SFTP, WebDAV).

## Decisions

### 1. Comandos y flujos

- **Descarga**: comando `/download <ruta>` (o `/dl <ruta>`). Si la ruta es un archivo, se envía como documento; si es un directorio, se comprime con `zipfile` en memoria o temporal y se envía el ZIP.
- **Subida**: 
  - Opción A: comando `/upload [ruta_destino]`; el usuario envía el/los documento(s) en el mensaje siguiente o en el mismo (multidocument). Si hay un solo archivo y es `.zip`, se puede tratar como “carpeta” y descomprimir en `ruta_destino`.
  - Opción B: detectar mensajes que solo contienen documentos (sin comando) y, si hay sesión actual, preguntar o usar un destino por defecto (p. ej. cwd).
- **Decisión**: Comando explícito `/upload [ruta]`; si no se indica ruta, usar cwd de la sesión actual. Si el usuario envía un único archivo `.zip`, ofrecer descomprimir en la ruta (o hacerlo por defecto con un flag `/upload --extract` o similar). Múltiples archivos se escriben en la ruta destino (nombres originales).

### 2. Resolución de rutas y sesión

- Las rutas se resuelven respecto al **working directory** de la sesión actual (o de la sesión indicada, si se añade parámetro opcional `[session]`).
- Rutas absolutas permitidas solo si están bajo una raíz configurada (p. ej. `ALLOWED_BASE_PATHS` o `WORKSPACE_ROOT`); si no, solo rutas relativas al cwd.
- **Decisión**: Una única base permitida por configuración (o por sesión). Cualquier ruta (relativa o absoluta) se normaliza y se comprueba que esté bajo esa base. El cwd de la sesión se obtiene vía tmux (e.g. `tmux display-message -p "#{pane_current_path}"` para el pane de la sesión).

### 3. Seguridad

- **Path traversal**: normalizar ruta (resolver `.`, `..`, enlaces simbólicos opcionalmente) y verificar que la ruta resuelta empiece con la base permitida.
- **Límites**: `FILE_DOWNLOAD_MAX_SIZE`, `FILE_UPLOAD_MAX_SIZE`, `ZIP_MAX_SIZE` (para ZIPs subidos o generados). Rechazar si se superan.
- **Tipos**: opcionalmente lista blanca de extensiones o MIME para subida; para descarga no restringir tipo (el bot envía lo que hay).
- **Decisión**: Implementar validación de rutas y límites de tamaño en la primera versión; lista blanca de extensiones como opción de configuración.

### 4. Dependencias

- **ZIP**: usar `zipfile` de la stdlib para generar ZIPs al descargar carpetas y para descomprimir al subir. No añadir dependencias externas.
- **Telegram**: usar `send_document` y recibir `document` en updates; tamaño máximo de documento según límites de la API de Telegram (20 MB para bot; considerar compresión o chunking en futuras versiones si se necesitan archivos mayores).

### 5. Ubicación en el código

- Nuevo módulo `file_transfer` (o `handlers/file_transfer.py`) con: resolución de rutas seguras, generación de ZIP, descompresión, lectura/escritura de archivos.
- Handlers de comandos `/download` y `/upload` que usen el session context (sesión actual, cwd) y llamen a ese módulo; enviar/recibir documentos vía python-telegram-bot.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Path traversal o escritura fuera de base | Normalización y comprobación estricta bajo base permitida; no seguir symlinks fuera de base. |
| Archivos muy grandes bloquean el bot o exceden Telegram | Límites configurables; rechazar con mensaje claro; en el futuro considerar chunking o enlace externo. |
| ZIP malicioso (path traversal dentro del ZIP) | Al descomprimir, comprobar que cada nombre de miembro normalizado quede bajo la ruta destino. |
| Cwd de tmux inexacto si hay múltiples panes | Usar el pane “principal” de la sesión o el primero; documentar comportamiento. |

## Migration Plan

- No hay migración de datos: es funcionalidad nueva.
- Despliegue: añadir variables de entorno (o configuración) para límites y rutas permitidas; desplegar código nuevo; documentar comandos en ayuda.
- Rollback: eliminar handlers y dependencias del módulo file_transfer; no hay cambios en esquemas ni en sesiones existentes.

## Open Questions

- ¿Permitir `/download <session> <ruta>` y `/upload <session> [ruta]` para actuar sobre otra sesión? (Propuesta: sí, opcional, para consistencia con otros comandos.)
- ¿Mostrar progreso para archivos grandes (p. ej. “Comprimiendo…” antes de enviar el ZIP)? (Propuesta: mensaje de estado opcional para UX.)
