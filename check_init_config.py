# -*- coding:utf-8 -*-
import init_config
from para_logger import TNLog

logger = TNLog()
def check_format():
    init_config_json = init_config.init_config
    vip_list = []
    host_list = []
    try:
        if len(init_config_json.get("virtual_ip")) != len(set(init_config_json.get("virtual_ip"))):
            return {"error_msg": "duplicate virtual ip.", "code": 400}
        if not 10 > len(init_config_json.get("servers")) > 1:
            return {"error_msg": "number of nodes are wrong.", "code": 400}

        for each_vip in init_config_json.get("virtual_ip"):
            vip_list.append(each_vip[0:each_vip.rfind('.')])
        for each_server in init_config_json.get("servers").keys():
            if each_server in init_config_json.get("virtual_ip"):
                return {"error_msg": "duplicate ip between host ip and vip.", "code": 400}
            host_list.append(each_server[0:each_server.rfind('.')])
        if len(set(vip_list)) != 1:
            logger.info("vip is not in the same subnet.")
            return {"error_msg": "vip is not in the same subnet.", "code": 400}
        if len(set(host_list)) != 1:
            logger.info("hosts are not in the same subnet.")
            return {"error_msg": "hosts are not in the same subnet.", "code": 400}
        if set(vip_list) != set(host_list):
            logger.info("vip is different from host.")
            return {"error_msg": "vip is different from host.", "code": 400}

        return {"code": 200}
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    check_format()
