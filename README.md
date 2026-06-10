# hmmer2py

**hmmer2py** es una herramienta automatizada en Python diseñada para agilizar el análisis de secuencias de proteínas utilizando HMMER y la base de datos Pfam.

El script automatiza la descarga de secuencias desde UniProt, la configuración de la base de datos Pfam (ya sea completa o un subconjunto personalizado), y la ejecución de `hmmscan` utilizando las mejores prácticas (como los umbrales de inclusión GA por defecto).

## 📂 Estructura del Proyecto

```text
hmmer2py/
├── hmmer2py.py                 # Script principal (Entry point de la CLI)
├── requirements.txt            # Dependencias del entorno de Python
├── LICENSE                     # Archivo oficial de la Licencia MIT
├── README.md                   # Documentación detallada del proyecto
├── scripts/
│   ├── downloader.py           # Descarga e integración de secuencias desde UniProt
│   ├── setup_hmmer.py          # Gestión, descarga e indexación de Pfam-A completa
│   ├── pfam_subset_creator.py  # Generador de bases de datos HMM reducidas (subconjuntos)
│   ├── analyzer.py             # Arquitectura OOP para parsing y análisis de resultados
│   └── logo_generator.py       # Renderizado de perfiles de conservación de aminoácidos (SVG)
├── example_data/
    ├── batch_job.txt             # Archivo de ejemplo con varios IDs de UniProt (ej. P04585, P12931 etc...)
    ├── single_job.txt            # Archivo de ejemplo con un unico ID de UniProt (ej. P04585)
    └── Pfam-A_subset.txt       # Archivo de ejemplo con IDs de familias Pfam (ej. RVT_1, Pkinase etc...)


```

---

## 📋 Requisitos Previos e Instalación

### 1. Dependencias del Sistema (Linux / WSL)

Asegúrate de contar con las siguientes herramientas en tu entorno Unix:

* **HMMER suite** (versión 3.3 o superior recomendada, con `hmmscan`, `hmmfetch` y `hmmpress` accesibles en el `$PATH`).
* Herramientas estándar del sistema: `wget`, `awk` y `bash`.

Para entornos basados en Ubuntu/Debian o WSL (Windows Subsystem for Linux), puedes instalar HMMER ejecutando:

```bash
sudo apt-get update
sudo apt-get install hmmer wget gawk

```

### 2. Clonación e Instalación de Dependencias de Python

El entorno requiere Python 3.10 o superior. Sigue estos pasos para preparar el proyecto:

```bash
# Clonar el repositorio
git clone https://github.com/andresfc-bio/hmmer2py.git
cd hmmer2py

# Dar permisos de ejecución al script principal
chmod +x hmmer2py.py

# Instalar las librerías necesarias de Python (Manejo de datos y gráficos)
pip install -r requirements.txt

```

---

## 📖 Guía de Uso Detallada

El script principal (`hmmer2py.py`) actúa como un orquestador. Dependiendo de los flags proporcionados, ejecutará pipelines completos o saltará tareas pesadas para realizar análisis dirigidos instantáneos.

### Modo 1: Pipeline Completo de Búsqueda (Comportamiento por Defecto)

Descarga secuencias, prepara la base de datos Pfam global, ejecuta `hmmscan` bajo umbrales curados (GA) y almacena los resultados de forma automática.

```bash
./hmmer2py.py --queries example_data/batch_job.txt

```

> *Nota: La primera vez que se ejecuta en modo `full`, el script tardará unos minutos en descargar la base de datos completa de Pfam-A y generar los índices binarios de HMMER (`hmmpress`). Las ejecuciones subsiguientes omitirán la descarga al detectar los archivos locales.*

### Modo 2: Pipeline Optimizado mediante Subconjuntos (Análisis Dirigidos)

Si sólo estás interesado en familias específicas (por ejemplo, dominios de quinasas o dominios SH2), puedes reducir masivamente el tiempo de escaneo extrayendo un subconjunto de Pfam.

```bash
./hmmer2py.py --queries example_data/batch_job.txt --db-mode subset --subset-file example_data/Pfam-A_subset.txt

```

### Modo 3: Análisis Directo de Resultados Existentes (Modo Ultra Rápido)

Si ya has realizado un escaneo previo y deseas interrogar el archivo tabular generado (`.tbl`) para estudiar una proteína específica usando el framework de objetos de Python, puedes saltarte todo el pipeline:

```bash
./hmmer2py.py --tbl-file results/batch_job_full.tbl --analyze P04585

```

### Modo 4: Generación Exclusiva de HMM Sequence Logos en SVG

