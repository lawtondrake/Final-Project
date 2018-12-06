#!/bin/bash
clear
#rm rfile*
phiangle=$(awk -v d=$2 'BEGIN {printf "%.6f\n",d}')
phiindex=$(awk -v g=$phiangle -v e=$3 'BEGIN {printf "%d\n",e/g}')
thetaangle=$(awk -v d=$4 'BEGIN {printf "%.6f\n",d}')
thetaindex=$(awk -v g=$thetaangle -v e=360 'BEGIN {printf "%d\n",e/g}')
for jj in `seq 1 $phiindex`;
do
	for kk in `seq 1 $thetaindex`
	do
		thetaname=$(awk -v g=$thetaangle -v j=$kk 'BEGIN {printf "%d\n",g*j-g/2}')
		#thetaname=$(awk -v g=$thetaangle -v j=$kk 'BEGIN {printf "%d\n",g*j}')
		if [[ $thetaname -lt 100 ]]
		then
			if [[ $thetaname -lt 10 ]]
			then
				th=""00$thetaname""
			else
				th=""0$thetaname""
			fi
		else
			th=$thetaname
		fi
		phiname=$(awk -v g=$phiangle -v j=$jj 'BEGIN {printf "%d\n",g*j-g/2}')
		#phiname=$(awk -v g=$phiangle -v j=$jj 'BEGIN {printf "%d\n",g*j}')
		if [[ $phiname -lt 10 ]]
		then
			ph=""00$phiname""
		else
			ph=""0$phiname""
		fi
		fname=""$1th$th""ph$ph""

		echo Running MCNP6 for $fname...
		echo Output file is $fname.o
		echo Run file is $fname.r
		cp MCNPrun.sh MCNPrunTEMP.sh
		sed -i -- "s&mpiexec -n 16 mcnp6.mpi i=Test.inp o=Test.o ru=Test.r&mpiexec -n 16 mcnp6.mpi i=$fname.inp o=$fname.o ru=rfile$fname.r &g" MCNPrunTEMP.sh
		qsub MCNPrunTEMP.sh #&
		#wait %-
		#rm ""$fname"".r""
	done
done
