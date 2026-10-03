#!/bin/bash
#SBATCH -p p.exclusive
#SBATCH -N 4
#SBATCH --ntasks-per-node=112
#SBATCH --job-name=zf4tmpl-r
#SBATCH --time=23:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=nianyi.chen7@gmail.com

# Restart from output/restartfiles (Arepo flag 1). Resubmits itself until output/end exists.
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/load_modules.sh

outdir="$HOME/scratch1/1_offcenter_zoom/runs/templates/zf4_tde"
cp param.txt $outdir
cp outputs.txt $outdir
cd $outdir

mpiexec -np 448 ./Arepo  param.txt 1 > log-$SLURM_JOB_ID
sleep 1
if [ ! -f output/end ]; then
    cd $cwd
    sbatch --dependency=afterany:$SLURM_JOB_ID restart.sh
fi
