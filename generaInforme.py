#!/usr/bin/env python3
import glob
import shutil
import os
import subprocess
import datetime
from unidecode import unidecode
import matplotlib.pyplot as plt
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import bold
from PyPDF2 import PdfMerger
import pandas as pd
from collections import Counter
import re
import argparse
import platform

# Configurar argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Generar informe a partir de archivos Markdown.')
parser.add_argument('--workpath', required=True, help='Ruta de trabajo donde se guardará el informe.')
parser.add_argument('--markdown_directory', required=True, help='Directorio donde se encuentran los archivos Markdown.')
parser.add_argument('--resource_directory', required=True, help='Directorio de recursos adicionales.')

args = parser.parse_args()

# Constantes
empresa = ""
email = ""
sitio_web = ""
telefono = ""

# Utilizar los argumentos proporcionados
workpath = args.workpath
markdown_directory = args.markdown_directory
resource_directory = args.resource_directory

def obtener_datos_usuario():
    """Solicita datos al usuario y devuelve los valores ingresados."""
    titulo = input("Ingrese el título de la página: ")
    autor = input("Ingrese el nombre del autor: ")
    nombreArchivo = unidecode(titulo).replace(' ', '_')

    # Establecer fecha del informe como la fecha actual en español
    meses_espanol = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    fecha_actual = datetime.datetime.now()
    fecha_informe = f"{fecha_actual.day} de {meses_espanol[fecha_actual.month - 1]} de {fecha_actual.year}"

    confirmar_fecha = input(f"Usar fecha de informe actual ({fecha_informe})? (S/N)")
    if confirmar_fecha.lower() == 'n':
        fecha_informe = input("Ingrese la fecha del informe (ejemplo: 23 de febrero de 2023): ")

    organizacion = input("Ingrese el nombre de la organización: ")
    codigo = input("Ingrese el código del informe: ")

    return titulo, autor, nombreArchivo, fecha_informe, organizacion, codigo

def generar_header(titulo, organizacion):
    """Genera el encabezado del archivo Markdown."""
    return f"""---
title: {titulo}
author: []
date:
subject: Markdown
keywords: [Markdown, Example]
subtitle: {organizacion}
lang: es
titlepage: false
titlepage-color: 483D8B
titlepage-text-color: FFFAFA
titlepage-rule-color: FFFAFA
titlepage-rule-height: 2
book: true
classoption: oneside
code-block-font-size: \scriptsize
table-use-row-colors: true
toc-own-page: true
---
"""

def combinar_archivos_markdown(markdown_directory, header):
    """Combina todos los archivos Markdown en un único archivo reporte.md."""
    md_files = glob.glob(os.path.join(markdown_directory, '*.md'))
    with open(markdown_directory+'/reporte.md', 'w') as report:
        report.write(header)
        for filename in md_files:
            with open(filename, 'r') as file:
                content = file.read()
                report.write(content)

def procesar_tabla_vulnerabilidades(markdown_directory):
    """Procesa la tabla de vulnerabilidades y genera un gráfico de barras si la tabla existe."""
    with open(markdown_directory+'/reporte.md', 'r') as file:
        data = file.read()

    # Extraer la tabla usando una expresión regular
    tabla = re.findall(r'\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|', data)

    if not tabla:
        print("[ADVERTENCIA] No se encontró una tabla de vulnerabilidades en el archivo Markdown.")
        opcion = input("¿Desea generar el informe sin el gráfico de barras? (S/N): ").strip().lower()
        if opcion == 's':
            print("Generando el informe sin el gráfico de barras...")
            return None
        else:
            print("Saliendo del proceso de generación del informe.")
            exit(1)

    try:
        # Convertir la tabla a un DataFrame
        df = pd.DataFrame([re.split(r'\s*\|\s*', row)[1:-1] for row in tabla[1:]], columns=re.split(r'\s*\|\s*', tabla[0])[1:-1])
        if 'Severidad' not in df.columns:
            print("[ADVERTENCIA] No se encontró una tabla de vulnerabilidades en el archivo Markdown.")
            opcion = input("¿Desea generar el informe sin el gráfico de barras? (S/N): ").strip().lower()
            if opcion == 's':
                print("Generando el informe sin el gráfico de barras...")
                return None
            else:
                print("Saliendo del proceso de generación del informe.")
                exit(1)

        severidad = df['Severidad']
        conteo = Counter(severidad)

        categorias = ['Crítica', 'Alta', 'Media', 'Baja', 'Informativa']
        valores = [conteo.get(cat, 0) for cat in categorias]

        plt.figure(figsize=(8, 4))
        barras = plt.bar(categorias, valores, color=['red', 'orange', 'yellow', 'green', 'cyan'])
        plt.title('Resumen de vulnerabilidades')
        plt.xlabel('Severidad')
        plt.ylabel('Número de vulnerabilidades')
        plt.xlim([-0.5, len(categorias)-0.5])

        for bar in barras:
            valor_y = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, valor_y, int(valor_y), va='bottom')

        grafico_path = os.path.join(markdown_directory, 'barchart.pdf')
        plt.savefig(grafico_path)
        plt.close()

        return grafico_path

    except Exception as e:
        print(f"[ADVERTENCIA] Ocurrió un error al procesar la tabla: {e}.")
        opcion = input("¿Desea generar el informe sin el gráfico de barras? (S/N): ").strip().lower()
        if opcion == 's':
            print("Generando el informe sin el gráfico de barras...")
            return None
        else:
            print("Saliendo del proceso de generación del informe.")
            exit(1)

