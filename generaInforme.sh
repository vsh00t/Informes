#!/bin/bash

# Constantes
empresa="Ironcybersec S.A.S."
email="info@ironcybersec.com"
sitio_web="www.ironcybersec.com"
telefono="+593 995653120"

# Array de nombres de meses en español
meses_espanol=("enero" "febrero" "marzo" "abril" "mayo" "junio" "julio" "agosto" "septiembre" "octubre" "noviembre" "diciembre")

# Solicitar datos
echo "Ingrese el título de la página:"
read titulo
echo "Ingrese el nombre del autor:"
read autor

nombreArchivo=$(echo $titulo | sed -e 's/[áéíóúÁÉÍÓÚ]//g' -e 's/ñ/n/g' -e 's/ /_/g')


# Establecer fecha del informe como la fecha actual en español
fecha_informe=$(date +"%d %m %Y")
IFS=' ' read -ra fecha_array <<< "$fecha_informe"
fecha_informe="${fecha_array[0]} de ${meses_espanol[$((${fecha_array[1]}-1))]^^} de ${fecha_array[2]}"

# Preguntar al usuario si desea cambiar la fecha del informe
read -p "Usar fecha de informe actual ($fecha_informe)? (S/N)" confirmar_fecha

# Si el usuario no confirma la fecha actual, solicitar la fecha del informe
if [[ $confirmar_fecha == [Nn]* ]]; then
  echo "Ingrese la fecha del informe (ejemplo: 23 de febrero de 2023):"
  read fecha_informe
fi

echo "Ingrese el nombre de la organización:"
read organizacion
echo "Ingrese el código del informe:"
read codigo

# Generar archivo .tex
cat > informe.tex << EOF
\documentclass{article}
\usepackage{graphicx}
\usepackage{background}

\title{\textbf{$titulo}}
\author{$autor}
\date{\today}

\backgroundsetup{
    scale=1,
    angle=0,
    opacity=1,
    contents={\includegraphics[width=\paperwidth,height=\paperheight]{/Users/jmoya/Tools/Informes/forside.pdf}}
}

\begin{document}

\begin{titlepage}
    \begin{center}
    \vspace{10cm}
    {\scshape\LARGE\textbf $titulo\par}
    \vspace{6cm}
    {\scshape\Large\textbf $organizacion\par}
    \vspace{4cm}
    \end{center}
    {\scshape\Large COD: $codigo\par}
    %\vspace{1cm}
    {\Large $fecha_informe\par}
    \vspace{2cm}
    {\small $empresa\par}
    {\small $email\par}
    {\small $sitio_web\par}
    {\small $telefono\par}
    \vfill
\end{titlepage}
\newpage
\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
\node[anchor=center] at (current page.center) {\textcolor{white}{\rule{\paperwidth}{\paperheight}}};
\end{tikzpicture}

\begin{center}
    \vspace*{\fill}
    {\color{red}\Huge\textbf{Aviso de Confidencialidad}\par}
\end{center}

    \vspace{4\baselineskip}
    \noindent La información contenida en el presente documento es confidencial y para uso exclusivo de la(s) persona(s) a quien(es) se dirige. Si el lector de este documento no es el destinatario, se le notifica que cualquier distribución o copia de la misma está estrictamente prohibida. Si ha recibido este documento por error le solicitamos notificar inmediatamente a la persona que lo envió y borrarlo definitivamente de su sistema.
      \vspace*{\fill}

\afterpage{\clearpage}

\end{document}
EOF

# Compilar archivo .tex con latexmk y generar PDF
pdf_nombre=Portada
latexmk -pdf informe.tex -jobname="$pdf_nombre" > /dev/null 2>&1

# Mostrar mensaje de éxito y salida
clear
echo -e "[-] Portada generada: OK\n"
awk '{gsub("../_resources/",""); print}' *.md > reporte.md; mv ../_resources/* . > /dev/null 2>&1
cat << EOF >> reporte.md


---
title: $titulo
author: []
date:
subject: Markdown
keywords: [Markdown, Example]
subtitle: $organizacion
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
EOF

docker run --rm -v $(pwd):/data  -w /data  rstropek/pandoc-latex  -f markdown  --from markdown+yaml_metadata_block -V fontfamily:lmodern --template https://raw.githubusercontent.com/vsh00t/Informes/main/eisvogel.tex  --table-of-contents  --toc-depth 6  -t latex --highlight-style=breezedark --listings -o Informe.pdf reporte.md

echo -e "[-] Contenido generado: OK\n"

gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=../$nombreArchivo.pdf Portada.pdf Informe.pdf

echo -e "[-] Informe generado exitosamente: $nombreArchivo.pdf\n"

read -p "¿Desea limpiar el contenido? (S/N): " opcion

if [[ "$opcion" == "S" || "$opcion" == "s" ]]; then
    cd ..
    for dir in */
    do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
        fi
    done
    echo -e "\nContenido eliminado exitosamente."
    exit 0
else
    exit 0
fi
