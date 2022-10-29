#!/usr/bin/env bash
all_ip=`hostname -I`
phy_ip=`hostname -i`
first_vip=`echo ${all_ip/$phy_ip/\ }|awk '{print $1}'`
all_vip=`echo ${all_ip/$phy_ip/\ }`
default_gateway=`route -n|grep -w UG|awk '{print $2}'`
phy_net_card=`route -n|grep -w UG|awk '{print $8}'`
ping -i 1 -c2 -w 3  -I $first_vip $default_gateway &> /dev/null
if [ "$?" == "1" ]; then
    ping -i 1 -c2 -w 3  $default_gateway  &> /dev/null
    if [ "$?" == "0" ]; then
        for each_vip in $all_vip;do
            /usr/sbin/arping -I $phy_net_card -c 2 -s $each_vip $default_gateway
            done
    fi
fi