#!/bin/bash
#SBATCH -p RM
#SBATCH -A phy240015p
#SBATCH -N 12
#SBATCH --ntasks-per-node=64
#SBATCH --job-name=zf4Hsd50-r
#SBATCH --time=48:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=nianyi.chen7@gmail.com

# Restart from output/restartfiles (Arepo flag 1). Resubmits itself until output/end exists.
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/modules_br2.sh

outdir="$HOME/scratch1/1_offcenter_zoom/runs/ZF4_H/seed50"
cp param.txt $outdir
cp outputs.txt $outdir
cd $outdir

mpiexec -np 768 ./Arepo  param.txt 1 > log-$SLURM_JOB_ID
sleep 1
if [ ! -f output/end ]; then
    cd $cwd
    sbatch --dependency=afterany:$SLURM_JOB_ID restart.sh
fi
