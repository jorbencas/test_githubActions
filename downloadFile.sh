#!/bin/bash 
function downloadder () {
    wget -O $1 $2;
    sleep 1;
}
htmlFile="index.html";
date=`date +"%Y%m%d"`;
url="https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Informe_Comunicacion_$date.ods";
file_in_repo=$(echo $url | rev | cut -d/ -f1 | rev);
dir='./files';
if [[ ! -d "$dir" ]]; then
    mkdir $dir;
fi
if [[ -f "$dir/*.ods" ]]; then
    rm -r $dir/*.ods;
fi
downloadFile="$dir/$file_in_repo";
http_status=$( wget --server-response -c "$url" 2>&1 )
if [[ $http_status == *"200"* ]]; then
    downloadder $downloadFile $url;
else
    file_in_repo="filters$date.json";
    downloadFile="$dir/$file_in_repo";
fi
if [[ ! -s "$htmlFile" ]]; then
    url="https://github.com/jorbencas/test_githubActions/blob/0f2cff77cf0914a37e4d439f8f026a3feefca3b0/index.html?raw=true";
    downloadder $htmlFile $url; 
fi
if [[ -s "$htmlFile" ]]; then
    sed "s|<a[^>]* href=\"[^\"]*|<a download href=\"$downloadFile|g" $htmlFile > $htmlFile.tmp && mv $htmlFile.tmp $htmlFile;
fi
echo $url;