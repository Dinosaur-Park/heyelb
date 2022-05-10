# HeYeLB(Distributed Loadbalancer)

HeYe is a kubernetes-native, high-performance loadbalancer.

HeYe provides traffic forward features, which handle traditional north-south traffic, as well as east-west traffic in datacenter and supports three health check type.

The technical architecture of HeYe LB:

<img width="1091" alt="image" src="https://user-images.githubusercontent.com/104561610/167608059-4a7b7e48-3287-4fcd-a6bc-a4df259d4b20.png">

It is a distributed load balancer, and the traffic can be evenly crossed on each node. The maximum number of nodes is 254, and the computing power and bandwidth are close to infinity. The architecture borrows kubernetes and refers to the principle of SVC and endpoint forwarding in kubernetes. Use circle_check module checks the effectiveness of the endpoint. Support traffic forwarding on layer 7 HTTP headers and layer 4 ports. General x86 server was liked without any special configuration or hardware. The configuration of addition, deletion, modification and query supports hot loading, which has no impact on the business. It can be managed based on yaml file or interface, which is simple and easy to operate.



Features
------------------------
1.The maximum number of forward traffic nodes is 254, and the computing power and bandwidth are close to infinity.

2.The architecture borrows kubernetes and refers to the principle of SVC and endpoint forwarding in kubernetes. CRUD management based on yaml file or interface, which is simple and easy to operate.

3.Support health check on layer 7 HTTP headers, layer 4 ports and mysql service.

4.General x86 server was liked without any special configuration or hardware.

5.The configuration of addition, deletion, modification and query supports hot loading, which has no impact on the business.

Get Started
----------------------------
Installation

Please refer to install documentation.

Getting started

The getting started guide is a great way to learn the basics of APISIX. Just follow the steps in Getting Started.

Further, you can follow the documentation to try more plugins.
