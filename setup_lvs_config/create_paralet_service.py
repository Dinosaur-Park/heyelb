from para_logger import TNLog
import init_config, os

logger = TNLog()
def create_paralet():
    etcd_ip = init_config.init_config['etcd']['ip']
    etcd_port = init_config.init_config['etcd']['port']
    with open('dist/paralet.example', 'r') as f:
        f_paralet_content = f.read()
    with open('dist/paralet.service', 'w') as f:
        f.write(f_paralet_content.replace('192.168.37.2:2379', '%s:%d' %(etcd_ip, etcd_port)))
