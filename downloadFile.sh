# set -euo pipefail
echo "hola mundo"
# function downloadder () {
#     wget -q -O "$1" "$2"
#     sleep 1
# }

# htmlFile="index.html"
# date=$(date +"%Y%m%d")
# url="https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Informe_Comunicacion_${date}.ods"
# file_in_repo=$(basename "$url")
# dir='./files'

# # Crear directorio si no existe
# mkdir -p "$dir"

# # Eliminar ODS antiguos de forma segura
# rm -f "$dir"/*.ods || true

# downloadFile="$dir/$file_in_repo"

# # Comprobar estado HTTP (solo cabecera)
# http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

# if [[ "$http_status" == "200" ]]; then
#     downloadder "$downloadFile" "$url"
# else
#     file_in_repo="filters${date}.json"
#     downloadFile="$dir/$file_in_repo"
# fi

# # Descargar HTML si no existe o está vacío
# if [[ ! -s "$htmlFile" ]]; then
#     html_url="https://github.com/jorbencas/test_githubActions/blob/0f2cff77cf0914a37e4d439f8f026a3feefca3b0/index.html?raw=true"
#     downloadder "$htmlFile" "$html_url"
# fi

# # Modificar el HTML para que apunte al nuevo archivo
# if [[ -s "$htmlFile" ]]; then
#     sed -E "s|<a[^>]*href=\"[^\"]*|<a download href=\"$downloadFile|g" "$htmlFile" > "$htmlFile.tmp"
#     mv "$htmlFile.tmp" "$htmlFile"
# fi