#!/bin/bash
mkdir /var/log/install_master  2>&- 1>&-
systemctl stop flanneld 2>&- 1>&-
systemctl stop kube-scheduler.service 2>&- 1>&-
systemctl stop kube-controller-manager.service 2>&- 1>&-
systemctl stop kube-apiserver.service 2>&- 1>&-
systemctl stop etcd 2>&- 1>&-
#INTERNAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=`hostname`
IP1=$(hostname -I | awk '{print $1}')
IP2=$1
IP3=$2
HOSTNAME2=$3
HOSTNAME3=$4
IP4=$5
IP5=$6
IP6=$7
INTERNAL_IP=$IP4
CLUSTER=$8
ETCD_ENDPOINTS=$7
cluster_cidr=`echo $IP5|awk -F'.' '{print $1"."$2"."$3".0"}'`
V_NET=`echo $IP6|awk -F'.' '{print $1"."$2"."$3".0"}'`

function install_etcd() {
  # 本机
  cd /tmp/
  bash -x etcd_install.sh $IP1 $IP2 $IP3 $HOSTNAME $HOSTNAME2 $HOSTNAME3 $CLUSTER $V_NET

  # IP2
  scp etcd_install.sh $IP2:/tmp
  ssh $IP2 "bash /tmp/etcd_install.sh $IP2 $IP1 $IP3 $HOSTNAME2 $HOSTNAME $HOSTNAME3 $CLUSTER $V_NET > /dev/null 2>&1"

  # IP3
  scp etcd_install.sh $IP3:/tmp
  ssh $IP3 "bash /tmp/etcd_install.sh $IP3 $IP1 $IP2 $HOSTNAME3 $HOSTNAME $HOSTNAME2 $CLUSTER $V_NET > /dev/null 2>&1"

}

function install_kn() {
    # repo don not have nginx
    cd /tmp
    curl -O "https://heye-media.bj.bcebos.com/media/install_kn.sh" 2>&- 1>&- 
    wget http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.20.1-1.el7.ngx.x86_64.rpm
    sed -i '/yum install nginx/a\cd /tmp && yum -y localinstall nginx-1.20.1-1.el7.ngx.x86_64.rpm ' install_kn.sh
    sed -i '/yum install nginx/d' install_kn.sh
    bash install_kn.sh  $IP2 $IP3 $IP4 2>&- 1>&-
    sed -i 's/bond4-1/ens192/' /etc/keepalived/keepalived.conf
    sed -i 's/virtual_router_id 51/virtual_router_id 83/g' /etc/keepalived/keepalived.conf
    systemctl restart keepalived
}


function create_cert() {
    mkdir -p /etc/kubernetes/{pki,manifests} &&mkdir -p /var/log/k8s/{kubelet,kube-proxy} &&mkdir -p /var/lib/{kubelet,kube-proxy} 2>&- 1>&- 
    mkdir -p /var/log/k8s/kube-apiserver 2>&- 1>&-
    mkdir -p /var/log/k8s/kube-controller-manager 2>&- 1>&-
    mkdir -p /var/log/k8s/kube-scheduler 2>&- 1>&-
    cd /etc/kubernetes/pki 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    curl -O "https://heye-media.bj.bcebos.com/media/openssl.cnf"  2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    sed -i 's|?subjectAltName?|'$IP4'|g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS5?/'$IP1'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS6?/'$IP2'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS7?/'$IP3'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP1?/'$IP1'/g'  /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP2?/'$IP2'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP3?/'$IP3'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP4?/'$IP4'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP5?/'$IP5'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?IP6?/'$IP6'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS1?/'$IP1'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS2?/'$IP2'/g' /etc/kubernetes/pki/openssl.cnf 
    sed -i 's/?DNS3?/'$IP3'/g' /etc/kubernetes/pki/openssl.cnf 
    curl -O "https://heye-media.bj.bcebos.com/media/create_cert.sh" 2>&- 1>&-
    # solve kube-proxy problem
    sed -i 's/CN=kube-proxy/CN=system:kube-proxy/g' create_cert.sh
    bash create_cert.sh 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
}



function download_resource() {
    ## 拷贝二进制和service文件。缺少etcdctl, 需要比较提前执行
    mkdir -p /var/log/install_master/
    cd /tmp

    curl -O "https://heye-media.bj.bcebos.com/media/k8s1.14.7-master.tar"  2>&- 1>&-
    tar -xf k8s1.14.7-master.tar 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
   
    
    for i in flanneld etcd  etcdctl kube-apiserver kube-scheduler kube-controller-manager;do
        unalias slavecp
        cp -r $i /usr/bin/
    done

    cd /tmp
    curl -O "https://heye-media.bj.bcebos.com/media/master_service.tar" 2>&- 1>&- 
    tar -xf master_service.tar  2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    cd master_service 2>&- 1>&-
    /usr/bin/cp -rf flanneld /etc/kubernetes/ 2>&- 1>&- 
    /usr/bin/cp -rf * /usr/lib/systemd/system/ 2>&- 1>&-
}



