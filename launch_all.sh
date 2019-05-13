#!/bin/bash

NB_TERMS="None"
SUB_FOLDER="None"
TRS_FOLDER="None"
REMOVE_FACT=0.25
MIN_ORDER=0.01
LANGUAGE="french"
POS=1

while getopts "it:s:n:r:o:l:p:" option
do
	case $option in
		i) pip3 install -r requirements.txt ;;
		t) TRS_FOLDER=$OPTARG ;;
		s) SUB_FOLDER=$OPTARG ;;
		n) 
			NB_TERMS=$OPTARG 
			;;
		r) 	REMOVE_FACT=$OPTARG 
			;;
		o)	MIN_ORDER=$OPTARG 
			;;
		l)	LANGUAGE=$OPTARG
			;;
		p)	POS=$OPTARG
			;;
		:) 
			echo "Option $OPTARG requires an argument"
			exit 1
			;;
		\?)
			echo "$OPTARG: invalid option" 
			exit 1
			;;
	esac
done

if [ -f "stop_"$LANGUAGE".txt" ];
then
   echo "INFO: Language stop word file stop_"$LANGUAGE".txt exists."
else
   echo "INFO: Language stop word file stop_"$LANGUAGE".txt does not exist. Abort!"
   exit 1
fi

if [ "$SUB_FOLDER" == "None" ]; then
	echo "ERROR: The subtitle folder is mandatory. USAGE: -s [subtitle_folder]."
	exit 1
fi

re='^[0-9]+([.][0-9]+)?$'
if ! [[ $REMOVE_FACT =~ $re ]] ; then
	echo "ERROR: The factor for term removal is negative or it is not a float."
	exit 1
fi

if [ $(echo " $REMOVE_FACT > 0.9 " | bc) -eq 1 ] ; then
	echo "ERROR: The factor for term removal is greater than 0.9. Think again..."
	exit 1
fi

if ! [[ $MIN_ORDER =~ $re ]] ; then
	echo "ERROR: The factor for local minimum order is negative or it is not a float."
	exit 1
fi

if [ $(echo " $MIN_ORDER > 0.5 " | bc) -eq 1 ] ; then
	echo "ERROR: The factor for local minimum order is greater than 0.5. Think again..."
	exit 1
fi

if [ "$NB_TERMS" -eq "$NB_TERMS" ] 2>/dev/null
then
	:
else
    echo "ERROR: Paramter -n (number of terms) must be an integer. USAGE: -n [integer_nb_of_terms]"
    exit 1
fi

if [ "$POS" -eq "$POS" ] 2>/dev/null
then
	if [ "$POS" -eq 0 ]
	then
		echo "INFO: POS will not be employed."
	else
		if [ "$POS" -eq 1 ]
		then
			echo "INFO: POS will be employed."
		else
			echo "ERROR: Parameter -p (with or without POS) must be 0 or 1."
		fi
	fi		
else
    echo "ERROR: Paramter -p (with or without POS) must be an integer (0 or 1). USAGE: -n [integer_nb_of_terms]"
    exit 1
fi

if [ "$TRS_FOLDER" == "None" ]; then
	echo "INFO: No .trs subtitle folder given. Bypassing..."
else
	for TRS_FILE in $(ls $TRS_FOLDER)
	do
		FILENAME="${TRS_FILE%.*}"
		echo "INFO: Converting subtitle file: "$TRS_FILE
		python3 trs2srt.py $TRS_FOLDER$TRS_FILE $SUB_FOLDER$FILENAME".srt"
	done
	
fi
rm -rf srt2txt
rm -rf json
#rm -rf graphs
#rm -rf output

mkdir srt2txt
mkdir json
#mkdir graphs
#mkdir output

for SRT_FILE in $(ls $SUB_FOLDER)
do
	FILENAME="${SRT_FILE%.*}"
	echo "INFO: Treating file:" $FILENAME
	python3 srt2txt.py $SUB_FOLDER$SRT_FILE "srt2txt/"$FILENAME".txt"
	python3 freq_terms.py $NB_TERMS "srt2txt/"$FILENAME".txt" "json/"$FILENAME".json" $LANGUAGE $POS
	python3 lexical_chains.py $NB_TERMS "json/"$FILENAME".json" "graphs/lang-"$LANGUAGE".pos-"$POS".NB-"$NB_TERMS".rem-"$REMOVE_FACT".min-"$MIN_ORDER"."$FILENAME $SUB_FOLDER$SRT_FILE "output/lang-"$LANGUAGE".pos-"$POS".NB-"$NB_TERMS".rem-"$REMOVE_FACT".min-"$MIN_ORDER"."$FILENAME".xml" $REMOVE_FACT $MIN_ORDER	
done

