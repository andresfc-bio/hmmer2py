# hmmer2py

**hmmer2py** es una herramienta automatizada en Python diseñada para agilizar el análisis de secuencias de proteínas utilizando HMMER y la base de datos Pfam.

El script automatiza la descarga de secuencias desde UniProt, la configuración de la base de datos Pfam (ya sea completa o un subconjunto personalizado), y la ejecución de `hmmscan` utilizando las mejores prácticas (como los umbrales de inclusión GA por defecto).

## 📋 Requisitos Previos

Para que este script funcione correctamente, asegúrate de tener instalados los siguientes programas en tu entorno Linux/Unix:

* **Python 3.x**
* **HMMER suite** (`hmmscan`, `hmmfetch`, `hmmpress`)
* Herramientas de sistema: `wget`, `awk`, `bash`

## 📂 Estructura del Proyecto

```text
hmmer2py/
├── hmmer2py.py                 # Script principal (Entry point)
├── scripts/
│   ├── downloader.py           # Descarga de secuencias FASTA de UniProt
│   ├── setup_hmmer.py          # Descarga e indexación de Pfam-A completa
│   └── pfam_subset_creator.py  # Creación de subconjuntos de Pfam-A
├── example_data/
│   ├── queries.txt             # Lista de IDs de UniProt a consultar
│   └── Pfam-A_subset.txt       # Lista de perfiles HMM para el subconjunto
└── results/                    # Directorio autogenerado para los resultados

```

## 🚀 Instrucciones de Uso

Antes de ejecutar el script por primera vez, asegúrate de darle permisos de ejecución:

```bash
chmod +x hmmer2py.py

```

### Argumentos Disponibles

* `--queries`: **(Requerido)** Ruta al archivo de texto que contiene la lista de IDs de UniProt (uno por línea).
* `--db-mode`: Define qué base de datos Pfam utilizar. Opciones: `full` (por defecto) o `subset`.
* `--subset-file`: Ruta al archivo `.txt` con los IDs de los modelos HMM (necesario solo si `--db-mode` es `subset`).
* `--no-cut-ga`: Desactiva el uso de los umbrales de inclusión *Gathering* (GA) curados por Pfam. Por defecto, **hmmer2py** siempre usa `--cut_ga`.

---

## 📖 Ejemplos de Ejecución

### 1. Ejecución con la Base de Datos Pfam Completa (Recomendado por defecto)

Si solo quieres correr tus secuencias contra toda la base de datos de Pfam, ejecuta:

```bash
./hmmer2py.py --queries example_data/queries.txt

```

*(Nota: Esto equivale a usar `--db-mode full`. La primera vez tomará un tiempo porque descargará e indexará la base de datos `Pfam-A.hmm.gz` de EBI).*

### 2. Ejecución con un Subconjunto Específico (Para análisis dirigidos)

Si tienes una lista específica de familias Pfam y no quieres escanear toda la base de datos (para ahorrar tiempo o restringir el análisis), usa el modo `subset` y pasa tu archivo con los IDs:

```bash
./hmmer2py.py --queries example_data/queries.txt --db-mode subset --subset-file example_data/Pfam-A_subset.txt

```

### 3. Ejecutar usando E-values en lugar de Umbrales GA

Pfam recomienda fuertemente usar sus umbrales curados (GA), por lo que están activados por defecto. Si necesitas un escaneo más permisivo basado puramente en E-values predeterminados de HMMER, desactiva la función con la bandera `--no-cut-ga`:

```bash
./hmmer2py.py --queries example_data/queries.txt --no-cut-ga

```

---

## 📁 Archivos de Salida

El script crea automáticamente una carpeta llamada `results/` en la raíz del proyecto. Los nombres de los archivos de salida se generan dinámicamente según el nombre de tu archivo `--queries` de entrada y el `--db-mode` utilizado, evitando que se sobrescriban.

Por ejemplo, si corres `./hmmer2py.py --queries mis_proteinas.txt --db-mode subset`, obtendrás:

* **`results/mis_proteinas_subset.txt`**: El output estándar de HMMER con alineamientos detallados.
* **`results/mis_proteinas_subset.tbl`**: El output en formato tabla (ideal para analizar en R, Python o Excel).
* **`results/queries/queries.fasta`**: El archivo unificado con todas las secuencias FASTA descargadas con éxito.
* **`results/queries/failed_downloads.log`**: Un registro con los IDs de UniProt que no se pudieron descargar (si los hay).