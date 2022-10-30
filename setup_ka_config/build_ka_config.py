# -*- coding:utf-8 -*-
import os
import shutil

from setup_ka_config import schedule_vip
from setup_ka_config.born_ka_config import born_ka_config
from para_logger import TNLog

logger = TNLog()
class build_ka_config():
    def __init__(self):
        with open("new_ka_config_files/general_content", "r") as f:
            general_content = f.readlines()
        self.general_content = general_content
        born_ka_config().reorg_config()

    def assemble_config(self):
        config_important_var = schedule_vip.schedule_vip()
        new_ka_config_files = "new_ka_config_files/"
        temp_ka_config_files = "temp_ka_config_files/"
        file_name = "keepalived.conf"
        del_dirs = os.listdir(new_ka_config_files)
        for each_dir in del_dirs:
            try:
                shutil.rmtree("%s%s" % (new_ka_config_files, each_dir))
            except Exception as e:
                logger.error(e)

        for each_server_config in config_important_var.keys():
            os.mkdir("%s%s" %(new_ka_config_files, each_server_config))

        for each_server_config in config_important_var.keys():
            server_config = []
            for each_server_config_content in os.listdir("temp_ka_config_files"):
                read_full_path = "%s%s/%s" %(temp_ka_config_files, each_server_config_content, each_server_config)
                with open(read_full_path, "r" ) as f:
                    part_server_config = f.readlines()
                server_config = server_config + part_server_config
            write_full_path = "%s%s/%s" %(new_ka_config_files, each_server_config, file_name)
            with open(write_full_path, "w") as f:
                f.writelines(self.general_content + server_config)
            logger.info(server_config)
