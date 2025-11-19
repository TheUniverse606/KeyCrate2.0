Guía de uso — KeyCrate
================================

1) Introducción
----------------
KeyCrate es una aplicación de escritorio para gestionar contraseñas de forma local y cifrada. Esta guía explica cómo instalar, configurar, ejecutar y mantener KeyCrate en un equipo Windows (instrucciones de PowerShell incluidas). También contiene recomendaciones de seguridad, empaquetado y resolución de problemas.

2) Requisitos mínimos
---------------------
- Sistema operativo: Windows 8/10/11 (funciona también en macOS o Linux con Python instalado).
- Python: 3.8+ (recomendado 3.10/3.11).
- Espacio libre en disco: ~100 MB (aplicación + base de datos pequeña).
- RAM: 1 GB mínimo (2–4 GB recomendado).
- Conexión a Internet para instalar dependencias.

3) Contenido del repositorio
----------------------------
Estructura relevante (resumida):

- main.py — punto de entrada (lanza la UI de escritorio).
- start_keycrate.bat — atajo para Windows.
- src/models/database.py — gestión de la DB (SQLite).
- src/ui/main_window.py — interfaz y flujo principal (login/registro/gestor).
- src/utils/encryption.py — hashing y cifrado (bcrypt, cryptography.Fernet).

Además en el mismo directorio hay una carpeta Keycrate_website con una página promocional (no altera la app).

4) Preparar entorno (Windows PowerShell)
---------------------------------------
Recomendado: usar un entorno virtual para aislar dependencias.

Pasos rápidos:

1. Abrir PowerShell y situarse en la carpeta del repositorio:

   cd 'C:\Users\cecia\Desktop\Proyectos personales\Keycrate'

2. Crear y activar un entorno virtual:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. Actualizar pip e instalar dependencias (si hay requirements.txt):

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt

Si no existe requirements.txt, instala dependencias principales:

   python -m pip install customtkinter cryptography bcrypt

5) Iniciar la aplicación
------------------------
Con el entorno activado:

python main.py

Alternativa: ejecutar start_keycrate.bat si fue creado para lanzar la app.

6) Flujo básico de uso
----------------------
- Registro: crea un usuario con email y contraseña maestra. La contraseña maestra se hashea (bcrypt) y se guarda en la DB.
- Login: introduce email y contraseña maestra; tras la verificación se accede al gestor.
- Gestor: listar entradas, agregar nueva entrada (nombre, URL, contraseña, notas), buscar, generar contraseña y copiar al portapapeles.
- Mostrar/Ocultar: para ver una contraseña se suele pedir confirmación de la contraseña maestra (depende del diseño en src/ui/main_window.py).
- Eliminar: borra la entrada de la base de datos.

7) Inicialización de la base de datos
-----------------------------------
La primera ejecución normalmente crea el fichero SQLite keycrate.db y las tablas necesarias. Si hay un script models/database.py con función create_tables() la aplicación lo invoca al iniciar.

8) Copias de seguridad y exportación
----------------------------------
- La base de datos SQLite (keycrate.db) contiene las entradas cifradas. Haz copias periódicas del archivo en un lugar seguro.
- Para restaurar: detener la app, reemplazar keycrate.db por la copia de seguridad y volver a iniciar.

9) Recomendaciones de seguridad
-------------------------------
- No compartir la contraseña maestra.
- Preferible derivar la clave Fernet desde la contraseña maestra (PBKDF2/Argon2) en lugar de almacenar encryption.key en disco. Esta mejora suele necesitar cambios en src/utils/encryption.py.
- Limpiar el portapapeles tras copiar contraseñas (por ejemplo, programar limpieza automática tras 20 segundos).
- Hacer backup de keycrate.db en almacenamiento cifrado o ubicación segura.
- Mantener el sistema operativo y Python actualizados.

10) Empaquetado en ejecutable (opcional)
--------------------------------------
Para distribuir la aplicación sin requerir Python instalado en el equipo final, puedes usar pyinstaller:

   python -m pip install pyinstaller
   pyinstaller --onefile --noconsole main.py

Notas:
- En Windows puede ser necesario incluir archivos adicionales (assets, encryption.key si se usa) en la carpeta del ejecutable.
- Probar el ejecutable en un entorno limpio antes de distribuir.

11) Localización y sitio promocional
-----------------------------------
El repositorio incluye Keycrate_website/ (sitio estático) que no modifica la app. Si quieres desplegarlo, puedes usar GitHub Pages o un host estático.

12) Solución de problemas comunes
--------------------------------
- Error al ejecutar python main.py:
  - Verifica que el entorno virtual esté activado y que las dependencias estén instaladas.
  - Ejecuta python -V para confirmar la versión.

- Problemas con compilación de bcrypt en Windows:
  - Instala las Build Tools de Visual Studio o usa ruedas precompiladas para Windows.
  - Alternativa: instalar la rueda .whl apropiada o usar pip para descargar binarios.

- No puede abrirse la base de datos (locked):
  - Asegúrate de que la app no esté corriendo en otra instancia y de cerrar programas que accedan al fichero.

13) Buenas prácticas para desarrolladores
----------------------------------------
- Mantener las dependencias en requirements.txt (ejecutar pip freeze > requirements.txt).
- Añadir tests unitarios para src/utils/encryption.py y src/models/database.py.
- Evitar persistir la contraseña maestra en memoria más tiempo del necesario.
- Considerar uso de un KDF (PBKDF2 o Argon2) para derivar la clave de cifrado.

14) Archivo requirements.txt sugerido
-------------------------------------
customtkinter
cryptography
bcrypt

15) FAQ rápido
--------------
Q: ¿Puedo usar KeyCrate en macOS / Linux?
A: Sí — los pasos de Python son prácticamente los mismos; cambia la activación del venv (macOS/Linux: source .venv/bin/activate).

Q: ¿Dónde se guarda la clave de cifrado?
A: En la implementación actual puede usarse encryption.key en disco o una clave derivada. Revisa src/utils/encryption.py para ver qué método usa tu copia.

Q: ¿Cómo restaurar el acceso si olvido la contraseña maestra?
A: Si olvidas la contraseña maestra y no tienes backups de la clave derivada, no es posible recuperar las contraseñas (están cifradas). Mantén backups seguros.

16) Contacto y contribuciones
------------------------------
Si quieres mejorar el proyecto, abre issues o pull requests en:

    https://github.com/TheUniverse606/KeyCrate2.0

17) Cambios y mantenimiento
---------------------------
Mantén un registro de cambios en CHANGELOG.md si planeas versiones públicas. Revisa commits y documenta actualizaciones de seguridad con prioridad.
