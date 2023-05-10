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

# Constantes
empresa=""
email=""
sitio_web=""
telefono=""
workpath = "/Users/jmoya/Tools/Informes/"
current_directory = os.getcwd()
resource_directory = os.path.join(current_directory, "../_resources")

# Array de nombres de meses en español
meses_espanol=["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Solicitar datos
titulo = input("Ingrese el título de la página: ")
autor = input("Ingrese el nombre del autor: ")

nombreArchivo = unidecode(titulo).replace(' ', '_')

# Establecer fecha del informe como la fecha actual en español
fecha_actual = datetime.datetime.now()
fecha_informe = f"{fecha_actual.day} de {meses_espanol[fecha_actual.month - 1]} de {fecha_actual.year}"

# Preguntar al usuario si desea cambiar la fecha del informe
confirmar_fecha = input(f"Usar fecha de informe actual ({fecha_informe})? (S/N)")

# Si el usuario no confirma la fecha actual, solicitar la fecha del informe
if confirmar_fecha.lower() == 'n':
  fecha_informe = input("Ingrese la fecha del informe (ejemplo: 23 de febrero de 2023): ")

# Obtener los datos
organizacion = input("Ingrese el nombre de la organización: ")
codigo = input("Ingrese el código del informe: ")
os.system('clear')

# Define la cadena de texto a agregar al inicio
header = f"""---
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
code-block-font-size: \\scriptsize
table-use-row-colors: true
toc-own-page: true
---
"""

# Encuentra todos los archivos .md en el directorio especificado
md_files = glob.glob(os.path.join(current_directory, '*.md'))

# Crea un nuevo archivo reporte.md
with open('reporte.md', 'w') as report:
    # Escribe el header en el archivo reporte.md
    report.write(header)
    # Para cada archivo .md
    for filename in md_files:
        # Abre el archivo
        with open(filename, 'r') as file:
            # Lee el contenido
            content = file.read()
            # Escribe el contenido en reporte.md
            report.write(content)

# Leer el contenido del archivo
with open('reporte.md', 'r') as file:
    file_content = file.read()

# Reemplazar el texto
file_content = file_content.replace("../_resources/", "")

# Escribir el contenido de nuevo al archivo
with open('reporte.md', 'w') as file:
    file.write(file_content)


# Obtén todos los archivos en el directorio de recursos
resource_files = glob.glob(os.path.join(resource_directory, "*"))

# Copia cada archivo al directorio actual
for file in resource_files:
    shutil.copy(file, current_directory)

with open('reporte.md', 'r') as file:
    data = file.read()

# Extrae la tabla de Markdown usando una expresión regular
tabla = re.findall(r'\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|', data)

# Convierte la tabla a un DataFrame
df = pd.DataFrame([re.split(r'\s*\|\s*', row)[1:-1] for row in tabla[1:]], columns=re.split(r'\s*\|\s*', tabla[0])[1:-1])

# Selecciona la columna 'Severidad'
severidad = df['Severidad']

# Contar ocurrencias de cada severidad
conteo = Counter(severidad)

# Asignar conteos a variables
criticas = conteo.get('Crítica', 0)
altas = conteo.get('Alta', 0)
medias = conteo.get('Media', 0)
bajas = conteo.get('Baja', 0)
informativas = conteo.get('Informativa', 0)

####

categories = ['Crítica', 'Alta', 'Media', 'Baja', 'Informativa']
values = [int(criticas), int(altas), int(medias), int(bajas), int(informativas)]
latex_graphic = current_directory + "/barchart.pdf"
plt.bar(categories, values, color=['black', 'red', 'orange', 'green', 'cyan'])
plt.title('Resumen de vulnerabilidades')
plt.xlabel('Severidad')
plt.ylabel('Número de vulnerabilidades')

max_value = max(values)
plt.xlim([-0.5, max_value-0.5])
plt.tick_params(axis='y', which='major', pad=5)
plt.savefig(current_directory + '/barchart.pdf')

####
# Crear documento
doc = Document()

# Agregar paquetes
doc.preamble.append(Command('usepackage', 'graphicx'))
doc.preamble.append(Command('usepackage', 'background'))

# Agregar página de título

#with doc.create(Section('')):
doc.append(NoEscape('\\backgroundsetup{\n'
                        '    scale=1,\n'
                        '    angle=0,\n'
                        '    opacity=1,\n'
                        '    contents={\\includegraphics[width=\\paperwidth,height=\\paperheight]'
                        '{/Users/jmoya/Tools/Informes/forside.pdf}}\n'
                        '}\n\n'
                        '\\begin{titlepage}\n'
                        '    \\begin{center}\n'
                        '    \\vspace{10cm}\n'
                        '    {\\scshape\\LARGE\\textbf ' + titulo + '\\par}\n'
                        '    \\vspace{6cm}\n'
                        '    {\\scshape\\Large\\textbf ' + organizacion + '\\par}\n'
                        '    \\vspace{4cm}\n'
                        '    \\end{center}\n'
                        '    {\\scshape\\Large COD: ' + codigo + '\\par}\n'
                        '    %\\vspace{1cm}\n'
                        '    {\\Large ' + fecha_informe + '\\par}\n'
                        '    \\vspace{2cm}\n'
                        '    {\\small ' + empresa + '\\par}\n'
                        '    {\\small ' + email + '\\par}\n'
                        '    {\\small ' + sitio_web + '\\par}\n'
                        '    {\\small ' + telefono + '\\par}\n'
                        '    \\vfill\n'
                        '\\end{titlepage}\n\n'
                        ))


doc.append(NoEscape('\\begin{tikzpicture}[remember picture,overlay]\n'
                    '\\node[anchor=center] at (current page.center) '
                    '{\\textcolor{white}{\\rule{\\paperwidth}{\\paperheight}}};\n'
                    '\\end{tikzpicture}\n'))

# Agregar sección de Aviso de Confidencialidad
doc.append(NoEscape('\\begin{center}\n'
                        '    \\vspace*{\\fill}\n'
                        '    {\\color{red}\\Huge\\textbf{Aviso de Confidencialidad}\\par}\n'
                        '\\end{center}\n\n'
                        '    \\vspace{4\\baselineskip}\n'
                        '    \\noindent La información contenida en el presente documento es confidencial '
                        'y para uso exclusivo de la(s) persona(s) a quien(es) se dirige. Si el lector de este '
                        'documento no es el destinatario, se le notifica que cualquier distribución o copia de '
                        'la misma está estrictamente prohibida. Si ha recibido este documento por error le '
                        'solicitamos notificar inmediatamente a la persona que lo envió y borrarlo definitivamente '
                        'de su sistema.\n'
                        '      \\vspace*{\\fill}\n\n'
                        '\\clearpage\n'))

doc.append(NoEscape('\\begin{tikzpicture}[remember picture,overlay]\n'
                    '\\node[anchor=center] at (current page.center) '
                    '{\\textcolor{white}{\\rule{\\paperwidth}{\\paperheight}}};\n'
                    '\\end{tikzpicture}\n'))

doc.append(NoEscape('\\begin{figure}[h!]\n'
                    '    \\vspace*{\\fill}\n'
                        '    \\vspace{4\\baselineskip}\n'
                        '    \\noindent En el gráfico presentado a continuación, se muestra un resumen que representa el número de vulnerabilidades detectadas, organizadas por su nivel de severidad. Cada barra del gráfico representa un nivel de severidad, y la longitud de la barra indica el número total de vulnerabilidades asociadas a ese nivel.\\ \n'
                        '      \\vspace*{\\fill}\n\n'
                         '    \\vspace{1\\baselineskip}\n'
                        '    \\noindent Esta representación visual facilita la comprensión de la distribución y la prevalencia de las vulnerabilidades según su severidad. Es posible, de un vistazo, discernir qué niveles de severidad son más comunes en las vulnerabilidades identificadas. Este conocimiento es fundamental para priorizar las acciones de mitigación, dirigiendo primero los esfuerzos hacia las vulnerabilidades de mayor severidad que pueden tener un impacto más significativo en la seguridad del sistema.\\ \n\n\n\n'
                        '      \\vspace*{\\fill}\n\n'
                        '    \\includegraphics[width=0.8\\textwidth]{barchart.pdf}\n'
                        '    %\\caption{Resumen de vulnerabilidades}\n'
                        '\\end{figure}\n'
                        '\\clearpage\n'))

# Guardar documento
doc.generate_pdf(current_directory+'/portada', clean_tex=False)

print("[-] Portada generada: OK\n")

# Asegúrate de que estás en el directorio correcto
os.chdir(current_directory)

# Define el comando de Docker como una cadena

docker_command = "docker run --rm -v "+current_directory+":/data -w /data rstropek/pandoc-latex -f markdown --from markdown+yaml_metadata_block -V fontfamily:lmodern --template https://raw.githubusercontent.com/vsh00t/Informes/main/eisvogel.tex --table-of-contents --toc-depth 6 -t latex --highlight-style=breezedark --listings -o Informe.pdf reporte.md"

# Ejecuta el comando con subprocess
subprocess.run(docker_command, shell=True)


print("[-] Contenido generado: OK\n")


merger = PdfMerger()

input1 = open(current_directory+ "/portada.pdf", "rb")
input2 = open(current_directory+ "/Informe.pdf", "rb")

# Añadir los archivos pdf a la fusión
merger.append(fileobj=input1)
merger.append(fileobj=input2)

# Escribir a la salida y cerrar los archivos de entrada
output = open(workpath + "/" +nombreArchivo + ".pdf", "wb")
merger.write(output)

input1.close()
input2.close()
output.close()

print(f"[-] Informe generado exitosamente: {nombreArchivo}.pdf\n")

opcion = input("¿Desea limpiar el contenido del directorio "+ current_directory +" ? (S/N): ")

if opcion.lower() == "s":
    shutil.rmtree(current_directory)
    shutil.rmtree(workpath + "/_resources")
    os.chdir(workpath)
    print("\nContenido eliminado exitosamente.")
else:
    print("\nBye.")
