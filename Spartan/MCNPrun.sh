#!/bin/bash
#PBS -N MCNP
#PBS -S /bin/bash
#PBS -l nodes=1:ppn=16
#PBS -l walltime=00:10:00
#PBS -r n
#PBS -V
#PBS -m ae

cd $PBS_O_WORKDIR
mpiexec -n 16 mcnp6.mpi i=Test.inp o=Test.o ru=Test.r

date
