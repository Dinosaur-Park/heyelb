#!/bin/bash
mkdir /var/log/install_master 2>&- 1>&-
systemctl stop flanneld 2>&- 1>&-
systemctl stop kube-scheduler.service 2>&- 1>&-
systemctl stop kube-controller-manager.service 2>&- 1>&-
systemctl stop kube-apiserver.service 2>&- 1>&-
systemctl stop etcd 2>&- 1>&-
HOSTNAME=`hostname`
IP1=$(ip a |grep -E 'inet 10|inet 172|inet 192' |awk -F/ '{print $1}'|awk '{print $2}')
IP2=$1
IP3=$2
HOSTNAME2=$3
HOSTNAME3=$4
IP4=$5
IP5=$6
IP6=$7
INTERNAL_IP=IP4
CLUSTER=$8
ETCD_ENDPOINTS=$7
cluster_cidr=`echo $IP5|awk -F'.' '{print $1"."$2"."$3".0"}'`
V_NET=`echo $IP6|awk -F'.' '{print $1"."$2"."$3".0"}'`
# repo don not have nginx
cd /tmp
curl -O "https://heye-media.bj.bcebos.com/media/install_kn.sh" 2>&- 1>&- 
wget http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.20.1-1.el7.ngx.x86_64.rpm
sed -i '/yum install nginx/a\cd /tmp && yum -y localinstall nginx-1.20.1-1.el7.ngx.x86_64.rpm ' install_kn.sh
sed -i '/yum install nginx/d' install_kn.sh
bash install_kn.sh  $IP2 $IP3 $IP4 2>&- 1>&-
sed -i 's/bond4-1/ens192/' /etc/keepalived/keepalived.conf
sed -i 's/virtual_router_id 51/virtual_router_id 83/g' /etc/keepalived/keepalived.conf
[[ `hostname` =~ '02' ]] && sed -i 's/priority 100/priority 97/g' /etc/keepalived/keepalived.conf
[[ `hostname` =~ '03' ]] && sed -i 's/priority 100/priority 94/g' /etc/keepalived/keepalived.conf
systemctl restart keepalived


mkdir -p /var/log/k8s/{kubelet,kube-proxy} &&mkdir -p /var/lib/{kubelet,kube-proxy} 2>&- 1>&- 
mkdir -p /var/log/k8s/kube-apiserver 2>&- 1>&-
mkdir -p /var/log/k8s/kube-controller-manager 2>&- 1>&-
mkdir -p /var/log/k8s/kube-scheduler 2>&- 1>&-


sed -i 's/?IP1?/'$IP1'/g' /usr/lib/systemd/system/kube-apiserver.service 2>&- 1>&-
sed -i 's/?cluster_cidr?/'$cluster_cidr'/g' /usr/lib/systemd/system/kube-apiserver.service 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-apiserver 2>&- 1>&-
systemctl start kube-apiserver 2>&- 1>&-
systemctl status kube-apiserver 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-apiserver installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-apiserver 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-apiserver installed error"
#    exit 1
fi
sed -i 's/?cluster_cidr?/'$cluster_cidr'/g' /usr/lib/systemd/system/kube-controller-manager.service 2>&- 1>&-
sed -i 's/?V_NET?/'$V_NET'/g' /usr/lib/systemd/system/kube-controller-manager.service 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-controller-manager  2>&- 1>&-
systemctl start kube-controller-manager 2>&- 1>&-
systemctl status kube-controller-manager  2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-controller installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-controller-manager 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-controller installed error"
#    exit 1
fi
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-scheduler 2>&- 1>&-
systemctl start kube-scheduler 2>&- 1>&-
systemctl status kube-scheduler 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-scheduler installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-scheduler 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-scheduler installed error"
#    exit 1
fi

sed -i 's/?IP1?/'$IP1'/g' /etc/kubernetes/flanneld 2>&- 1>&-
sed -i 's/?IP2?/'$IP2'/g' /etc/kubernetes/flanneld 2>&- 1>&-
sed -i 's/?IP3?/'$IP3'/g' /etc/kubernetes/flanneld 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable flanneld 2>&- 1>&-
systemctl start flanneld 2>&- 1>&-
systemctl status flanneld 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "flanneld installed error" >> /var/log/install_master/install_master.log
    systemctl status flanneld 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "flanneld installed error"
#    exit 1
fi
systemctl stop flanneld 2>&- 1>&-
systemctl stop kube-scheduler.service 2>&- 1>&-
systemctl stop kube-controller-manager.service 2>&- 1>&-
systemctl stop kube-apiserver.service 2>&- 1>&-
systemctl stop etcd 2>&- 1>&-
systemctl enable etcd 2>&- 1>&-
systemctl start etcd 2>&- 1>&-
systemctl enable kube-apiserver.service 2>&- 1>&-
systemctl start kube-apiserver.service 2>&- 1>&-
systemctl enable kube-controller-manager.service 2>&- 1>&-
systemctl start kube-controller-manager.service 2>&- 1>&-
systemctl enable kube-scheduler.service 2>&- 1>&-
systemctl start kube-scheduler.service 2>&- 1>&-
systemctl enable flanneld 2>&- 1>&-
systemctl start flanneld 2>&- 1>&-
echo "Master has been installed"
