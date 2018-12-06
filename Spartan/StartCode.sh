#!/bin/bash
# To run us ./StartCode FolderToSaveFiles
# $1 is the folder name

detdistance=86.36    # Detector distance (cm)
erg=14			 # Detector energy (MeV)
delta_theta=22.5		 # Theta discretization (degrees) 90 must be evenly divisible by this number
delta_phi=22.5		 # Phi discretization (degrees) 90 must be evenly divisible by this number
end_phi=165			 # Phi angle limit (degrees) must be <= 180-delta_phi
StructMesh=1		 # Use MCNP CSG (1) or unstructured mesh (0) NOTE: UM is not currently enabled
nps=500000			 # Number of particles to run (should be >0 500000 without importance weighting)
cluster=0			 # Run single processor on single machine (0) or submit all angles to cluster (100+ jobs)





#*************************************** Run code *********************************************
# Create new directory otherwise give error so not overwritten
if [ -d "$1" ];
then
	echo "Folder already exists."
	echo "No files created." 
else
	# Update settings with input variables in this file
	mkdir "$1"
	iname="$1master"
	cp "RunTemplate.py" "$iname.py"
	# Modify Mablab base design variables
	sed -i -e  "s?StructMesh=1?StructMesh=$StructMesh?g" $iname.py
	sed -i -e  "s/nps=5000/nps=$nps/g" $iname.py
	
	rname="$1run.inp"
	sed -i -e  "s?MainDir='./Test'?MainDir='./$1'?g" $iname.py
	sed -i -e  "s?fout=MainDir + '/mcnp.inp'?fout=MainDir + '/$rname'?g" $iname.py
	sed -i -e  "s?delta_theta=10.?delta_theta=$delta_theta?g" $iname.py
	sed -i -e  "s?delta_phi=10.?delta_phi=$delta_phi?g" $iname.py
	sed -i -e  "s?end_phi=170?end_phi=$end_phi.?g" $iname.py
	
	# Create new design
	python3 ./$iname.py

	# Create all MCNP input files from master
	cp "MCNPrun.sh" "./$1" 
	cd $1
	phiangle=$(awk -v d=$delta_phi 'BEGIN {printf "%.6f\n",d}')
	phiindex=$(awk -v g=$phiangle -v e=$end_phi 'BEGIN {printf "%d\n",e/g}')
	thetaangle=$(awk -v d=$delta_theta 'BEGIN {printf "%.6f\n",d}')
	thetaindex=$(awk -v g=$thetaangle -v e=360 'BEGIN {printf "%d\n",e/g}')
	# Cycle through source phi angles
	for jj in `seq 1 $phiindex`;
	do 
		ii=$(awk -v d=$jj -v j=$phiangle 'BEGIN {printf "%.6f\n",d*j-j/2 + 0.01}')
		detector_z=$(awk -v d=$detdistance -v ph=$ii -v s=$Struc 'BEGIN {printf "%.6f\n",d*cos(ph*atan2(0,-1)/180+s)}')
		ndetector_z=$(awk -v d=$detector_z 'BEGIN {printf "%.6f\n",-d}')
	
		detector_r=$(awk -v d=$detdistance -v ph=$ii -v s=$Struc 'BEGIN {printf "%.6f\n",d*sin(ph*atan2(0,-1)/180+s)}')
		# Cycle through source theta angles
		for kk in `seq 1 $thetaindex` 
		do
			rr=$(awk -v d=$kk -v j=$thetaangle 'BEGIN {printf "%.6f\n",d*j-j/2 + 0.01}')
			detector_x=$(awk -v d=$detector_r -v thet=$rr -v s=$Struc 'BEGIN {printf "%.6f\n",d*cos(thet*atan2(0,-1)/180+s)}')
			detector_y=$(awk -v d=$detector_r -v thet=$rr -v s=$Struc 'BEGIN {printf "%.6f\n",d*sin(thet*atan2(0,-1)/180+s)}')
			ndetector_x=$(awk -v d=$detector_x 'BEGIN {printf "%.6f\n",-d}')
			ndetector_y=$(awk -v d=$detector_y 'BEGIN {printf "%.6f\n",-d}')

			# Create MCNP input and output file names
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
			if [[ $phiname -lt 100 ]]
			then
				if [[ $phiname -lt 10 ]]
				then
					ph=""00$phiname""
				else
					ph=""0$phiname""
				fi
			else
				ph=$phiname
			fi
			oname=""$1th$th""ph$ph"".inp""
            echo 'Creating MCNP input file: '$oname 
			cp $rname "$oname"
			
			# Change source definition based on variables in this file
			sed -i -e  "s/sdef erg 0.662 pos 0.015073 0.000003 86.359999/sdef erg $erg pos $detector_x $detector_y $detector_z/g" $oname
			sed -i -e  "s/vec -0.015073 -0.000003 -86.359999/vec $ndetector_x $ndetector_y $ndetector_z/g" $oname
			chmod a+x "$oname"
		done
	done
	
	# 
	echo $(pwd)
	# Choose how to run the simulations.  Single computer or via qsub
	if [[ $cluster -eq 0 ]]
	then
		# Run MCNP on single computer using a single processor
	    ../runbatch.sh $1 $delta_phi $end_phi $delta_theta
	    # Use multiple processors (currently not enabled)
	    #../runbatchmulti.sh $1 $delta_phi $end_phi $delta_theta
	else
	    # Run MCNP on cluster
	    ../runcluster.sh $1 $delta_phi $end_phi $delta_theta
	fi
	cd ..
	
	echo "Generatating output..."
	
	echo "Run Completed"
fi
