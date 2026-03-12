# Tasks: File Management (Download/Upload)

## 1. Configuración y resolución de rutas

- [x] 1.1 Añadir variables de entorno o config para base path permitido, FILE_DOWNLOAD_MAX_SIZE, FILE_UPLOAD_MAX_SIZE, ZIP_MAX_SIZE
- [x] 1.2 Implementar utilidad de resolución de rutas: normalizar (., ..), resolver contra cwd de sesión y validar que la ruta final esté bajo la base permitida
- [x] 1.3 Exponer cwd de la sesión (p. ej. desde tmux: pane_current_path) para uso por file transfer

## 2. Módulo file_transfer (lógica de negocio)

- [x] 2.1 Implementar descarga de archivo: dado path resuelto y validado, leer archivo y devolver contenido (o path temporal) con comprobación de tamaño
- [x] 2.2 Implementar generación de ZIP para carpeta: dado path a directorio, crear ZIP (en memoria o temporal) con zipfile y comprobar tamaño máximo
- [x] 2.3 Implementar subida de archivo(s): escribir uno o más archivos en ruta destino con nombres originales; validar tamaño por archivo
- [x] 2.4 Implementar extracción de ZIP: descomprimir en ruta destino validando que cada miembro del ZIP quede bajo esa ruta (evitar path traversal)

## 3. Handlers de comandos (bot)

- [x] 3.1 Registrar comando /download (o /dl): parsear ruta, resolver con sesión actual, distinguir archivo vs directorio; si archivo enviar con send_document; si directorio usar lógica ZIP y enviar
- [x] 3.2 Registrar comando /upload [ruta]: sin ruta usar cwd; aceptar documento(s) en el mismo mensaje o siguiente; escribir archivos en destino; si es único .zip ofrecer o soportar flag --extract para extraer
- [x] 3.3 Manejar errores (path no permitido, archivo no existe, tamaño excedido, sin sesión) con mensajes claros al usuario

## 4. Integración y documentación

- [x] 4.1 Añadir /download y /upload a la ayuda del bot (comandos y descripción)
- [x] 4.2 Documentar en README o docs las nuevas variables de configuración y límites recomendados

## 5. Tests

- [x] 5.1 Tests unitarios para resolución y validación de rutas (path traversal, bajo base, relativas/absolutas)
- [x] 5.2 Tests para generación de ZIP (carpeta vacía, con archivos, límite de tamaño)
- [x] 5.3 Tests para extracción segura de ZIP (miembros con path traversal rechazados)
- [x] 5.4 Tests de integración o handlers para /download y /upload (mocks de Telegram y sesión)
