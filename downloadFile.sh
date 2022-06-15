#!/bin/bash 
date='20210127';#`date +"%Y%m%d"`;# 20210127
url="https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Informe_Comunicacion_$date.ods";
file_in_repo=$(echo $url | rev | cut -d/ -f1 | rev);
dir='./files';
if [ ! -d $dir ]; then
    mkdir $dir;
fi
if [ -f "$dir/*.ods" ]; then
    rm -r $dir/*;
fi
var2="$dir/$file_in_repo";
wget "$url" -O "$var2";
if [ ! -f $var2 ]; then
    sleep 3;
fi
sed "s|<a[^>]* href=\"[^\"]*|<a download href=\"$var2|g" "index.html";