function correct_service() {
    sed -i 's/?IP1?/'$IP1'/g' /usr/lib/systemd/system/kube-apiserver.service 2>&- 1>&-
    sed -i 's/?cluster_cidr?/'$cluster_cidr'/g' /usr/lib/systemd/system/kube-apiserver.service 2>&- 1>&-
    sed -i 's/?cluster_cidr?/'$cluster_cidr'/g' /usr/lib/systemd/system/kube-controller-manager.service 2>&- 1>&-
    sed -i 's/?V_NET?/'$V_NET'/g' /usr/lib/systemd/system/kube-controller-manager.service 2>&- 1>&-
    sed -i '/insecure-experimental-approve-all-kubelet-csrs-for-group/d' /usr/lib/systemd/system/kube-controller-manager.service 2>&- 1>&-

}


generate_etc_file() {
  cd /tmp
  curl -O "https://heye-media.bj.bcebos.com/media/service_account_kubeconfig.sh" 2>&- 1>&- 
  bash service_account_kubeconfig.sh $IP4 2>&- 1>&-
  curl -O "https://heye-media.bj.bcebos.com/media/kube-scheduler_kubeconfig.sh" 2>&- 1>&- 
  bash kube-scheduler_kubeconfig.sh $IP4 2>&- 1>&-
  curl -O "https://heye-media.bj.bcebos.com/media/admin_kubeconfig.sh" 2>&- 1>&- 
  bash admin_kubeconfig.sh $IP4 2>&- 1>&-


  TOKEN_PUB=$(openssl rand -hex 3)
  TOKEN_SECRET=$(openssl rand -hex 8)
  BOOTSTRAP_TOKEN="${TOKEN_PUB}.${TOKEN_SECRET}"
  echo $BOOTSTRAP_TOKEN > /etc/kubernetes/BOOTSTRAP_TOKEN
  kubectl -n kube-system create secret generic bootstrap-token-${TOKEN_PUB} \
          --type 'bootstrap.kubernetes.io/token' \
          --from-literal description="cluster bootstrap token" \
          --from-literal token-id=${TOKEN_PUB} \
          --from-literal token-secret=${TOKEN_SECRET} \
          --from-literal usage-bootstrap-authentication=true \
          --from-literal usage-bootstrap-signing=true 2>&- 1>&-

  KUBERNETES_PUBLIC_ADDRESS=$IP4
  CLUSTER_NAME="default"
  KCONFIG="bootstrap.kubeconfig"
  KUSER="kubelet-bootstrap"
  cd /etc/kubernetes
  kubectl config set-cluster ${CLUSTER_NAME} \
    --certificate-authority=pki/ca.crt \
    --embed-certs=true \
    --server=https://${KUBERNETES_PUBLIC_ADDRESS}:6443 \
    --kubeconfig=${KCONFIG} 2>&- 1>&-
  kubectl config set-context ${KUSER}@${CLUSTER_NAME} \
    --cluster=${CLUSTER_NAME} \
    --user=${KUSER} \
    --kubeconfig=${KCONFIG} 2>&- 1>&-
  kubectl config use-context ${KUSER}@${CLUSTER_NAME} --kubeconfig=${KCONFIG} 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
  sed -i 's/?IP1?/'$IP1'/g' /etc/kubernetes/flanneld 2>&- 1>&-
  sed -i 's/?IP2?/'$IP2'/g' /etc/kubernetes/flanneld 2>&- 1>&-
  sed -i 's/?IP3?/'$IP3'/g' /etc/kubernetes/flanneld 2>&- 1>&-
  BOOTSTRAP_TOKEN=`cat /etc/kubernetes/BOOTSTRAP_TOKEN`
  kubectl config set-credentials kubelet-bootstrap \
    --token=$BOOTSTRAP_TOKEN \
    --kubeconfig=/etc/kubernetes/bootstrap.kubeconfig 2>&- 1>&-

  echo "/etc/kubernetes configfile create done! please check...."
  sleep 20
}


