#!/bin/bash
#SBATCH -p RM
#SBATCH -A phy240015p
#SBATCH -N 12
#SBATCH --ntasks-per-node=64
#SBATCH --job-name=zf4Hsd50
#SBATCH --time=48:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=nianyi.chen7@gmail.com

#--------------- Modules -----------------
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/modules_br2.sh

#-------- Copy over relevant files --------
outdir="$HOME/scratch1/1_offcenter_zoom/runs/ZF4_H/seed50"

mkdir -p $outdir
cp param.txt $outdir
cp outputs.txt $outdir
cp Config.sh $outdir
cp ./Arepo $outdir
cd $outdir

#------------- Execute --------------------
mpiexec -np 768 ./Arepo  param.txt > log-$SLURM_JOB_ID
sleep 1
