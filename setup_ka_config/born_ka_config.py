# -*- coding:utf-8 -*-
import copy
import os
import random
import shutil

import init_config
from setup_ka_config import schedule_vip
from para_logger import TNLog

logger = TNLog()
class born_ka_config():
    def __init__(self):
        with open("setup_ka_config/common_txt", "r") as f:
            config_content = f.readlines()
        self.config_content = config_content
        self.init_config = init_config.init_config

    def reorg_config(self):
        config_important_var = schedule_vip.schedule_vip()
        ka_config_files = "temp_ka_config_files/"

        del_dirs = os.listdir(ka_config_files)
        for each_dir in del_dirs:
            try:
                shutil.rmtree("%s%s" %(ka_config_files, each_dir))
            except Exception as e:
                logger.error(e)

        for each_server_config in config_important_var.keys():
            os.mkdir("%s%s" %(ka_config_files, each_server_config))

        for each_server_config in config_important_var.keys():
            instance_num = random.randint(150, 250)
            for each_server_config_file in config_important_var.keys():
                old_ka_config = copy.deepcopy(self.config_content)
                try:
                    new_instance_name = "VI_" + str(instance_num)
                    old_instance_name = old_ka_config[0]
                    final_instance_name = old_instance_name.replace("VI_1", new_instance_name)
                    old_ka_config[0] = final_instance_name

                    old_interface = old_ka_config[2]
                    final_interface = old_interface.replace("bond4-1", self.init_config.get("servers").get(each_server_config_file)["device"])
                    old_ka_config[2] = final_interface

                    old_router_id = old_ka_config[3]
                    final_router_id = old_router_id.replace("201", str(instance_num))
                    old_ka_config[3] = final_router_id

                    if each_server_config_file == each_server_config:
                        old_priority = old_ka_config[4]
                        final_priority = old_priority.replace("100", str(instance_num))
                        old_ka_config[4] = final_priority
                    else:
                        old_priority = old_ka_config[4]
                        final_priority = old_priority.replace("100",
                                                              str(instance_num - list(config_important_var.keys()).index(each_server_config_file)*10-10))
                        old_ka_config[4] = final_priority

                    old_src_ip = old_ka_config[6]
                    final_src_ip = old_src_ip.replace("10.127.11.201", each_server_config_file)
                    old_ka_config[6] = final_src_ip

                    new_peer_ip = list(config_important_var.keys())
                    new_peer_ip.remove(each_server_config_file)
                    for each_peer_ip in new_peer_ip:
                        old_ka_config.insert(8, '        %s\n' %each_peer_ip)

                    new_virtual_ip = config_important_var[each_server_config]["vip"]
                    for each_virtual_ip in new_virtual_ip:
                    #     if new_virtual_ip.index(each_virtual_ip) != 0:
                        old_ka_config.insert(-2, "        %s\n" %each_virtual_ip)
                    file_path = "%s%s/%s" %(ka_config_files, each_server_config, each_server_config_file)
                    with open(file_path, "w") as f:
                        f.writelines(old_ka_config)
                except Exception as e:
                    logger.error(e)
