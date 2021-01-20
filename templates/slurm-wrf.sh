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

python3 $WRF_OPERATIVO/runWRFpost.py --param={{PARAM}}

cp -a $HOME/wrfplot {{TEMP_DIR}}/{{PARAM}}/

cd {{TEMP_DIR}}/{{PARAM}}/wrfplot/src

source /home/wrf/WRFoperativo/env-node.sh
conda activate wrfplot-env32

ray start --head --redis-port=6379 --num-cpus=32 # --object-store-memory 42949672960 --redis-max-memory 21474836480
#ray start --head --port=6379 --num-cpus=16
time python3 productos_eureka.py {{WRFOUT}} {{OUTDIR}} {{OUTDIR_WM}}

time python3 tabla_datos.py {{WRFOUT}} /home/wrf/datos-webwrf/datos-meteo/ 'CBA_{{PARAM}}_'$H

ray stop

conda deactivate

conda activate wrfcuenca3

cp -a $HOME/wrf-cuenca {{TEMP_DIR}}/{{PARAM}}/

cd {{TEMP_DIR}}/{{PARAM}}/wrf-cuenca/src

export API_BASE_URL_DICT='{"https://ohmc.com.ar/wrf-beta/api": {"token": "9c0d4c51ef7a43c3eab966b5cc96b549b2496caf"}, "https://ohmc.com.ar/wrf/api": {"token": "9c0d4c51ef7a43c3eab966b5cc96b549b2496caf"}}'

ray start --head --redis-port=6379 --num-cpus=4
#ray start --head --port=6379 --num-cpus=16
time python3 cuencas_wrf.py {{WRFOUT}}  /home/wrf/datos-webwrf/img/ /home/wrf/datos-webwrf/datos-meteo/

ray stop

