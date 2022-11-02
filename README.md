# HeYe(Parasaus)

HeYe(Parasaus) is a high-performance, high-scalability, ops-friendly loadbalancer.

HeYe(Parasaus) provides traffic forward features, which handle traditional north-south traffic, as well as east-west traffic in datacenter efficiently.

The technical architecture of HeYe(Parasaus):

<img width="978" alt="image" src="https://user-images.githubusercontent.com/104561610/198887824-a14f5d78-7bb1-4d7a-a33b-0e63125714d4.png">

Features
------------------------
1. The data plane and the control plane are separated in the architecture, a clean architecture is realized.

2. The forward traffic nodes support horizontal scaling, and the computing power and bandwidth are close to infinity.

3. Traffic forwarding is implemented through LVS. As we all know, LVS is implemented inside the Linux kernel. which works on OSI Layer 4 (Transport Layer) and forwards requests to the clients at the transport layer without looking at the content of the packets, so it has the best performance.

4. General x86 server was liked without any special configuration or hardware.

5. The configuration of addition, deletion, modification and query supports hot update, which has no impact on the business. These can be done through yaml and API, which is very simple and friendly

6. Supports 3 modes of health check on layer 7 HTTP headers, layer 4 tcp port and udp.

7. Supports multiple load balancing modes, such as RR, LC, WLC, WRR, source hash, etc.


Installation Guide
----------------------------
https://github.com/Dinosaur-Park/heyelb/wiki/Parasaus-Installation-Guide
