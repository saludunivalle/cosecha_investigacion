
# 📚 Extractor de Publicaciones Académicas ORCID

## 🎯 Descripción General

**Extractor de Publicaciones Académicas ORCID** es una herramienta automatizada diseñada para facilitar la recopilación, organización y exportación de la producción académica de investigadores a partir de sus códigos ORCID. El programa permite obtener de manera masiva y estructurada información sobre artículos, libros, capítulos y otros productos académicos registrados en la plataforma ORCID, generando un archivo Excel listo para análisis, reportes institucionales o gestión de indicadores.

### Características principales
- **Automatización total:** Solo necesitas una lista de investigadores con sus códigos ORCID y el programa se encarga del resto.
- **Resultados en Excel profesional:** Exporta los datos en formato XLSX, compatible con Excel, Google Sheets y otros programas.
- **Soporte para grandes volúmenes:** Procesa decenas o cientos de investigadores en una sola ejecución, mostrando barra de progreso y tiempos estimados.
- **Registro detallado de errores y logs:** Guarda bitácoras de cada ejecución para facilitar el soporte y la trazabilidad.
- **Configuración sencilla:** Instalación y uso guiados para Windows, Mac y Linux.
- **Personalizable y extensible:** Código abierto y modular, fácil de adaptar a nuevas necesidades.

### ¿Cómo funciona?
1. **Preparas un archivo CSV/Excel** con los nombres y códigos ORCID de los investigadores.
2. **Configuras tus credenciales ORCID** (guía paso a paso incluida).
3. **Ejecutas el programa** (doble clic o desde terminal, según tu sistema operativo).
4. El programa consulta la API de ORCID, descarga y organiza todas las publicaciones encontradas.
5. **Obtienes un archivo Excel** con toda la información lista para usar.

### Casos de uso
- Consolidación de hojas de vida académicas para grupos de investigación.
- Reportes institucionales de producción científica.
- Apoyo a procesos de acreditación, convocatorias y rankings.
- Seguimiento y análisis bibliométrico.

### Tecnologías empleadas
- **Python 3.8+**
- **Pandas** (procesamiento de datos)
- **OpenPyXL** (exportación a Excel)
- **Rich** (interfaz visual y barra de progreso)
- **ORCID API** (fuente de datos)

**En resumen:** Esta herramienta ahorra horas de trabajo manual, reduce errores y garantiza que la información de publicaciones esté siempre actualizada y bien organizada.

---

## 📋 ¿Qué necesitas antes de empezar?

### 1. **Python 3 instalado en tu computador**

- **¿Cómo saber si lo tienes?**
  - Abre una ventana de comandos:
    - En **Windows**: Presiona `Windows + R`, escribe `cmd` y presiona Enter
    - En **Mac/Linux**: Busca "Terminal" en tus aplicaciones
  - Escribe: `python --version` o `python3 --version`
  - Si ves algo como `Python 3.8.0` o superior, ¡ya lo tienes! ✅

