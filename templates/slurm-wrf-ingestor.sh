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
conda activate wrfplot-env32

cd {{TEMP_DIR}}/{{PARAM}}/wrfplot-v1.2.0/src

# Token para el usuario wrfplot
export API_TOKEN="29736090019d44b8ee4b52ed54ca25e39b40dabb"

time python3 api_ingest_csv.py
