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
        filedata = filedata.replace('{{TEMP_DIR}}', os.getenv('TEMP_DIR'))
        filedata = filedata.replace('{{LOGS}}', f"{os.getenv('LOGS_DIR')}/"
                                                f"{ruta_fecha_hora}/"
                                                f"slurm-{self.nombre}-%j.out")
        filedata = filedata.replace('{{LOGS-ERR}}', f"{os.getenv('LOGS_DIR')}/"
                                                    f"{ruta_fecha_hora}"
                                                    f"/slurm-{self.nombre}-"
                                                    f"%j.err")
        filedata = filedata.replace('{{PARAM}}', self.nombre)
        filedata = filedata.replace('{{WRFOUT}}', f"{os.getenv('WRFOUT_DIR')}/"
                                                  f"{os.getenv('Y')}_"
                                                  f"{os.getenv('M')}"
                                                  f"/wrfout_{self.nombre}_d01_"
                                                  f"{os.getenv('Y')}-"
                                                  f"{os.getenv('M')}-"
                                                  f"{os.getenv('D')}_"
                                                  f"{os.getenv('H')}:00:00")
        filedata = filedata.replace('{{OUTDIR}}', f"/home/wrf/datos-webwrf/img/"
                                                  f"{os.getenv('REGION')}/"
                                                  f"{self.nombre}/"
                                                  f"{os.getenv('Y')}_"
                                                  f"{os.getenv('M')}/"
                                                  f"{os.getenv('D')}_"
                                                  f"{os.getenv('H')}/")
        filedata = filedata.replace('{{OUTDIR_WM}}', f"/home/wrf/"
                                                     f"datos-webwrf/img/webmet/"
                                                     f"{self.nombre}/")
        with open(self.carpeta + '/slurm-wrf.sh', 'w') as file:
            file.write(filedata)

    def generar_slurm_sh_ingestor(self):
        # Se copia el template
        os.system(f"cp -a {os.getenv('TEMPLATES_DIR')}/slurm-wrf-ingestor.sh "
                  f"{self.carpeta}/slurm-wrf-ingestor.sh")

        # Se reemplazan las variables en el runner
        fecha = datetime.datetime(int(os.getenv('Y')),
                                  int(os.getenv('M')),
                                  int(os.getenv('D')),
                                  int(os.getenv('H')))
        ruta_fecha_hora = fecha.strftime('%Y_%m/%d_%H')
        with open(self.carpeta + '/slurm-wrf-ingestor.sh', 'r') as file:
            filedata = file.read()

        filedata = filedata.replace('{{NOMBRE}}', f"WRF-{self.nombre}")
        filedata = filedata.replace('{{TEMP_DIR}}', os.getenv('TEMP_DIR'))
        filedata = filedata.replace('{{WORKDIR}}', os.getenv('WRF_OPERATIVO'))
        filedata = filedata.replace('{{LOGS}}', f"{os.getenv('LOGS_DIR')}/"
                                                f"{ruta_fecha_hora}/"
                                                f"slurm-{self.nombre}-%j.out")
        filedata = filedata.replace('{{LOGS-ERR}}', f"{os.getenv('LOGS_DIR')}/"
                                                    f"{ruta_fecha_hora}"
                                                    f"/slurm-{self.nombre}-"
                                                    f"%j.err")
        filedata = filedata.replace('{{PARAM}}', self.nombre)
        with open(self.carpeta + '/slurm-wrf-ingestor.sh', 'w') as file:
            file.write(filedata)

    def run_wrf_post(self):
        os.chdir(self.carpeta)
        print(f"slef: {self}")

        self.generar_slurm_sh()
        _, output = subprocess.getstatusoutput('sbatch slurm-wrf.sh')
        self.job_id = output.split(' ')[3]

    def run_wrf_ingestor(self):
        os.chdir(self.carpeta)

        self.generar_slurm_sh_ingestor()

        _, output = subprocess.getstatusoutput('slurm-wrf-ingestor.sh')
        self.job_id = output.split(' ')[3]

    def run_wrf(self):
        print('Se linkean los ejecutables de WRF')
        os.system(f"mkdir -p {self.carpeta}/WRF")
        os.system(f"ln -sf {os.getenv('WRF_BASE')}/WRF-4.1.1/test/em_real/* "
                  f"{self.carpeta}/WRF/")

        print('Se linkean las salidas de WPS')
        os.system(f"ln -sf {os.getenv('TEMP_DIR')}/WPS/met_em.* "
                  f"{self.carpeta}/WRF/")

        print(f"Se edita el namelist para {self.nombre}")
        editar_namelist_wrf(self.nombre)

        os.chdir(f"{self.carpeta}/WRF/")

        print('Se ejecuta el REAL')
        os.system(f"time prun ./real.exe > $LOGS_DIR/$Y'_'$M/$D'_'$H/real_"
                  f"{self.nombre}_`date +%Y%m%d%H%M`.log 2>&1")

        print('Se ejecuta el WRF')
        os.system(f"time prun ./wrf.exe > $LOGS_DIR/$Y'_'$M/$D'_'$H/wrf_"
                  f"{self.nombre}_`date +%Y%m%d%H%M`.log 2>&1")

    def extraer_variables(self):
        pass

    def tabla_datos(self):
        pass

    def generar_graficos(self):
        pass
