# -*- coding: utf-8 -*-
"""

"""

import os
import subprocess
import datetime

from namelists import editar_namelist_wrf


class ParametrizacionWRF(object):
    """ """

    def __init__(self, nombre):
        self.nombre = nombre
        self.carpeta = f"{os.getenv('TEMP_DIR')}/{nombre}"

    def generar_slurm_sh(self):
        # Se copia el template
        os.system(f"cp -a {os.getenv('TEMPLATES_DIR')}/slurm-wrf.sh "
                  f"{self.carpeta}/slurm-wrf.sh")

        # Se reemplazan las variables en el runner
        fecha = datetime.datetime(int(os.getenv('Y')),
                                  int(os.getenv('M')),
                                  int(os.getenv('D')),
                                  int(os.getenv('H')))
        ruta_fecha_hora = fecha.strftime('%Y_%m/%d_%H')
        with open(self.carpeta + '/slurm-wrf.sh', 'r') as file:
            filedata = file.read()

        filedata = filedata.replace('{{NOMBRE}}', f"WRF-{self.nombre}")
        filedata = filedata.replace('{{WORKDIR}}', os.getenv('WRF_OPERATIVO'))
        filedata = filedata.replace('{{LOGS}}', f"{os.getenv('LOGS_DIR')}/"
                                                f"{ruta_fecha_hora}/"
                                                f"slurm-{self.nombre}-%j.out")
        filedata = filedata.replace('{{PARAM}}', self.nombre)
        with open(self.carpeta + '/slurm-wrf.sh', 'w') as file:
            file.write(filedata)

    def run_wrf_post(self):
        os.chdir(self.carpeta)

        self.generar_slurm_sh(self)

        _, output = subprocess.getstatusoutput('sbatch slurm-wrf.sh')
        self.job_id = output.split(' ')[3]

    def run_wrf(self):
        print('Se linkean los ejecutables de WRF')
        os.system('mkdir -p ' + self.carpeta + '/WRF')
        os.system('ln -sf ' + os.getenv('WRF_BASE') + '/WRFV3/test/em_real/* ' + self.carpeta + '/WRF/')

        print('Se linkean las salidas de WPS')
        os.system('ln -sf ' + os.getenv('TEMP_DIR') + '/WPS/met_em.* ' + self.carpeta + '/WRF/')

        print('Se edita el namelist para ' + self.nombre)
        editar_namelist_wrf(self.nombre)

        os.chdir(self.carpeta + '/WRF/')

        print('Se ejecuta el REAL')
        os.system("time prun ./real.exe > $LOGS_DIR/$Y'_'$M/$D'_'$H/real_" + self.nombre  + "_`date +%Y%m%d%H%M`.log 2>&1")

        print('Se ejecuta el WRF')
        os.system("time prun ./wrf.exe > $LOGS_DIR/$Y'_'$M/$D'_'$H/wrf_" + self.nombre + "_`date +%Y%m%d%H%M`.log 2>&1")

    def extraer_variables(self):
        pass

    def tabla_datos(self):
        pass

    def generar_graficos(self):
        pass
