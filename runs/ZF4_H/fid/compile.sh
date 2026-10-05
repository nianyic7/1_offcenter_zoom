#!/bin/bash
codedir="$HOME/arepo"
cwd=$(pwd)
source $codedir/modules_br2.sh
cd $codedir
make clean DIR=$cwd
make build -j 8 DIR=$cwd
