#!/bin/bash


iptables -F geoip-input
ip6tables -F geoip6-input
iptables -F geoip-output
ip6tables -F geoip6-output

for cc in RU BY KP CN
do
	ipset create ipnet-$cc hash:net -4 || true
	ipset flush ipnet-$cc
	ipset create ip6net-$cc hash:net -6 || true
	ipset flush ip6net-$cc
	while read network
	do

		if [[ $network =~ ":" ]]
		then
			ipset add ip6net-$cc $network
		else
			ipset add ipnet-$cc $network
		fi

	done < <(python3 ./geoip.py -cidr $cc | grep -v '^#')
	
	iptables -A geoip-input -m set --match-set ipnet-$cc src -m comment --comment GEOIP_BLOCK_$cc -j DROP
	ip6tables -A geoip6-input -m set --match-set ip6net-$cc src -m comment --comment GEOIP_BLOCK_$cc -j DROP

	iptables -A geoip-output -m set --match-set ipnet-$cc dst -m comment --comment GEOIP_BLOCK_$cc -j DROP
	ip6tables -A geoip6-output -m set --match-set ip6net-$cc dst -m comment --comment GEOIP_BLOCK_$cc -j DROP
done
