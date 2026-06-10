import os
import subprocess
import sys

# Manejo de dependencias para asegurar que el usuario tenga logomaker instalado
try:
    import pandas as pd
    import logomaker
    import matplotlib.pyplot as plt
except ImportError:
    print("Error: Faltan librerías para generar el logo.")
    print("Por favor instálalas ejecutando: pip install pandas logomaker matplotlib")
    sys.exit(1)

def generate_logo(domain_name, db_path):
    """Extrae un modelo HMM de Pfam y genera su Logo en PDF."""
    
    os.makedirs("results", exist_ok=True)
    hmm_file = f"results/{domain_name}.hmm"
    txt_file = f"results/{domain_name}_logo.txt"
    out_svg = f"results/{domain_name}_logo.svg"

    print(f"\n[Logo] Extrayendo el perfil HMM para '{domain_name}' de la base de datos...")
    
    # 1. hmmfetch: Extraer el dominio específico
    fetch_cmd = f"hmmfetch {db_path} {domain_name} > {hmm_file}"
    try:
        subprocess.run(fetch_cmd, shell=True, check=True, executable='/bin/bash')
    except subprocess.CalledProcessError:
        print(f"Error: No se pudo extraer '{domain_name}'. Verifica que el nombre sea exacto y exista en {db_path}.")
        if os.path.exists(hmm_file):
            os.remove(hmm_file)
        return

    # 2. hmmlogo: Generar los datos de las frecuencias
    print(f"[Logo] Generando datos de información y frecuencias...")
    logo_cmd = f"hmmlogo --no_indel --height_relent_abovebg {hmm_file} > {txt_file}"
    subprocess.run(logo_cmd, shell=True, check=True, executable='/bin/bash')

    # 3. Procesar los datos con Pandas
    print(f"[Logo] Dibujando el gráfico...")
    aminoacidos = list('ACDEFGHIKLMNPQRSTVWY')
    
    with open(txt_file, 'r') as f:
        datos = {int(p[0][:-1]): [float(v) for v in p[1:21]]
                 for linea in f if (p := linea.split()) and len(p) >= 21 and p[0].endswith(':') and p[0][:-1].isdigit()}

    if not datos:
        print("Error: El archivo de logo está vacío o corrupto.")
        return

    df = pd.DataFrame.from_dict(datos, orient='index', columns=aminoacidos).rename_axis('Posicion')

    # 4. Generar la gráfica multipágina con logomaker
    ventana = 100
    pos_max = df.index.max()
    num_filas = (pos_max - 1) // ventana + 1

    fig, axes = plt.subplots(num_filas, 1, figsize=(16, 2 * num_filas), squeeze=False)

    for i, ax in enumerate(axes.flatten()):
        inicio, fin = i * ventana + 1, min((i + 1) * ventana, pos_max)
        
        # Extraer los datos de la ventana actual
        df_slice = df.loc[inicio:fin]
        if df_slice.empty:
            continue

        logo = logomaker.Logo(df_slice, ax=ax, color_scheme='chemistry', vpad=.1, width=.8)
        logo.style_spines(visible=False)
        logo.style_spines(spines=['left', 'bottom'], visible=True)

        ax.set(ylabel='Info (bits)', title=f'{domain_name}: Posiciones {inicio} - {fin}', xlim=(inicio - 0.5, fin + 0.5))

    axes.flatten()[-1].set_xlabel('Posición en el perfil HMM', fontsize=14)

    plt.tight_layout()
    # Guardamos forzando el formato svg
    fig.savefig(out_svg, format='svg', bbox_inches='tight') 
    plt.close(fig) 
    
    print(f"[Logo] ¡Completado! El logo se ha guardado en: {out_svg}")