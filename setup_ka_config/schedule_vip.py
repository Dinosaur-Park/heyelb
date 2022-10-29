# -*- coding:utf-8 -*-
import init_config
from para_logger import TNLog

logger = TNLog()
def schedule_vip():
    vip_list = init_config.init_config["virtual_ip"]
    servers_dic = init_config.init_config["servers"]
    server_bound_vip = list(servers_dic.keys())

    circle_num = 0
    try:
        for vip_num in range(0, len(vip_list)):
            servers_dic[server_bound_vip[vip_num - len(server_bound_vip) * circle_num]]["vip"].append(vip_list[vip_num])
            if (vip_num + 1) % len(server_bound_vip) == 0:
                circle_num = circle_num + 1
        logger.info(servers_dic)
        return servers_dic
    except Exception as e:
        logger.error(e)
