#!/bin/bash
#SBATCH --job-name={{NOMBRE}}-ingestor
#SBATCH --partition=master
#SBATCH --exclusive

#SBATCH --ntasks=1
#SBATCH --nodes=1

#SBATCH --time=10:00:00
#SBATCH --get-user-env
#SBATCH --workdir={{WORKDIR}}
#SBATCH --output={{LOGS}}
#SBATCH --error={{LOGS-ERR}}

#SBATCH --mail-type=FAIL
#SBATCH --mail-user=amartina@unc.edu.ar

source $WRF_OPERATIVO/env-node.sh

# WRF PLOT INGESTION
conda activate wrfplot-env32

cd {{TEMP_DIR}}/{{PARAM}}/wrfplot/src

# Token para el usuario wrfplot

export API_BASE_URL_DICT='{"https://ohmc.com.ar/wrf-beta/api": {"token": "29736090019d44b8ee4b52ed54ca25e39b40dabb"}, "https://ohmc.com.ar/wrf/api": {"token": "29736090019d44b8ee4b52ed54ca25e39b40dabb"}}'

time python3 api_ingest_csv.py


cd {{TEMP_DIR}}/{{PARAM}}/wrf-cuenca/src

conda activate wrfcuenca3

export API_BASE_URL_DICT='{"https://ohmc.com.ar/wrf-beta/api": {"token": "9c0d4c51ef7a43c3eab966b5cc96b549b2496caf"}, "https://ohmc.com.ar/wrf/api": {"token": "9c0d4c51ef7a43c3eab966b5cc96b549b2496caf"}}'


python api_ingest_csv.py

