#!/bin/bash
mkdir /var/log/install_worker 2>&- 1>&-
INTERNAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=`hostname`
VIP=$1
etcd_node=$2
CLUSTER_DNS=$3
CLUS_DOMAIN=$4
etcd_prefix=$5
INS_REG=artifact.paas.yp
location=$(hostname -I | awk '{print $1}'|awk -F'.' '{print$1"."$2}')
mkdir -p /etc/kubernetes/{pki,manifests} 2>&- 1>&-&&mkdir -p /var/log/k8s/{kubelet,kube-proxy} 2>&- 1>&-&&mkdir -p /var/lib/{kubelet,kube-proxy} 2>&- 1>&-
swapoff -a 2>&- 1>&-
/usr/bin/bash /etc/sysconfig/modules/ipvs.modules 2>&- 1>&-
date >> /var/log/install_worker/worker.log
cd /tmp
curl -O "https://heye-media.bj.bcebos.com/media/docker-ce-18.09.9-3.el7.x86_64.rpm" 2>&- 1>&-&&
curl -O "https://heye-media.bj.bcebos.com/media/docker-ce-cli-18.09.9-3.el7.x86_64.rpm" 2>&- 1>&-&&
rpm -ivh docker-ce-18.09.9 -y 2>/var/log/install_worker/worker.log 1>/var/log/install_worker/worker.log
rpm -ivh docker-ce-cli-18.09.9 -y 2>/var/log/install_worker/worker.log 1>/var/log/install_worker/worker.log
systemctl start docker 2>/var/log/install_worker/worker.log 1>/var/log/install_worker/worker.log
echo "Docker has been installed"
cd /tmp  2>&- 1>&-
#curl -O "http://artifact.paas.yp:8000/artifactory/sys-k8s-package-local/worker_node.tar" 2>&- 1>&-&&tar -xf worker_node.tar 2>&- 1>&-
curl -O "https://heye-media.bj.bcebos.com/media/k8s1.14.7-node.tar" 2>&- 1>&-&&tar -xf k8s1.14.7-node.tar 2>&- 1>&-
echo "Download binary files"
#cd worker_node  2>&- 1>&-
#/usr/bin/cp -rf  /usr/bin 2>&- 1>&-
for i in flanneld kubelet  kube-proxy;do
    systemctl stop $i
    unalias cp
    scp -r $i /usr/bin/
    systemctl start $i
done
[ ! -d "/etc/kubernetes" ] && mkdir /etc/kubernetes 2>&- 1>&-
cd /etc/kubernetes  2>&- 1>&-
cd /tmp  2>&- 1>&-
[ ! -f "worker_service.tar" ] && curl -O "https://heye-media.bj.bcebos.com/media/worker_service.tar" 2>&- 1>&-&& tar -xf worker_service.tar 2>&- 1>&-
echo "Download service files"
cd worker_service  2>&- 1>&-
/usr/bin/cp -rf * /usr/lib/systemd/system 2>&- 1>&-
sed -i 's/memory=2Gi/memory=1Gi/g' /usr/lib/systemd/system/kubelet.service
sed -i 's/memory=8Gi/memory=1Gi/g' /usr/lib/systemd/system/kubelet.service
cd /usr/lib/systemd/system  2>&- 1>&-
[ ! -f /etcd/kubernetes/flanneld ] && /usr/bin/cp -rf flanneld /etc/kubernetes/ 2>&- 1>&-
rm -f flanneld 2>&- 1>&-
cd /usr/lib/systemd/system
sed -i 's|-etcd-endpoints=???|-etcd-endpoints='$etcd_node'|g' /etc/kubernetes/flanneld
sed -i 's|etcd-prefix=???|etcd-prefix='$etcd_prefix'|g' /etc/kubernetes/flanneld
systemctl daemon-reload 2>&- 1>&-i
systemctl enable flanneld 2>&- 1>&-
systemctl start flanneld 2>&- 1>&-
systemctl status flanneld 2>&- 1>&-
if [[ $? -ne 0 ]];then
    date >> /var/log/install_worker/worker.log
    echo "flanneld installed error" >> /var/log/install_worker/worker.log
    echo "flanneld installed error"
    exit 1
fi
echo "flanneld has been installed"
sed -i 's|insecure-registry=???|insecure-registry='$INS_REG'|' docker.service
systemctl daemon-reload 2>&- 1>&-
systemctl enable docker 2>&- 1>&-
systemctl restart docker 2>&- 1>&-
systemctl status docker 2>&- 1>&-
if [[ $? -ne 0 ]];then
    date >> /var/log/install_worker/worker.log
    echo "Docker installed error" >> /var/log/install_worker/worker.log
    echo "Docker installed error"
    exit 1
