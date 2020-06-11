#!/bin/bash
#SBATCH --job-name={{NOMBRE}}-new
#SBATCH --partition=WRF-norm
#SBATCH --exclusive

#SBATCH --ntasks=32
#SBATCH --nodes=1

#SBATCH --time=10:00:00
#SBATCH --get-user-env
#SBATCH --workdir={{WORKDIR}}
#SBATCH --output={{LOGS}}
#SBATCH --error={{LOGS-ERR}}

#SBATCH --mail-type=FAIL
#SBATCH --mail-user=amartina@unc.edu.ar

python $WRF_OPERATIVO/runWRFpost.py --param={{PARAM}}

cp -a $HOME/wrfplot-v1.2.0 {{TEMP_DIR}}/{{PARAM}}/

cd {{TEMP_DIR}}/{{PARAM}}/wrfplot-v1.2.0/src

source $WRF_OPERATIVO/env-node.sh
conda activate wrfplot-env32

ray start --head --redis-port=6379 --num-cpus=32 # --object-store-memory 42949672960 --redis-max-memory 21474836480

time python3 productos_eureka.py {{WRFOUT}} {{OUTDIR}} {{OUTDIR_WM}}

time python3 tabla_datos.py {{WRFOUT}} /home/wrf/datos-webwrf/datos-meteo/ 'CBA_{{PARAM}}_'$H

ray stop

source activate wrfcuenca3

cp -a $HOME/wrf-cuenca-v0.9.0 {{TEMP_DIR}}/{{PARAM}}/

cd {{TEMP_DIR}}/{{PARAM}}/wrf-cuenca-v0.9.0/src

ray start --head --redis-port=6379 --num-cpus=30

time python3 cuencas_wrf.py {{WRFOUT}}  /home/wrf/datos-webwrf/img/plots/ /home/wrf/datos-webwrf/datos-meteo/

ray stop

