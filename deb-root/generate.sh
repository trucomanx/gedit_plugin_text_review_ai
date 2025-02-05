#!/bin/bash

################################################################################
VERSION=$(grep "^Version=" ../plugins/text_review_ai.plugin | cut -d'=' -f2)
ARCH=$(dpkg-architecture -qDEB_HOST_MULTIARCH)

mkdir -p gedit-plugin-text-review-ai/usr/lib/$ARCH/gedit/plugins
mkdir -p gedit-plugin-text-review-ai/DEBIAN

# Caminho para o arquivo de serviço
TEMP_FILEPATH="gedit-plugin-text-review-ai/DEBIAN/control"

# Conteúdo do arquivo de serviço (substitua os placeholders)
STRING_CONTENT="Package: gedit-plugin-text-review-ai
Version: $VERSION
Section: editors
Priority: optional
Architecture: all
Depends: gedit (>= 3.0), python3, python3-gi, gir1.2-gtk-3.0
Maintainer: Fernando Pujaico Rivera <fernando.pujaico.rivera@gmail.com>
Description: Text review plugin with AI.
"

# Cria o arquivo de serviço temporário e escreve o conteúdo nele
echo "$STRING_CONTENT" | tee $TEMP_FILEPATH > /dev/null

cp -r ../plugins/* gedit-plugin-text-review-ai/usr/lib/$ARCH/gedit/plugins

dpkg-deb --build gedit-plugin-text-review-ai

mv gedit-plugin-text-review-ai.deb gedit-plugin-text-review-ai_${VERSION}.deb