def generar_documento_latex(titulo, organizacion, codigo, fecha_informe, grafico_path, markdown_directory):
    """Genera el documento LaTeX con portada personalizada, aviso de confidencialidad y gráfico."""
    doc = Document()
    doc.preamble.append(Command('usepackage', 'graphicx'))
    doc.preamble.append(Command('usepackage', 'background'))
    doc.preamble.append(Command('usepackage', 'xcolor'))  # Para texto en color

    # Configurar la portada con los ajustes solicitados
    doc.append(NoEscape(r"""
        \backgroundsetup{
            scale=1,
            angle=0,
            opacity=1,
            contents={\includegraphics[width=\paperwidth,height=\paperheight]{/Users/jmoya/Tools/Informes/Portada_2025.pdf}}
        }

        \begin{titlepage}
            \raggedright
            % Título del Informe (H1) ajustado 3 cm más arriba, con sangría izquierda de 3 cm y margen derecho de 1 cm
            \vspace*{3cm}
            \hspace*{3cm}\parbox[t]{\dimexpr\textwidth-0.5cm}{\color{white}\sffamily\bfseries\LARGE """ + titulo.upper() + r"""}\\[3cm]

            % Nombre del Cliente (H2) centrado verticalmente, con sangría izquierda de 3 cm y margen derecho de 1 cm
            \hspace*{3cm}\parbox[t]{\dimexpr\textwidth-0.5cm}{\color{white}\sffamily\bfseries\huge """ + organizacion + r"""}\\[6cm]

            % Código del Informe (H3) y Fecha (H6) ajustados en la parte baja, con sangría izquierda de 6 cm y margen derecho de 0.5 cm
            \vfill
            \hspace*{10.5cm}\parbox[t]{\dimexpr\textwidth-0.5cm}{\color{white}\sffamily\bfseries\Large """ + codigo + r"""}\\
            \hspace*{10.5cm}\parbox[t]{\dimexpr\textwidth-0.5cm}{\color{white}\sffamily\small """ + fecha_informe + r"""}
        \end{titlepage}
    """))

    # Desactivar el fondo después de la portada para el acuerdo de confidencialidad
    doc.append(NoEscape(r"""
        \NoBgThispage
        \newpage
        \begin{center}
        {\color{red}\LARGE\textbf{Aviso de Confidencialidad}}
        \end{center}
        \vspace{1cm}
        \noindent
        La información contenida en el presente documento es confidencial y para uso
        exclusivo de la(s) persona(s) a quien(es) se dirige. Si el lector de este documento
        no es el destinatario, se le notifica que cualquier distribución o copia de la
        misma está estrictamente prohibida. Si ha recibido este documento por error
        le solicitamos notificar inmediatamente a la persona que lo envió y borrarlo
        definitivamente de su sistema.
        \newpage
    """))

    # Desactivar el fondo para la página del gráfico
    if grafico_path and os.path.exists(grafico_path):
        doc.append(NoEscape(r"""
            \NoBgThispage
            \newpage
            \noindent
            En el gráfico presentado a continuación, se muestra un resumen que representa
            el número de vulnerabilidades detectadas, organizadas por su nivel de severidad.
            Cada barra del gráfico representa un nivel de severidad, y la longitud de la barra
            indica el número total de vulnerabilidades asociadas a ese nivel.
            Esta representación visual facilita la comprensión de la distribución y la prevalencia
            de las vulnerabilidades según su severidad. Es posible, de un vistazo,
            discernir qué niveles de severidad son más comunes en las vulnerabilidades identificadas.
            Este conocimiento es fundamental para priorizar las acciones de mitigación,
            dirigiendo primero los esfuerzos hacia las vulnerabilidades de mayor
            severidad que pueden tener un impacto más significativo en la seguridad del
            sistema.
            \includegraphics[width=1.04\textwidth]{""" + grafico_path + r"""}
        """))

    # Generar PDF
    doc.generate_pdf(markdown_directory + '/portada', clean_tex=False)

