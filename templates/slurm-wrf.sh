#!/bin/bash
#SBATCH --job-name={{NOMBRE}}
#SBATCH --partition=normal
#SBATCH --exclusive

#SBATCH --ntasks=32
#SBATCH --nodes=1

#SBATCH --time=04:00:00
#SBATCH --get-user-env
#SBATCH --workdir={{WORKDIR}}
#SBATCH --output={{LOGS}}
#SBATCH --error={{LOGS-ERR}}
#SBATCH --time=02:00:00

#SBATCH --mail-type=FAIL
#SBATCH --mail-user=gonzalo.zigaran@alumnos.unc.edu.ar

python $WRF_OPERATIVO/runWRFpost.py --param={{PARAM}}
