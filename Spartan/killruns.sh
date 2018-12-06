#!/bin/bash

# To use type: ./killruns.sh <StartJob#> <EndJob#> 

for ii in `seq $1 $2`;
do
   qdel $ii
done