- **Si no lo tienes**, descárgalo desde: [https://www.python.org/downloads/](https://www.python.org/downloads/)
  - Durante la instalación en Windows, **marca la casilla** que dice "Add Python to PATH"

### 2. **Credenciales de ORCID**

- Son como un usuario y contraseña para acceder a la información de ORCID
- Más abajo te explicamos cómo obtenerlas (es gratis y toma 5 minutos)

### 3. **Archivo con la lista de investigadores**

- Un archivo Excel/CSV con los nombres y códigos ORCID de los investigadores
- Te explicamos cómo prepararlo más adelante

---

## 🔑 Cómo obtener tus credenciales de ORCID

**Paso a paso:**

1. **Ve a**: [https://orcid.org/developer-tools](https://orcid.org/developer-tools)

2. **Inicia sesión** con tu cuenta ORCID
   - Si no tienes cuenta, créala en [https://orcid.org/register](https://orcid.org/register) (es gratis)

3. **Registra una nueva aplicación**:
   - Click en "Register for the free ORCID public API"
   - Llena el formulario:
     - **Nombre**: "Extractor de Publicaciones" (o el nombre que prefieras)
     - **Descripción**: "Herramienta para extraer publicaciones académicas"
     - **URL del sitio web**: Puedes poner tu página web o `http://localhost`
     - **URL de redirección**: `http://localhost`

4. **Guarda tus credenciales**:
   - Una vez registrada la aplicación, verás:
     - **Client ID**: Un código como `APP-XXXXXXXXXXXXXXXX`
     - **Client Secret**: Un código secreto largo
   - ⚠️ **IMPORTANTE**: Guarda estos códigos, los necesitarás en el siguiente paso

---

## 💻 Instalación del programa

### Para Windows

1. **Abre la carpeta del proyecto** en el Explorador de Archivos

2. **Haz doble clic** en el archivo `setup.bat`
   - Se abrirá una ventana negra (consola)
   - Verás mensajes de instalación
   - Espera a que termine (puede tomar 2-3 minutos)
   - Cuando veas "Configuración completada exitosamente", ¡listo! ✅

### Para Mac o Linux

1. **Abre la Terminal**:
   - En Mac: Busca "Terminal" en Spotlight
   - En Linux: Presiona `Ctrl + Alt + T`

2. **Navega a la carpeta del proyecto**:

   ```bash
   cd ruta/del/proyecto
   ```

   (Reemplaza `ruta/del/proyecto` con la ubicación real)

3. **Ejecuta el instalador**:

   ```bash
   bash setup.sh
   ```

   - Verás mensajes de instalación
   - Espera a que termine (puede tomar 2-3 minutos)
   - Cuando veas "Configuración completada exitosamente", ¡listo! ✅

---

## ⚙️ Configuración

### Configura tus credenciales de ORCID

1. **Busca el archivo** `.env.example` en la carpeta del proyecto

2. **Copia ese archivo** y renómbralo a `.env` (quita el ".example")
   - En Windows: Click derecho → Copiar → Pegar → Renombrar
   - En Mac/Linux: Desde Terminal: `cp .env.example .env`

3. **Abre el archivo `.env`** con un editor de texto (Bloc de notas, TextEdit, etc.)

4. **Reemplaza los valores**:

   ```env
   ORCID_CLIENT_ID=tu_client_id_aquí
   ORCID_CLIENT_SECRET=tu_client_secret_aquí
   ```

   - Pega el Client ID y Client Secret que obtuviste de ORCID

5. **Guarda el archivo** y ciérralo

⚠️ **IMPORTANTE**:

- NO compartas el archivo `.env` con nadie (contiene datos privados)
- NO lo subas a internet o redes sociales

---

## 📊 Preparar tu archivo de datos

El programa necesita un archivo llamado `input.csv` con la información de los investigadores.

### Formato del archivo

El archivo debe ser un CSV (valores separados por comas) con estas columnas:

```csv
cedula,nombre,orcid
12345678,Juan Pérez García,0000-0001-2345-6789
87654321,María López Rodríguez,0000-0002-9876-5432
11223344,Carlos Gómez Martínez,0000-0003-1122-3344
```

### ¿Cómo crearlo?

#### Desde Excel

1. Crea una tabla en Excel con 3 columnas: `cedula`, `nombre`, `orcid`
2. Llena los datos de cada investigador
3. Guarda como "CSV (delimitado por comas)"
4. Renombra el archivo a `input.csv`
5. Colócalo en la carpeta principal del proyecto

### Notas importantes

- La columna `cedula` es el número de identificación del investigador
- La columna `nombre` es el nombre completo
- La columna `orcid` debe tener el código ORCID completo (formato: 0000-0000-0000-0000)
- Si un investigador no tiene ORCID, pon un guión `-` en esa celda

---

## 🚀 Ejecutar el programa

Una vez configurado todo:

### En Windows

1. **Haz doble clic** en el archivo `start.bat`
2. Se abrirá una ventana mostrando el progreso
3. Espera a que termine (el tiempo depende de cuántos investigadores tienes)
4. Verás el mensaje "Procesamiento completado exitosamente" cuando termine

### En Mac o Linux

1. **Abre la Terminal**
2. **Navega a la carpeta del proyecto**:

   ```bash
   cd ruta/de/tu/proyecto
   ```

3. **Ejecuta**:

   ```bash
   bash start.sh
   ```

4. Espera a que termine

### Durante la ejecución verás

- ✓ Carga de usuarios
- ⏱️ Barra de progreso con tiempo estimado
- 📄 Cantidad de publicaciones encontradas
- ✓ Confirmación cuando termina

---

## 📈 Ver los resultados

Cuando el programa termine, encontrarás un archivo nuevo en la **carpeta principal del proyecto**:

📁 **`publicaciones_orcid_YYYY-MM-DD.xlsx`**

Por ejemplo: `publicaciones_orcid_2025-10-14.xlsx`

Este archivo contiene todas las publicaciones encontradas con la siguiente información:

| Columna | Qué significa |
|---------|---------------|
| `cedula` | Cédula del investigador |
| `nombre_profesor` | Nombre del investigador |
| `orcid_profesor` | Código ORCID del investigador |
| `title` | Título de la publicación |
| `journal` | Revista o editorial donde se publicó |
| `date` | Fecha de publicación |
| `doi` | Identificador único de la publicación (DOI) |
| `source` | Fuente de la información |
| `url_source` | Enlace a la publicación |

### ¿Cómo abrir los resultados?

- **En Excel**: Simplemente haz doble clic sobre el archivo (formato nativo de Excel)
- **En Google Sheets**: Archivo → Importar → Sube el archivo `.xlsx`
- **En LibreOffice Calc**: Archivo → Abrir → Selecciona el archivo

### Ventajas del formato XLSX

✅ **Formato nativo de Excel** - Se abre directamente sin problemas de codificación  
✅ **Mejor presentación** - Mantiene el formato de las celdas  
✅ **Más fácil de compartir** - Compatible con todos los programas de hojas de cálculo  
✅ **Nombre con fecha** - Cada ejecución genera un archivo único, no se sobrescribe

---

## ❗ Problemas comunes y soluciones

### "Python no está instalado" o "command not found: python"

**Solución**: Instala Python 3 desde [python.org](https://www.python.org/downloads/)

- En Windows, asegúrate de marcar "Add Python to PATH" durante la instalación

### "No se encontró el archivo .env"

**Solución**:

1. Revisa que hayas creado el archivo `.env` (sin el ".example")
2. Asegúrate de que está en la carpeta principal del proyecto

### "Error: Variables de Entorno Faltantes"

**Solución**:

1. Abre el archivo `.env`
2. Verifica que hayas pegado correctamente tus credenciales de ORCID
3. No debe haber espacios extras ni comillas

### "No se encontró el archivo input.csv"

**Solución**:

1. Verifica que el archivo `input.csv` esté en la carpeta principal
2. Revisa que el nombre sea exactamente `input.csv` (minúsculas)

### El programa se cierra inmediatamente

**Solución**:

1. En lugar de hacer doble clic, abre primero la Terminal/CMD
2. Navega a la carpeta del proyecto
3. Ejecuta manualmente:
   - Windows: `start.bat`
   - Mac/Linux: `bash start.sh`
4. Así podrás ver los mensajes de error

### "No se encontraron usuarios con ORCID válido"

**Solución**:

1. Abre el archivo `input.csv`
2. Verifica que los códigos ORCID estén en el formato correcto: `0000-0000-0000-0000`
3. Verifica que la columna se llame exactamente `orcid` (minúsculas)

### El programa tarda mucho

**Es normal**. El programa hace peticiones a ORCID por cada investigador:

- Con 10 investigadores: ~2-5 minutos
- Con 50 investigadores: ~10-20 minutos
- Con 100+ investigadores: puede tomar 30+ minutos

⏳ Ten paciencia, la barra de progreso te mostrará el tiempo estimado.

---

## 📝 Logs y registros

Si necesitas revisar qué pasó durante la ejecución:

- Los registros se guardan en: **`orcid/logs/`**
- Cada ejecución crea un archivo con la fecha y hora
- Útil para reportar errores o hacer seguimiento

---

## 🆘 ¿Necesitas más ayuda?

Si después de revisar esta guía sigues teniendo problemas:

1. **Revisa los logs** en la carpeta `orcid/logs/`
2. **Anota el mensaje de error** exacto que aparece
3. **Contacta al equipo de soporte** con:
   - Descripción del problema
   - Mensaje de error (si hay)
   - Sistema operativo que usas
   - Pasos que realizaste antes del error

---

## 📚 Información técnica adicional

### Tecnologías usadas

- Python 3.8+
- Pandas (procesamiento de datos)
- OpenPyXL (exportación a Excel)
- ORCID API (datos de publicaciones)
- Rich (interfaz visual)

### Estructura del proyecto

```bash
📁 Proyecto
├── 📄 main.py                           # Programa principal
├── 📄 input.csv                         # Tus datos de entrada
├── 📄 requirements.txt                  # Librerías necesarias
├── 📄 .env                              # Tus credenciales (privado)
├── 📄 setup.sh / setup.bat              # Instaladores
├── 📄 start.sh / start.bat              # Ejecutores
├── 📄 publicaciones_orcid_YYYY-MM-DD.xlsx  # RESULTADOS (se genera aquí)
└── 📁 orcid/                            # Módulo de ORCID
    ├── 📄 app.py                        # Lógica principal
    ├── 📄 utils.py                      # Funciones auxiliares
    └── � logs/                         # Registros de ejecución
```

---

## 📜 Licencia

Este proyecto está diseñado para uso académico e investigativo.

---

**¡Listo!** 🎉 Ahora estás preparado para usar el extractor de publicaciones ORCID.
