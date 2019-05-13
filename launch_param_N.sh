#!/bin/bash

REMOVE_FACT=0.25
MIN_ORDER=0.01

num=$(awk 'BEGIN{for(i=10;i<=150;i+=10)print i}')
numF=$(awk 'BEGIN{for(i=0.05;i<=0.9;i+=0.05)print i}')
numM=$(awk 'BEGIN{for(i=0.01;i<=1;i+=0.01)print i}')


for N in $num
	for REMOVE_FACT in $numF
		for MIN_ORDER in $numM
		do
			echo $N
			echo $REMOVE_FACT
			echo $MIN_ORDER
			./launch_all.sh -t trs/ -s srt/ -n $N -r $REMOVE_FACT -o $MIN_ORDER
			cp -r output/ output_$N"_"$REMOVE_FACT"_"$MIN_ORDER
			cp -r json/ json_$N"_"$REMOVE_FACT"_"$MIN_ORDER
			cp -r graphs/ graphs_$N"_"$REMOVE_FACT"_"$MIN_ORDER
		done
	done
done
	
