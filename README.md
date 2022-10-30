# HeYe(Parasaus)

HeYe(Parasaus) is a high-performance, high-scalability, ops-friendly loadbalancer.

HeYe(Parasaus) provides traffic forward features, which handle traditional north-south traffic, as well as east-west traffic in datacenter efficiently.

The technical architecture of HeYe(Parasaus):

<img width="978" alt="image" src="https://user-images.githubusercontent.com/104561610/198887824-a14f5d78-7bb1-4d7a-a33b-0e63125714d4.png">

Features
------------------------
1. The data plane and the control plane are separated in the architecture, a clean architecture is realized. The data plane is borrowed from kubernetes, and the control plane is implemented by ourselves, which is very lightweight.

2. The forward traffic nodes support horizontal scaling, and the computing power and bandwidth are close to infinity.

3. Traffic forwarding is implemented through LVS. As we all know, LVS is an implementation of Layer 4 load balancing inside the Linux kernel. Layer 4 load balancing works on OSI Layer 4 (Transport Layer) and distributes requests to the servers at the transport layer without looking at the content of the packets, so it has the best performance.

4. General x86 server was liked without any special configuration or hardware.

5. The configuration of addition, deletion, modification and query supports hot update, which has no impact on the business. These can be done through yaml and API, which is very simple and friendly

6. Supports 3 modes of health check on layer 7 HTTP headers, layer 4 tcp port and udp.

7. Supports multiple load balancing modes, such as RR, LC, WLC, WRR, source hash, etc.

Get Started
----------------------------

Prepare

  1. one managment server and N(minimal is 2) worker nodes

     recommended configuration: 

     * 8c, 32G mem, 100G disk
     
     * CentOS 7.9

     * turnoff swap on all worker nodes，supports passwordless login between management server and workers

Installation

  1. setup yum repo on all servers and nodes, it have to include all CentOS 7.9 packages and docker

  2. setup passwordless login between management server and workers on management server
     
     * ssh-copy-id worker_node_ip

     * ssh worker_node_ip date (verify it about passwordless login)
 
  3. install docker on managment server

     * yum install -y docker*

  4. docker pull image and docker run image

     * docker pull image

     * mkdir -p /workdir/stage/service&touch /workdir/stage/init_config.py&mkdir -p /workdir/stage/etcd/&touch /workdir/stage/etcd/default.etcd

     * docker run -v /workdir/stage/init_config.py:/workdir/devops/parasaus/init_config.py -v /workdir/stage/service:/workdir/devops/parasaus/service/ -v /workdir/stage/etcd/default.etcd:/default.etcd -p 2379:2379 -p 2380:2380 -it -d parasaus:v9 /bin/bash --restart=always

Getting started

  1. docker exec -it docker_id /bin/bash 
  
  2. vi /workdir/devops/parasaus/init_config.py and input critical info. for example:
  
  init_config = {
               "virtual_ip":["192.168.9.3", "192.168.9.9"],
               "etcd":{'ip':"10.13.5.16",'port':2379},
               "servers":{
                   "192.168.9.4":{
                       "device":"ens192",
                       "vip":[]
                   },
                   "192.168.9.5":{
                       "device":"ens192",
                        "vip":[]
                   }
               }
               }
  notice: option "vip" must be null
  
  3. input "paractl init cluster" and which return some successful messages

  4. 

ok, let's have a nice journey!
  
if you have any ideas or questions, please tell me(opendinosaurpark@gmail.com) or take a new issue. thanks
