# -*- coding: utf-8 -*-
""" Este archivo incluye funciones que permiten la manipulación de
los archvios de configuración de del modelo numerico WRF
"""

import os
import datetime


def editar_namelist_wps():
    """ Esta funcion configura el namelist.wps reemplazando
    las variables correspondiente a la corrida seteada en el entorno
    """
    # Obtengo la fecha de simulación
    fecha = datetime.datetime(int(os.getenv('Y')),
                              int(os.getenv('M')),
                              int(os.getenv('D')),
                              int(os.getenv('H')))
    start_date = f"{fecha.strftime('%Y-%m-%d_%H')}:00:00"
    date_run_hours = datetime.timedelta(hours=int(os.getenv('RUN_HOURS')))
    end_date = f"{(fecha + date_run_hours).strftime('%Y-%m-%d_%H')}:00:00"

    # Se copia el namelist temporal
    os.system(f"cp -a {os.getenv('NAMELISTS_DIR')}/namelistTemp.wps "
              f"{os.getenv('TEMP_DIR')}/WPS/namelist.wps")

    # Se reemplazan las variables en el namelist
    with open(f"{os.getenv('TEMP_DIR')}/WPS/namelist.wps", 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('START_DATE', start_date)
    filedata = filedata.replace('END_DATE', end_date)
    filedata = filedata.replace('RUTA_GEOG_DATA', os.getenv('WPS_GEOG'))
    filedata = filedata.replace('REF_LAT', os.getenv('REF_LAT'))
    filedata = filedata.replace('REF_LON', os.getenv('REF_LON'))
    filedata = filedata.replace('TRUELAT1', os.getenv('TRUELAT1'))
    filedata = filedata.replace('TRUELAT2', os.getenv('TRUELAT2'))
    filedata = filedata.replace('STAND_LON', os.getenv('STAND_LON'))
    with open(f"{os.getenv('TEMP_DIR')}/WPS/namelist.wps", 'w') as file:
        file.write(filedata)


def editar_namelist_wrf(param):
    """ Esta funcion configura el namelist.input reemplazando
    las variables correspondiente a la corrida seteada en el entorno
    """
    # Obtengo la fecha de simulación
    fecha = datetime.datetime(int(os.getenv('Y')),
                              int(os.getenv('M')),
                              int(os.getenv('D')),
                              int(os.getenv('H')))
    fecha_fin = fecha + datetime.timedelta(hours=int(os.getenv('RUN_HOURS')))

    ruta_wrf = f"{os.getenv('TEMP_DIR')}/{param}/WRF"
    history_outname = (f"{os.getenv('WRFOUT_DIR')}{fecha.strftime('/%Y_%m/')}"
                       f"wrfout_{param}_d<domain>_<date>.nc")

    # Se copia el namelist temporal
    os.system(f"rm {ruta_wrf}/namelist.input")
    os.system(f"cp -a {os.getenv('NAMELISTS_DIR')}/namelistTemp_{param}.input "
              f"{ruta_wrf}/namelist.input")

    # Se reemplazan las variables en el namelist
    with open(f"{ruta_wrf}/namelist.input", 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('RUN_HOURS', os.getenv('RUN_HOURS'))
    filedata = filedata.replace('START_YEAR', fecha.strftime('%Y'))
    filedata = filedata.replace('START_MONTH', fecha.strftime('%m'))
    filedata = filedata.replace('START_DAY', fecha.strftime('%d'))
    filedata = filedata.replace('START_HOUR', fecha.strftime('%H'))
    filedata = filedata.replace('START_MINUTE', fecha.strftime('%M'))
    filedata = filedata.replace('START_SECOND', fecha.strftime('%S'))
    filedata = filedata.replace('END_YEAR', fecha_fin.strftime('%Y'))
    filedata = filedata.replace('END_MONTH', fecha_fin.strftime('%m'))
    filedata = filedata.replace('END_DAY', fecha_fin.strftime('%d'))
    filedata = filedata.replace('END_HOUR', fecha_fin.strftime('%H'))
    filedata = filedata.replace('END_MINUTE', fecha_fin.strftime('%M'))
    filedata = filedata.replace('END_SECOND', fecha_fin.strftime('%S'))
    filedata = filedata.replace('HISTORY_OUTNAME', history_outname)

    with open(f"{ruta_wrf}/namelist.input", 'w') as file:
        file.write(filedata)
