#!/bin/bash

V_NET=$8
CLUSTER=$7
IP1=$1
IP2=$2
IP3=$3
HOSTNAME=$4
HOSTNAME2=$5
HOSTNAME3=$6


function download_resource {
	mkdir -p /var/log/install_master/
	cd /tmp
	curl -O "https://heye-media.bj.bcebos.com/media/k8s1.14.7-master.tar"  2>&- 1>&-
	tar -xf k8s1.14.7-master.tar 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
	cd k8s1.14.7-master 2>&- 1>&-
	/usr/bin/cp -rf * /usr/bin 2>&- 1>&-
	cd /tmp
	curl -O "https://heye-media.bj.bcebos.com/media/master_service.tar" 2>&- 1>&- 
	tar -xf master_service.tar  2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
	cd master_service 2>&- 1>&-
	/usr/bin/cp -rf flanneld /etc/kubernetes/ 2>&- 1>&- 
	/usr/bin/cp -rf * /usr/lib/systemd/system/ 2>&- 1>&-
}


function install_etcd() {





	sed -i 's/?IP1?/'$IP1'/g'  /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's/?IP2?/'$IP2'/g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's/?IP3?/'$IP3'/g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's/?HOSTNAME?/'$HOSTNAME'/g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's/?HOSTNAME2?/'$HOSTNAME2'/g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's/?HOSTNAME3?/'$HOSTNAME3'/g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	sed -i 's|?CLUSTER?|'$CLUSTER'|g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	# etcd.service lack of =
	sed -i 's|--initial-cluster |--initial-cluster=|g' /usr/lib/systemd/system/etcd.service 2>&- 1>&-
	#sed -i 's/?TOKEN?/'$TOKEN'/g' 2>&- 1>&-
	systemctl daemon-reload 2>&- 1>&-
	systemctl enable etcd 2>&- 1>&-
	systemctl start etcd 2>&- 1>&-
	etcdctl --endpoints=$CLUSTER \
	  --ca-file=/etc/kubernetes/pki/etcd-ca.crt \
	  --cert-file=/etc/kubernetes/pki/etcd.crt \
	  --key-file=/etc/kubernetes/pki/etcd.key \
	  mkdir /kube-centos/network 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
	etcdctl --endpoints=$CLUSTER \
	  --ca-file=/etc/kubernetes/pki/etcd-ca.crt \
	  --cert-file=/etc/kubernetes/pki/etcd.crt \
	  --key-file=/etc/kubernetes/pki/etcd.key \
	  mk /kube-centos/network/config "{ \"Network\": \"$V_NET/16\", \"SubnetLen\": 24, \"Backend\": { \"Type\": \"host-gw\" } }" 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log

}


[ ! -f "/usr/lib/systemd/system/etcd.service" ] && download_resource || echo "resource already exist"
# double check
[  -f "/usr/bin/kube-apiserver" ] && echo "resource  exist" || download_resource
install_etcd




