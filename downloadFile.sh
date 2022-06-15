#!bin/bash 
date=`date +"%Y%m%d"`;# 20210127
url="https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Informe_Comunicacion_"+ echo $date + ".ods";
file_in_repo=`${echo $url | rev | cut -d/ -f1 | rev}`;
mkdir -p "$(dirname "$file_in_repo")";
wget "$url" -O "$file_in_repo" ;

html="./index.html";
var2="./files/$file_in_repo";
headerremove=`grep -o './files/*' $1`;
var3=`echo $headerremove`;
echo $var2;
echo $var3;
sed 's/$var3/$var2/g' "$html";
