# HeYeLB(Distributed Loadbalancer)

HeYe is a high-performance, high scalable, ops-friendly, kubernetes-native loadbalancer.

HeYe provides traffic forward features, which handle traditional north-south traffic, as well as east-west traffic in datacenter and supports three health check types.

The technical architecture of HeYe LB:

![image](https://user-images.githubusercontent.com/104561610/167753755-4b40ea7d-1c8f-4d2d-b2ec-bb1436025e93.png)

Features
------------------------
1. The maximum number of forward traffic nodes is 254, and the computing power and bandwidth are close to infinity.

2. The architecture borrows kubernetes and refers to the principle of SVC and endpoint forwarding in kubernetes. modify/add/delete/query management based on yaml file or interface, which is simple and friendly to operate.

3. Support 3 types of healthcheck on layer 7 HTTP headers, layer 4 ports and mysql service.

4. General x86 server was liked without any special configuration or hardware.

5. The configuration of addition, deletion, modification and query supports hot update, which has no impact on the business.


Get Started
----------------------------
Prepare

  1. core switch supports network quality feature, such as cisco sla, h3c nqa

  2. 3 servers， minimal configuration(Strongly recommended): 

     * 8c 32G 100 disk

     * turnoff swap on all nodes，supports passwordless login beetween nodes

Installation

  0. equivalent routing is configured on the switch and all traffic which forwards svc_cidr goes through three nodes

  1. login node1
 
  2. cd *your_path*/heyelb/install_cli

  3. sh master_node.sh <node2_ip> <node3_ip> <node2_hostname> <node3_hostname> <vip> <svc_ip_cidr> <pod_ip_cidr> <etcd_endpoints>
  
     for example: sh master_node.sh 10.1.1.2 10.1.1.3 k8s02 k8s03 10.1.1.4 10.11.0.0 10.12.0.0   "https://10.1.1.92:2379,https://10.1.1.93:2379,https://10.1.1.150:2379"
  
  4. sh worker_node.sh <vip> <etcd_endpoints> <svc_ip_DNS>  "cluster.local." "/kube-centos/network"
  
  5. docker pull heyelb:v6
  
  6. choose anyone node and run heyelb:
  
     * mkdir -p /workdir/servers/ && mkdir -p /workdir/etcd/ && mkdir -p /workdir/kubeconfig/ 
  
     * cd /workdir/servers/ && touch upstream.conf 
  
     * cp *your_path*/admin.kubeconfig /workdir/kubeconfig/ && cd /workdir/kubeconfig/ && mv admin.kubeconfig kubeconfig.yaml
  
     * docker run -v /workdir/servers/:/export/home/yeepine-1.0/conf/servers/ -v /workdir/etcd:/default.etcd -v /workdir/kubeconfig:/workdir/kubeconfig -d heyelb:v6 /bin/bash

Getting started

  1. edit a yaml file, Service.spec.ports.name and Endpoints.subnets.addresses.ports.name must be the sanme, Endpoints.metadata.annotations.calledSource and Endpoints.metadata.annotations.calledSource.healthCheckType are required. 
  
  2. Endpoints.metadata.annotations.calledSource.healthCheckType have 3 types, which supports only http, tcp and mysql.

ok, let us have a nice journey!
  
if you have any ideas or questions, please tell me(422287032@qq.com) or take a new issue. thanks
