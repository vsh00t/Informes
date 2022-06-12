# Informes

Procedimiento para la elaboración de informes. 

## Prerequisitos

1. Descargar el contenedor https://hub.docker.com/r/rstropek/pandoc-latex

2. Instalar Joplin

## Procedimiento

1. Elaborar el informe en formato markdown en Joplin. No incluir emojis, ni tablas de contenido. 
2. Une vez terminado el informe, clic en exportar y en formato elegir markdown. 
3. Elegir un directorio para guardar el archivo markdown. 
4. Una vez generado el archivo exportado, desde linux o mac hacer lo siguiente:

El archivo original es 01.md

$ awk '{gsub("../_resources/",""); print}' 01.md > 02.md; mv ../_resources/* .
$ echo '---                                                                                                                                                 
title: Reporte No. 1 - Test de Intrusión Externo
author: []
date:
subject: Markdown
keywords: [Markdown, Example]
subtitle: NOMBRE DE LA EMPRESA CLIENTE.
lang: es
titlepage: false
titlepage-color: 483D8B
titlepage-text-color: FFFAFA
titlepage-rule-color: FFFAFA
titlepage-rule-height: 2
book: true
classoption: oneside
code-block-font-size: \scriptsize
---' | cat - 02.md > temp && mv temp 02.md

$ sudo docker run --rm -v $(pwd):/data \                                                                                                                   
    -w /data \
    rstropek/pandoc-latex \
    -f markdown \
    --from markdown+yaml_metadata_block+raw_html \
    --template https://raw.githubusercontent.com/vsh00t/Informes/main/eisvogel.tex \
    --table-of-contents \
    --toc-depth 6 \
    -t latex \
    -o Informe.pdf \
    02.md
 
 Se genera el archivo Informe.pdf
