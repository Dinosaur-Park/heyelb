# HeYeLB(Distributed Loadbalancer)

HeYe is a high-performance, high scalable, ops-friendly, kubernetes-native loadbalancer.

HeYe provides traffic forward features, which handle traditional north-south traffic, as well as east-west traffic in datacenter and supports three health check types.

The technical architecture of HeYe LB:

![image](https://user-images.githubusercontent.com/104561610/167753755-4b40ea7d-1c8f-4d2d-b2ec-bb1436025e93.png)

Features
------------------------
1.The maximum number of forward traffic nodes is 254, and the computing power and bandwidth are close to infinity.

2.The architecture borrows kubernetes and refers to the principle of SVC and endpoint forwarding in kubernetes. modify/add/delete/query management based on yaml file or interface, which is simple and friendly to operate.

3.Support 3 types of healthcheck on layer 7 HTTP headers, layer 4 ports and mysql service.

4.General x86 server was liked without any special configuration or hardware.

5.The configuration of addition, deletion, modification and query supports hot update, which has no impact on the business.


Get Started
----------------------------
Prepare

3 servers， minimal configuration，8c 32G 100 disk

turnoff swap，supports passwordless login

Installation

?

Getting started

?
