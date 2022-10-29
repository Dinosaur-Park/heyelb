import sys, os
from setup_lvs_config import watch_svc_change as wsc
from setup_lvs_config import ipvs_snat
import para_logger

logger = para_logger.TNLog()
def paralet():
    try:
        # os.system('mkdir -p %s' % para_logger.dir)
        if len(sys.argv) != 2 or sys.argv[1] == '-h':
            print('paralet: the next distribute loadbalancer')
            print(' -h')
            print('\t The help message of paralet.')
            print(' --etcd-servers strings')
            print('\t List of etcd servers to connect with (http://ip:port).')

        elif sys.argv[1][:14] == '--etcd-servers':
            etcd_ip_port = sys.argv[1][22:]
            if ipvs_snat.set_ipvs_snat()['code'] == 200:
                wsc.watch_svc_change(etcd_ip_port.split(':')[0], int(etcd_ip_port.split(':')[1])).entry_change()
        else:
            logger.info('please input paralet -h to complete it.')

    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    paralet()