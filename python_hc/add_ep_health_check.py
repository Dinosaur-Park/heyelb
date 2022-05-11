import json, requests, datetime
from time import sleep
import etcd
from ops_etcd import set_etcd_down_ep
import watch_ep_change, ops_k8s_ep
from archive_logger import TNLog

logger = TNLog()
def get_ngx_down_dic():
    ngx_status_down = requests.get('http://127.0.0.1/nginx_status?format=json&status=down',headers={'Cache-Control':'no-cache'}).content
    if ngx_status_down[-9] == ',':
        ngx_status_down_content = ngx_status_down[:-9] + '' + ngx_status_down[-8:]
    else:
        ngx_status_down_content = ngx_status_down
    ngx_status_down_content = json.loads(ngx_status_down_content)
    return ngx_status_down_content

def get_init_ep_status():
    ngx_hc_down_dict = {}
    ngx_status_down_dic = get_ngx_down_dic()
    for each_ngx_status_down_ep in ngx_status_down_dic['servers']['server']:
        # print each_ngx_status_down_ep
        if ngx_hc_down_dict.get(each_ngx_status_down_ep['upstream'], None) is None:
            ngx_hc_down_dict[each_ngx_status_down_ep['upstream']] = [each_ngx_status_down_ep['name']]
        else:
            ngx_hc_down_dict[each_ngx_status_down_ep['upstream']].append(each_ngx_status_down_ep['name'])
    return ngx_hc_down_dict

if __name__ == "__main__":
    set_etcd_down_ep_instance = set_etcd_down_ep()
    init_signal = 0
    while True:
        next_ngx_down_dic = get_ngx_down_dic()
        ngx_ep_status = set_etcd_down_ep_instance.read_etcd_down_ep()
        if ngx_ep_status is None:
            ngx_ep_status = get_init_ep_status()
        else:
            ngx_ep_status = eval(ngx_ep_status)
        try:
            for each_upstream_name_server in next_ngx_down_dic['servers']['server']:
                ep_upstream = ngx_ep_status.get(each_upstream_name_server['upstream'], None)
                ep_name = each_upstream_name_server['name']
                if ep_upstream is not None and (ep_name in ep_upstream):
                    continue
                if ep_upstream is not None and (ep_name not in ep_upstream):
                    if init_signal == 0:
                        #append new ep
                        ngx_ep_status.get(each_upstream_name_server['upstream'], None).append(ep_name)
                    else:
                        #disbale ep,
                        print 'disable', each_upstream_name_server['upstream'], ep_name
                        if ops_k8s_ep.ops_eps('disable',each_upstream_name_server['upstream'],ep_name,watch_ep_change.lb_ns) == 200:
                            ngx_ep_status.get(each_upstream_name_server['upstream'], None).append(ep_name)
                        else:
                            logger.info('failed to add down servers into list')
                if ep_upstream is None:
                    if init_signal == 0:
                        #append new upstream
                        ngx_ep_status[each_upstream_name_server['upstream']] = [ep_name]
                    else:
                        # disable ep in k8s
                        print 'disable', each_upstream_name_server['upstream'], ep_name
                        if ops_k8s_ep.ops_eps('disable',each_upstream_name_server['upstream'],ep_name,watch_ep_change.lb_ns) == 200:
                            ngx_ep_status[each_upstream_name_server['upstream']] = [ep_name]
                        else:
                            logger.info('failed to add down servers into list')
            logger.info(ngx_ep_status)
            set_etcd_down_ep_instance.write_etcd_down_ep(ngx_ep_status)
            sleep(1)
            init_signal = 1
        except Exception as e:
            logger.error(e)




