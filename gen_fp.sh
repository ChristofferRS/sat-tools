#!/bin/bash

##   This script was create by Christoffer to generate russia FP from SDK outpu
##   It was just a siplifyed version of the original tx_i_short.sh
##   Just give the imput and the advance. The putput can easyally be piped to a new file. I did not implement file creation
##   directly since it keeps the script more general. Just use ./gen_fp.sh [SDK-FILE] [Advance] >> new_file.txt
##   to create a file containing th flightplan


usage="$(basename "$0") [SDK-file] [advance] -- program to generate flighplan uding SDK output format.

SDK-file: the file outputet from SDK prediction
advacne: seconds before timetamp to execute command

To create a fligplan file ude:
   command > filename        Redirect command output to a file

   command >> filename       APPEND into a file

"
if [ "$1" == "-h" ]; then
  echo "$usage"
  exit 0
fi

#The imput neeeded
filename=$1
advance=$2

if [ -z "$filename" ] || [ -z "$advance" ]; then
echo "Missing imput. Read usage."
echo "$usage"
exit 0
fi
# Create array from alle the lines containg timestamps
readarray dates < <(egrep "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec" $filename | awk '{print $2, $3, $4, $5, $10}' |  sed 1d | sed '/Duration/d' )

#Converts all dates to correct format, and store them in an array
times=()
for item in "${dates[@]}"
do
cur_date=$(echo $item | cut -d ' ' -f1,2,3,4)
times+=($(date --date date -u --date="${cur_date}" +"%s"))
done


#Print the result

###################################
## If putput incorrect change here:
###################################

for ((i=0;i<${#times[@]};i++)); do
dur=$(echo ${dates[i]} | cut -d ' ' -f5 | cut -d '.' -f1)
echo ""tx_inhibit$((number++))",rparam download 5 0,0,0,0,0,"$((${times[i]}-$advance))",0,1
"tx_inhibit$((number++))",rparam set tx_inhibit "$dur",1,0,0,0,"$((${times[i]}+4-$advance))",0,1"
done