copy_etc_file_to_peermaster() {
/usr/bin/scp -rp -o "StrictHostKeyChecking no" /etc/kubernetes/ root@$IP2:/etc 2>&- 1>&-
#/usr/bin/scp -rp -o "StrictHostKeyChecking no" /tmp/master_node.tar root@$IP2:/tmp 2>&- 1>&-
/usr/bin/scp -rp -o "StrictHostKeyChecking no" /etc/kubernetes/ root@$IP3:/etc 2>&- 1>&-
#/usr/bin/scp -rp -o "StrictHostKeyChecking no" /tmp/master_node.tar root@$IP3:/tmp 2>&- 1>&-
}



install_kn
create_cert
download_resource
correct_service
generate_etc_file
copy_etc_file_to_peermaster

echo "install etcd server, it may take several minutes..."
install_etcd
sleep 20

etcd_status=`systemctl status etcd |grep Active |grep running |wc -l`
[ $etcd_status -ne 0 ]  && echo "etcd running OK, continue installing......" || (echo "etcd install failed,exiting..."; exit 1)



systemctl daemon-reload 2>&- 1>&-
systemctl enable flanneld 2>&- 1>&-
systemctl start flanneld 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-apiserver 2>&- 1>&-
systemctl start kube-apiserver 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-controller-manager  2>&- 1>&-
systemctl start kube-controller-manager 2>&- 1>&-
systemctl daemon-reload 2>&- 1>&-
systemctl enable kube-scheduler 2>&- 1>&-
systemctl start kube-scheduler 2>&- 1>&-

scp /tmp/master_node_slave.sh $IP2:/tmp/
ssh $IP2 "cd /tmp && bash -x master_node_slave.sh $IP1 $IP3 $HOSTNAME $HOSTNAME3 $IP4 $IP5 $IP6" 2>&- 1>&-
scp /tmp/master_node_slave.sh $IP3:/tmp/
ssh $IP3 "cd /tmp && bash -x master_node_slave.sh $IP1 $IP2 $HOSTNAME $HOSTNAME2 $IP4 $IP5 $IP6" 2>&- 1>&-
systemctl stop flanneld 2>&- 1>&-
systemctl stop kube-scheduler.service 2>&- 1>&-
systemctl stop kube-controller-manager.service 2>&- 1>&-
systemctl stop kube-apiserver.service  2>&- 1>&-
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




generate_bootstrap_secret() {
  cd /etc/kubernetes
  TOKEN_PUB=`cat BOOTSTRAP_TOKEN |awk -F'.' '{print $1}'`
  TOKEN_SECRET=`cat BOOTSTRAP_TOKEN |awk -F'.' '{print $2}'`
  kubectl -n kube-system create secret generic bootstrap-token-${TOKEN_PUB} \
          --type 'bootstrap.kubernetes.io/token' \
          --from-literal description="cluster bootstrap token" \
          --from-literal token-id=${TOKEN_PUB} \
          --from-literal token-secret=${TOKEN_SECRET} \
          --from-literal usage-bootstrap-authentication=true \
          --from-literal usage-bootstrap-signing=true 2>&- 1>&-
  [ $? -eq 0 ] && echo "BOOTSTRAP secert created success." || echo "BOOTSTRAP secert created fail......"
}

generate_bootstrap_secret




kubectl -n kube-public create configmap cluster-info \
        --from-file /etc/kubernetes/pki/ca.crt \
        --from-file /etc/kubernetes/bootstrap.kubeconfig 2>&- 1>&-
kubectl -n kube-public create role system:bootstrap-signer-clusterinfo \
        --verb get --resource configmaps 2>&- 1>&-
kubectl -n kube-public create rolebinding kubeadm:bootstrap-signer-clusterinfo \
        --role system:bootstrap-signer-clusterinfo --user system:anonymous 2>&- 1>&-
kubectl create clusterrolebinding kubeadm:kubelet-bootstrap \
        --clusterrole system:node-bootstrapper --group system:bootstrappers 2>&- 1>&-
systemctl status etcd 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "etcd installed error" >>/var/log/install_master/install_master.log
    systemctl status etcd 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "etcd installed error"
    exit 1
fi
systemctl status kube-apiserver 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-apiserver installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-apiserver 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-apiserver installed error"
    exit 1
fi
systemctl status kube-controller-manager  2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-controller installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-controller-manager 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-controller installed error"
    exit 1
fi
systemctl status kube-scheduler 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "kube-scheduler installed error" >> /var/log/install_master/install_master.log
    systemctl status kube-scheduler 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "kube-scheduler installed error"
    exit 1
fi
systemctl status flanneld 2>&- 1>&-
if [[ $? -ne 0 ]];then
    echo "flanneld installed error" >> /var/log/install_master/install_master.log
    systemctl status flanneld 2>>/var/log/install_master/install_master.log 1>>/var/log/install_master/install_master.log
    echo "flanneld installed error"
    exit 1
fi
echo "Master has been installed"
