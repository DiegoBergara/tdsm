# Proposal: File Management (Download/Upload)

## Why

Los usuarios de TDSM ejecutan comandos en sesiones remotas cuyo working directory está en el host. Hoy no hay forma de transferir archivos entre el cliente (Telegram) y ese sistema de archivos: no se puede descargar un artefacto generado en la sesión ni subir un script o carpeta para usarlo allí. Añadir descarga por ruta (archivo o carpeta en zip) y subida (archivo o carpeta) cierra esa brecha y hace las sesiones realmente útiles para flujos de desarrollo.

## What Changes

- **Descarga de archivo**: comando (o flujo) para descargar un archivo del host dado su ruta (relativa al working directory de la sesión o absoluta).
- **Descarga de carpeta en ZIP**: comando para descargar una carpeta como un archivo ZIP dado su ruta.
- **Subida de archivo(s)**: comando para subir uno o más archivos desde el cliente a una ruta de destino en el host (sesión actual).
- **Subida de carpeta**: comando para subir una carpeta (p. ej. como ZIP o como árbol de archivos) a una ruta de destino en el host.
- Definición de permisos y restricciones (rutas permitidas, tamaños máximos, tipos de archivo si aplica) para evitar abusos y riesgos de seguridad.
- Integración con el bot de Telegram (envío de documentos para subir; respuestas con documentos para descargar).

## Capabilities

### New Capabilities

- `file-download`: descarga de un archivo por ruta (ruta relativa al cwd de la sesión o absoluta dentro de allowed paths). El bot responde con el archivo como documento.
- `folder-download-zip`: descarga de una carpeta por ruta; el servidor genera un ZIP y lo envía como documento.
- `file-upload`: subida de uno o más archivos enviados por el usuario (documentos en Telegram) a una ruta de destino en el host; soporta mensaje con múltiples documentos.
- `folder-upload`: subida de una carpeta: el usuario envía un ZIP; el servidor lo descomprime en la ruta de destino (o flujo equivalente para “carpeta” como conjunto de archivos).

### Modified Capabilities

- Ninguna (no se modifican requisitos de specs existentes).

## Impact

- **Código**: nuevos handlers/comandos en el bot (p. ej. `/download`, `/upload` o flujos conversacionales), módulo o paquete de “file transfer” que use el filesystem y, si se usa ZIP, librería estándar o dependencia (zipfile en Python).
- **APIs**: uso de la API de Telegram para enviar/recibir documentos (archivos), posiblemente mensajes con captions o parámetros para rutas.
- **Seguridad**: validación estricta de rutas (evitar path traversal), límites de tamaño de archivo/carpeta, y opcionalmente lista de extensiones o MIME permitidos.
- **Sesión/tmux**: las rutas se resuelven en el contexto del working directory de la sesión actual (o de una sesión indicada), por lo que el session manager y el tmux controller deben exponer cwd y possibly “allowed base path” por sesión.
- **Configuración**: posible nueva configuración (ej. `UPLOAD_MAX_SIZE`, `ALLOWED_DOWNLOAD_PATHS`, `ALLOWED_UPLOAD_PATHS` o equivalente).
