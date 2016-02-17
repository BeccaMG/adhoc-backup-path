#!/bin/bash
IPLIST="hosts"


for ip in $(cat $IPLIST)

do
    ping $ip -c 1 -t 1 &> /dev/null
    if [ $? -ne 0 ]; then

        echo $ip ping failed;

        else

        echo $ip ping passed;

    fi

done
