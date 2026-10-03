#!/bin/bash
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/load_modules.sh
cd $codedir
make clean DIR=$cwd
make build -j 8 DIR=$cwd
