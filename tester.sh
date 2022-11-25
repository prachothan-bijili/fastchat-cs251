#!/bin/bash
n=$1
python3 conn_tester.py $n
for((i=0; i<$n; i++))
do
    python3 chat_client.py $i 
    sleep 0.000001
done 
rm -f *.txt
exit 1
