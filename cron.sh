#!/bin/bash

usage() { echo "$(basename "$0") [-h] [-f AAAAMMDDHH] [-d x] [-p x] [-r x] [-v x] [-t x] [-g x] [-m x] 

Programa para correr operativo el WRF, con opción de ensamble y postprocesamiento

opciones:
    -h  Mostrar esta ayuda
    -f  Fijar una fecha particular en el formato AAAAMMDDHH (default: fecha actual)
    -d  Descargar GFS, 1 para descargar 0 para no descargar (default: 1)
    -p  Ejecutar el WPS, 1 para ejecutar el WPS 0 para no ejecutarlo (default: 1)
    -r  Ejecutar el WRF, 1 para ejecutar el WRF 0 para no ejecutarlo (default: 1)
    -v  Extraer las variables del wrfout, 1 para extraer 0 para no extraer (default: 1)
    -t  Guardar las tablas de datos para puntos, 1 para guardar 0 para no guardar (default: 1)
    -g  Generar los gráficos con mapas, 1 para graficar 0 para no graficar (default: 1)
    -m  Enviar el mail al finalizar, 1 para enviar 0 para no enviar (default: 1)
    " 1>&2; exit 1; }

while getopts ':hf:d:p:r:m:' option; do
  case "$option" in
    h) usage
        ;;
    f)  export Y=`date -d "${OPTARG:0:-2} ${OPTARG:8:10}" +%Y`
            export M=`date -d "${OPTARG:0:-2} ${OPTARG:8:10}" +%m`
            export D=`date -d "${OPTARG:0:-2} ${OPTARG:8:10}" +%d`
            export H=`date -d "${OPTARG:0:-2} ${OPTARG:8:10}" +%H`
            ;;
    d)  export DESCARGAR=$OPTARG
            ;;
    p)  export RUN_WPS=$OPTARG
            ;;
    r)  export RUN_WRF=$OPTARG
            ;;
    v)  export EXTRAER_VARIABLES=$OPTARG
            ;;
    t)  export DATOS_METEO=$OPTARG
            ;;
    g)  export MAPAS=$OPTARG
            ;;
    m)  export MAIL=$OPTARG
            ;;
    :) printf "Falta argumento para -%s\n" "$OPTARG" >&2
       usage
       ;;
   \?) printf "No existe esta opcion: -%s\n" "$OPTARG" >&2
       usage
       ;;
  esac
done
shift $((OPTIND-1))

# Crea las variables de entorno
source env.sh

echo "################ Se ejecuta el runEureka ################"
mkdir -p $LOGS_DIR/$Y'_'$M/$D'_'$H
time python3 runEureka.py > $LOGS_DIR/$Y'_'$M/$D'_'$H/eureka_`date +%Y%m%d%H%M`.log 2>&1