fi
echo "Docker has been started"
IP_TAG=`echo $INTERNAL_IP|awk -F'.' '{print $1"."$2}'`
if [[ $IP_TAG == 10.127 ]];then
    sed -i 's|address=???|address='$INTERNAL_IP'|;s|hostname-override=???|hostname-override='$HOSTNAME'|;s|node-ip=???|node-ip='$INTERNAL_IP'|' kubelet.service
else
    sed -i 's|address=???|address='$INTERNAL_IP'|;s|hostname-override=???|hostname-override='$INTERNAL_IP'|;s|node-ip=???|node-ip='$INTERNAL_IP'|' kubelet.service
fi
sed -i 's|cluster-dns=???|cluster-dns='$CLUSTER_DNS'|;s|cluster-domain=???|cluster-domain='$CLUS_DOMAIN'|' kubelet.service

cat kubelet.service |grep image |awk -F= '{print $2}' |awk -F'\' '{print $1}' |xargs docker pull
[ $? -ne 0 ] && (echo "pull image failed"; exit 1)
systemctl daemon-reload 2>&- 1>&-
systemctl enable kubelet 2>&- 1>&-
systemctl start kubelet 2>&- 1>&-
systemctl status kubelet 2>&- 1>&-
if [[ $? -ne 0 ]];then
    date >> /var/log/install_worker/worker.log
    echo "Kubelet installed error" >> /var/log/install_worker/worker.log
    echo "Kubelet installed error"
    exit 1
fi
echo "kubelet has been installed"
cat > /etc/logrotate.d/kubelet.log << EOF
/var/log/k8s/kubelet/kubelet.log {
    daily
    rotate 7
    dateext
    missingok
    copytruncate
}
EOF
echo "kubelet log add to logrotated success"
sed -i 's/bind-address=???/bind-address='$INTERNAL_IP'/;s/hostname-override=???/hostname-override='$HOSTNAME'/' kube-proxy.service


function create_kubeproxy_kubeconfig() {

    KUBERNETES_PUBLIC_ADDRESS=$1

    CLUSTER_NAME="default"
    KCONFIG=kube-proxy.kubeconfig
    KUSER="system:kube-proxy"
    KCERT=kube-proxy

    cd /etc/kubernetes/

    kubectl config set-cluster ${CLUSTER_NAME} \
      --certificate-authority=pki/ca.crt \
      --embed-certs=true \
      --server=https://${KUBERNETES_PUBLIC_ADDRESS}:6443 \
      --kubeconfig=${KCONFIG}

    kubectl config set-credentials ${KUSER} \
      --client-certificate=pki/${KCERT}.crt \
      --client-key=pki/${KCERT}.key \
      --embed-certs=true \
      --kubeconfig=${KCONFIG}

    kubectl config set-context ${KUSER}@${CLUSTER_NAME} \
      --cluster=${CLUSTER_NAME} \
      --user=${KUSER} \
      --kubeconfig=${KCONFIG}

    kubectl config use-context ${KUSER}@${CLUSTER_NAME} --kubeconfig=${KCONFIG}
    kubectl config view --kubeconfig=${KCONFIG}
    echo "kube-proxy.kubeconfig created"


}

create_kubeproxy_kubeconfig  $VIP


systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-proxy 2>&- 1>&-
systemctl start kube-proxy 2>&- 1>&-
systemctl status kube-proxy 2>&- 1>&-
if [[ $? -ne 0 ]];then
    date >> /var/log/install_worker/worker.log
    echo "Kube-proxy installed error" >> /var/log/install_worker/worker.log
    echo "Kube-proxy installed error"
    exit 1
fi
echo "kube-proxy has been installed"
cat > /etc/logrotate.d/kube-proxy.log << EOF
/var/log/k8s/kube-proxy/kube-proxy.log {
    daily
    rotate 7
    dateext
    missingok
    copytruncate
}
EOF
echo "kube-proxy log add to logrotated success"
#systemctl start ycelet.service 2>&- 1>&-
#systemctl enable ycelet.service 2>&- 1>&-
mkdir /dns-kubeconfig
/usr/bin/cp -rf /etc/kubernetes/admin.kubeconfig /dns-kubeconfig
echo "Worker node has been installed successfully"

