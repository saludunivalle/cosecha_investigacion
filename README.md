# Antes de iniciar:
Antes de iniciar a ejecutar el programar es necesario tener en la carpeta donde se encuentra el archivo "main.py" un archivo llamado "input" en formato CSV con la siguiente estructura:
```csv
nombre,orcid,author_id
```

Es decir, el archivo debe contener tres columnas, la primera con el nombre del autor, la segunda con el ORCID y la tercera con el author_id. Cada fila corresponde a un autor.

Tambien es importante tener python instalado en el sistema. Para instalar python se puede instalar desde la tienda de aplicaciones de Windows en este [link](https://www.microsoft.com/es-es/p/python-39/9p7qfqmjrfp7?activetab=pivot:overviewtab) o desde la pagina oficial de python en este [link](https://www.python.org/downloads/).

# Ejecución:

Para ejecutar el programa se debe abrir una terminal* en la carpeta donde se encuentra el archivo "main.py" y ejecutar el siguiente comando:
```bash
python main.py
```
La instalacion de las librerias necesarias se realiza automaticamente al ejecutar el programa.

*Nota: Si no sabes como abrir una terminal en Windows puedes usar alternativamente el archivo "start.bat" que se encuentra en la carpeta del proyecto. Solo debes hacer doble click en el archivo "start.bat" y se abrirá una terminal en la carpeta del proyecto.

# Resultados:

El programa generará un archivo llamado "Publicaciones.xlsx" en la misma carpeta donde se encuentra el archivo "main.py" que contendra la información de las publicaciones de los autores en formato Excel.

Hay 3 hojas en el archivo Excel:

- **Publicaciones - ORCID**: Contiene la información de las publicaciones de los autores obtenida a partir del ORCID.
- **Publicaciones - Google Scholar**: Contiene la información de las publicaciones de los autores obtenida a partir de Google Scholar.
- **Publicaciones - ORCID + Scholar**: Contiene la información de las publicaciones de los autores obtenida a partir de la combinación de la información obtenida de ORCID y Google Scholar.

# Notas:

- La ejecucion del algoritmo al ejecutarse en un entorno local puede tardar un tiempo considerable, ya que se realizan muchas peticiones a las paginas web de ORCID y Google Scholar para obtener la información de las publicaciones de los autores. 

- Ocasionalmente puede ocurrir que el programa se detenga por un tiempo debido a que se realizan muchas peticiones a las paginas web y estas bloquean las peticiones por un tiempo. En este caso solo hay que reiniciar el programa y este continuará desde donde se quedó.

- A veces puede que al intentar abrir el archivo salte un mensaje de recuperacion por que el archivo esta roto, pero no hay problema, solo hay que darle a aceptar y el archivo se abrirá correctamente.

- Todas las hojas se filtraron para que solo muestren las publicaciones que no se encuentran repetidas. Se toma como criterio de repetición que dos publicaciones son iguales si tienen el mismo título y el mismo identificador del usuario que la publicó (orcid o author_id).
