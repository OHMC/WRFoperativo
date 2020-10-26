# -*- coding: utf-8 -*-
"""Example Google style docstrings.
Este scripot es el encargado de configurar el entorno y llamar a las funciones
correspondientes y en el orden que se debe

TODO: add logging
"""


import os
import glob
import time
import datetime
import socket

from descarga_GFS025 import download, get_list_gfs
from namelists import editar_namelist_wps
from parametrizaciones import ParametrizacionWRF


def log_date(log):
    date = datetime.datetime.now()
    print('------------------------------------------------------')
    print(log)
    print(date)
    print('------------------------------------------------------')


def limpiar_temp():
    """ Limpia archivos temporales
    Dado que se generan archivos temporales ocn cada corrida,
    esta funcion se encarga de eliminar aquellos temporales
    con más de diez días
    """

    # Se eliminan los archivos temporales de hace 10 días
    fecha = datetime.datetime(int(os.getenv('Y')),
                              int(os.getenv('M')),
                              int(os.getenv('D')),
                              int(os.getenv('H')))
    fecha_ant = fecha + datetime.timedelta(days=-10)
    if (os.path.isdir(f"{os.getenv('WRF_OPERATIVO')}/temp/"
                      f"{fecha_ant.strftime('%Y%m%d%H')}")):
        os.system(f"rm -r {os.getenv('WRF_OPERATIVO')}/temp/"
                  f"{fecha_ant.strftime('%Y%m%d%H')}")


def crear_directorios():
    """ Crealos directorios para la corrida
    Esta funcion se encarga de crear todos los directorios y
    subdirectorio de la corrida, utilizando las variables de
    entorno de la misma
    """

    ruta_fecha_hora = (f"{os.getenv('Y')}_{os.getenv('M')}/"
                       f"{os.getenv('D')}_{os.getenv('H')}")
    ruta_fecha = f"{os.getenv('Y')}_{os.getenv('M')}"

    # Directorio de descarga
    os.system(f"mkdir -p {os.getenv('GFS_DIR')}/{ruta_fecha_hora}")
    # Directorio de logs
    os.system(f"mkdir -p {os.getenv('LOGS_DIR')}/{ruta_fecha_hora}")
    # Directorio de datos-meteo
    os.system(f"mkdir -p {os.getenv('METEO_DIR')}/{ruta_fecha}")
    # Directorio de mapas
    os.system(f"mkdir -p {os.getenv('MAPAS_DIR')}/{ruta_fecha_hora}")
    # Directorio de wrfout
    os.system(f"mkdir -p {os.getenv('WRFOUT_DIR')}/{ruta_fecha}")
    # Directorio temporal para cada parametrizacion
    codigos = os.getenv('CODIGOS').split(' ')
    for codigo in codigos:
        os.system(f"mkdir -p {os.getenv('TEMP_DIR')}/{codigo}")


def descargar(i=0):
    """ Esta funcion configura el entorno de descarga de los GFS
    y llama a la función que lo hace
    """
    # Definimos las variables para la funcion download de descarga_GFS025.py
    inidate = (f"{os.getenv('Y')}{os.getenv('M')}"
               f"{os.getenv('D')}{os.getenv('H')}")
    ruta_fecha_hora = (f"{os.getenv('Y')}_{os.getenv('M')}/"
                       f"{os.getenv('D')}_{os.getenv('H')}")
    output = f"{os.getenv('GFS_DIR')}/{ruta_fecha_hora}"

    # Descargamos los GFS
    try:
        list_remote_files, list_files_local = get_list_gfs(inidate)
        download(output, list_remote_files, list_files_local)
    except socket.timeout as err:
        print(err)
        descargar(i)

    # Comprobamos archivos descargados
    archivos = glob.glob(output + '/*')
    for archivo in archivos:
        # chek if the file is too small to be not corrupted
        if os.path.getsize(archivo) < 21*1024*1024:
            os.system(f"rm {archivo}")
    archivos = glob.glob(output + '/*')
    if len(archivos) < (int(os.getenv('RUN_HOURS')) // 3):
        time.sleep(5*60)
        i = i + 1
        if i < 30:
            descargar(i)


def run_wps():
    """ Esta funcion establece el entorno y ejecuta WPS,
    que son los tres pre procesamientos de WRF
    """
    # Definimos las variables para los procesos de WPS
    ruta_fecha_hora = (f"{os.getenv('Y')}_{os.getenv('M')}/"
                       f"{os.getenv('D')}_{os.getenv('H')}")
    data = os.getenv('GFS_DIR') + '/' + ruta_fecha_hora

    # Se linkean los ejecutables de WPS
    os.system(f"mkdir -p {os.getenv('TEMP_DIR')}/WPS")
    os.system(f"ln -sf {os.getenv('WRF_BASE')}/WPS-4.2/* "
              f"{os.getenv('TEMP_DIR')}/WPS/")

    # Se edita el namelist
    editar_namelist_wps()

    os.chdir(f"{os.getenv('TEMP_DIR')}/WPS/")

    # Se ejecuta geogrid
    os.system(f"time ./geogrid.exe > "
              f"$LOGS_DIR/$Y'_'$M/$D'_'$H/geogrid_`date +%Y%m%d%H%M`.log 2>&1")

    # Se ejecuta ungrib
    os.system(f"ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable")
    os.system(f"./link_grib.csh {data}/")
    os.system(f"time ./ungrib.exe > "
              f"$LOGS_DIR/$Y'_'$M/$D'_'$H/ungrib_`date +%Y%m%d%H%M`.log 2>&1")

    # Se ejecuta metgrid
    os.system(f"time ./metgrid.exe > "
              f"$LOGS_DIR/$Y'_'$M/$D'_'$H/metgrid_`date +%Y%m%d%H%M`.log 2>&1")


def gen_final():
    """
    TODO
    """
    pass


def main():
    # Limpiar archivos temporales y crear directorios
    limpiar_temp()
    crear_directorios()

    # Descarga GFS
    if os.getenv('DESCARGAR') == '1':
        log_date('Descarga de GFS')
        descargar()

    # Ejecutar WPS
    if os.getenv('RUN_WPS') == '1':
        log_date('Ejecucion de WPS')
        run_wps()

    # Se obtienen los códigos para las diferentes parametrizaciones
    codigos = os.getenv('CODIGOS').split(' ')
    param_classes = {}

    for codigo in codigos:
        # Se crea la clase para esta parametrización
        param_classes[codigo] = ParametrizacionWRF(codigo)
        # Se ejecuta el WRF y el post-procesamiento para cada prametrización
        param_classes[codigo].run_wrf_post()

        # param_classes[codigo].run_wrf_ingestor()
        # jobs_ids[codigo] = param_classes[codigo].job_id_ingestor

    # Generar media
    gen_final()


if __name__ == "__main__":
    main()
