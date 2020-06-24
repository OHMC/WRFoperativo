#!/bin/bash

RES=$(sbatch slurm-wrf.sh) && sbatch --dependency=afterok:${RES##* } slurm-wrf-ingestor.sh
