import add_ep_health_check
from time import sleep
from ops_etcd import set_etcd_down_ep
import ops_k8s_ep
import watch_ep_change
from archive_logger import TNLog

logger = TNLog()
if __name__ == '__main__':
    set_etcd_down_ep_instance = set_etcd_down_ep()
    init_signal = 0
    while True:
        old_ngx_ep_status = eval(set_etcd_down_ep_instance.read_etcd_down_ep())
        new_ngx_ep_status = add_ep_health_check.get_init_ep_status()
        try:
            for each_old_ngx_ep_status_k, each_old_ngx_ep_status_v in old_ngx_ep_status.items():
                ep_upstream = new_ngx_ep_status.get(each_old_ngx_ep_status_k, None)
                if ep_upstream is not None and (each_old_ngx_ep_status_v in ep_upstream):
                    continue
                if ep_upstream is not None and (each_old_ngx_ep_status_v not in ep_upstream):
                    for each_ep in each_old_ngx_ep_status_v:
                        if each_ep not in ep_upstream:
                            if init_signal == 0:
                                old_ngx_ep_status[each_old_ngx_ep_status_k].remove(each_ep)
                            #restore
                            else:
                                print 'restore', each_old_ngx_ep_status_k, each_ep
                                if ops_k8s_ep.ops_eps('enable',each_old_ngx_ep_status_k,each_ep,watch_ep_change.lb_ns) == 200:
                                    old_ngx_ep_status[each_old_ngx_ep_status_k].remove(each_ep)
                                else:
                                    logger.info('failed to remove down servers from list')
                else:
                    if init_signal == 0:
                        old_ngx_ep_status.pop(each_old_ngx_ep_status_k)
                    else:
                        #restore
                        print 'restore', each_old_ngx_ep_status_k
                        if ops_k8s_ep.ops_eps('enable', each_old_ngx_ep_status_k, 'all', watch_ep_change.lb_ns) == 200:
                            old_ngx_ep_status.pop(each_old_ngx_ep_status_k)
                        else:
                            logger.info('failed to remove down servers from list')
            logger.info(old_ngx_ep_status)
            set_etcd_down_ep_instance.write_etcd_down_ep(old_ngx_ep_status)
            sleep(1)
            init_signal = 1
        except Exception as e:
            logger.error(e)