Para extraer el modelo probabilístico de una familia y renderizar su distribución de bits y frecuencias de aminoácidos directamente en un vector SVG sin ejecutar alineamientos de secuencias:

```bash
./hmmer2py.py --logo RVT_1

```

### Modo Combinado Total

Puedes indicarle a `hmmer2py` que ejecute el pipeline completo, extraiga de inmediato el reporte OOP para una proteína de interés en la terminal y guarde el Sequence Logo del dominio catalítico de tu elección en una sola línea de comandos:

```bash
./hmmer2py.py --queries example_data/batch_job.txt --analyze P04585 --logo RVT_1

```

---

## 🛠️ Referencia Exhaustiva de la Interfaz de Línea de Comandos (CLI)

Puedes consultar la documentación integrada en cualquier momento mediante:

```bash
./hmmer2py.py --help

```

| Argumento | Tipo | Valores permitidos | Descripción |
| --- | --- | --- | --- |
| `--queries` | Ruta | Archivo de texto | **(Requerido para escaneo)** Lista de códigos de acceso UniProt (uno por línea) para descargar y alinear. |
| `--db-mode` | Opción | `full`, `subset` | Define si se escanea contra toda la base de datos (`full`, por defecto) o contra un archivo reducido (`subset`). |
| `--subset-file` | Ruta | Archivo de texto | Lista de nombres de dominios Pfam (uno por línea). **Obligatorio** si `--db-mode` es `subset`. |
| `--no-cut-ga` | Flag | Sin valor | Desactiva el flag `--cut_ga` de HMMER, provocando que `hmmscan` use los valores estándar de E-value en lugar de umbrales curados. |
| `--analyze` | Cadena | ID de UniProt | Identificador único de la proteína (ej. `P00519`) para procesar e imprimir su resumen OOP en consola. |
| `--tbl-file` | Ruta | Archivo `.tbl` | Especifica un reporte tabular de `hmmscan` ya existente. Evita la descarga y escaneos de secuencias. |
| `--logo` | Cadena | Nombre Pfam | Extrae el modelo de la base de datos local y genera el Sequence Logo multipágina en formato gráfico vectorial (`.svg`). |

---

## 📊 Arquitectura de Análisis (OOP interna)

El módulo `scripts/analyzer.py` está estructurado bajo tres abstracciones principales de programación orientada a objetos para manejar la complejidad taxonómica y estadística de HMMER:

1. **`HmmDomain`**: Instancia un hit individual de dominio. Almacena valores continuos (`E-value`, `Score`) transformados a tipos nativos flotantes de Python, el código de acceso del modelo Pfam y su descripción biológica.
2. **`ProteinAnalysis`**: Colecciona de manera indexada todos los objetos `HmmDomain` asociados a una misma secuencia query. Implementa métodos analíticos internos como `get_best_domain()`, el cual evalúa en tiempo lineal el dominio más significativo estadísticamente, y `print_summary()`, encargado de formatear los cuadros y listados finales en la terminal.
3. **`HmmscanParser`**: Implementa un flujo de lectura secuencial eficiente optimizado para memoria que parsea archivos tabulares extensos de HMMER. Utiliza expresiones regulares para limpiar las cabeceras de UniProt y poblar de forma dinámica el mapa relacional de objetos de proteínas.

---

## 📁 Estructura de Archivos de Salida (`results/`)

Los resultados se organizan de forma para salvaguardar el historial de ejecuciones:

* **`results/queries/queries.fasta`**: Archivo multifasta unificado con las secuencias descargadas de manera exitosa desde UniProt.
* **`results/queries/failed_downloads.log`**: Registro de fallos que contiene los IDs que arrojaron errores de conexión o que no existen en el servidor de UniProt.
* **`results/[NombreDeQuery]_[Modo].txt`**: Reporte exhaustivo de `hmmscan` con los alineamientos de secuencia clásicos.
* **`results/[NombreDeQuery]_[Modo].tbl`**: Reporte tabular optimizado estructuralmente para integraciones bioinformáticas o lecturas en frameworks de análisis.
* **`results/[NombreDominio]_logo.svg`**: Gráfico multipágina en formato vectorial con barras escaladas según el contenido de información (*bits*) del perfil de conservación, dividido en ventanas de 100 posiciones consecutivas.

---

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Esto significa que puedes modificar, distribuir, utilizar de forma comercial y privada el código de forma completamente libre, siempre y cuando mantengas el aviso de copyright original incluido en el archivo [LICENSE](https://github.com/andresfc-bio/hmmer2py/blob/main/LICENSE).