def generar_informe_pdf(markdown_directory):
    """Genera el archivo PDF del informe usando Docker."""
    docker_command = (
        f"docker run --rm -v {markdown_directory}:/data -w /data "
        "rstropek/pandoc-latex -f markdown --from markdown+yaml_metadata_block "
        "-V fontfamily:lmodern --template https://raw.githubusercontent.com/vsh00t/Informes/main/eisvogel.tex "
        "--table-of-contents --toc-depth 6 -t latex --highlight-style=breezedark --listings -o Informe.pdf reporte.md"
    )

    print("Ejecutando el comando Docker para generar el PDF...")
    result = subprocess.run(docker_command, shell=True)
    if result.returncode != 0:
        raise RuntimeError("Error al generar el archivo Informe.pdf usando Docker.")

def ajustar_rutas_imagenes(markdown_directory):
    """Ajusta las rutas de las imágenes en el archivo Markdown y copia las imágenes al directorio de trabajo."""
    with open(markdown_directory + '/reporte.md', 'r') as file:
        data = file.read()

    # Reemplazar las rutas de las imágenes para que apunten al directorio de trabajo
    data = data.replace('../_resources/', '')

    # Escribir el contenido modificado de nuevo al archivo
    with open(markdown_directory + '/reporte.md', 'w') as file:
        file.write(data)

    # Copiar las imágenes al directorio de trabajo
    resource_files = glob.glob(os.path.join(resource_directory, '*'))
    for resource in resource_files:
        shutil.copy(resource, markdown_directory)

def verificar_e_iniciar_docker():
    """Verifica si Docker está corriendo y lo inicia si no lo está."""
    try:
        # Verificar si Docker está corriendo
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("Docker está corriendo.")
    except subprocess.CalledProcessError:
        print("Docker no está corriendo. Intentando iniciarlo...")
        sistema = platform.system()
        if sistema == "Darwin":  # macOS
            try:
                subprocess.run(["open", "/Applications/Docker.app"], check=True)
                print("Docker se está iniciando en macOS. Por favor, espera unos momentos y vuelve a intentarlo.")
            except Exception as e:
                print(f"Error al intentar iniciar Docker en macOS: {e}")
        elif sistema == "Linux":
            try:
                subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
                print("Docker se está iniciando en Linux. Por favor, espera unos momentos y vuelve a intentarlo.")
            except Exception as e:
                print(f"Error al intentar iniciar Docker en Linux: {e}")
        else:
            print("Este script no soporta el inicio automático de Docker en este sistema operativo.")

def main():
    verificar_e_iniciar_docker()  # Verificar e iniciar Docker antes de cualquier operación
    titulo, autor, nombreArchivo, fecha_informe, organizacion, codigo = obtener_datos_usuario()
    header = generar_header(titulo, organizacion)
    combinar_archivos_markdown(markdown_directory, header)
    ajustar_rutas_imagenes(markdown_directory)  # Ajustar rutas de imágenes y copiar recursos
    grafico_path = procesar_tabla_vulnerabilidades(markdown_directory)
    generar_documento_latex(titulo, organizacion, codigo, fecha_informe, grafico_path, markdown_directory)

    # Generar el informe PDF
    generar_informe_pdf(markdown_directory)

    # Fusión de PDFs
    portada_path = markdown_directory + "/portada.pdf"
    informe_path = markdown_directory + "/Informe.pdf"

    if not os.path.exists(portada_path) or not os.path.exists(informe_path):
        raise FileNotFoundError("No se encontraron los archivos necesarios para la fusión de PDFs.")

    merger = PdfMerger()
    with open(portada_path, "rb") as input1, open(informe_path, "rb") as input2:
        merger.append(fileobj=input1)
        merger.append(fileobj=input2)

    output_path = os.path.join(workpath, f"{nombreArchivo}.pdf")
    with open(output_path, "wb") as output:
        merger.write(output)

    print(f"[-] Informe generado exitosamente: {output_path}\n")

    opcion = input("¿Desea limpiar el contenido del directorio " + markdown_directory + " ? (S/N): ")

    if opcion.lower() == "s":
        shutil.rmtree(markdown_directory)
        shutil.rmtree(workpath + "/_resources")
        os.chdir(workpath)
        print("\nContenido eliminado exitosamente.")
    else:
        print("\nBye.")

if __name__ == "__main__":
    main()

print("[-] Contenido generado: OK\n")

