#!/bin/bash
#SBATCH -p p.exclusive
#SBATCH -N 4
#SBATCH --ntasks-per-node=112
#SBATCH --job-name=zf4tmpl
#SBATCH --time=23:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=nianyi.chen7@gmail.com

#--------------- Modules -----------------
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/load_modules.sh

#-------- Copy over relevant files --------
outdir="$HOME/scratch1/1_offcenter_zoom/runs/templates/zf4_tde"

mkdir -p $outdir
cp param.txt $outdir
cp outputs.txt $outdir
cp Config.sh $outdir
cp ./Arepo $outdir
cd $outdir

#------------- Execute --------------------
mpiexec -np 448 ./Arepo  param.txt > log-$SLURM_JOB_ID
sleep 1
