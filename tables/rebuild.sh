#!/bin/bash
typeset -A MODELS2OPT=( [bin]="-b" [std]="" )
typeset -A FORMAT2EXT=( [csv]="csv" [json]="json" [yaml]="yml" [text]="txt" )

mydir=$(dirname $BASH_SOURCE[0])
cd $mydir

for num in 100 5000 ; do
    for format in "${!FORMAT2EXT[@]}"; do
	for COST in "${!MODELS2OPT[@]}"; do
	    typeset filename=${num}-${COST}cost.${FORMAT2EXT[$format]}
	    cmd="mult-by-const ${MODELS2OPT[$COST]} --to ${num} --fmt $format -o $filename"
	    echo $cmd
	    $cmd
	done
    done
done
