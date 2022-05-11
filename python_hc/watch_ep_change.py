from kubernetes import client, config, watch
import ops_upstream
from archive_logger import TNLog

config.load_kube_config(config_file="/workdir/kubeconfig/kubeconfig.yaml")
api_instance = client.CoreV1Api()
lb_ns = 'lwl-test'
logger = TNLog()

def watch_ep_status():
    w_ep = watch.Watch()
    subset_set = set()
    watch_ep_change_type = ('MODIFIED', 'ADDED', 'DELETED')
    # init_signal = 0
    while True:
        try:
            for event_ep in w_ep.stream(api_instance.list_namespaced_endpoints, namespace=lb_ns, _request_timeout=0):
                logger.info(event_ep['object'])
                # if init_signal == 0:
                #     init_signal = 1
                #     continue
                if event_ep['object'].subsets is None:
                    continue
                logger.info(subset_set)
                subset_set = set()
                for each_subset in event_ep['object'].subsets:
                    logger.info(each_subset)
                    if each_subset.addresses is None:
                        subset_set.add(each_subset.not_ready_addresses[0].ip + ":" + str(each_subset.ports[0].port))
                    else:
                        subset_set.add(each_subset.addresses[0].ip + ":" + str(each_subset.ports[0].port))
                logger.info(subset_set)
                if event_ep['type'] in watch_ep_change_type:
                    logger.info(event_ep['type'])
                    is_annotation = event_ep['object'].metadata.annotations.get('healthCheckType',None)
                    logger.info(is_annotation)
                    if is_annotation is None:
                        healthCheck_type = 'http'
                    else:
                        healthCheck_type = is_annotation
                    ep_content = (event_ep['object'].metadata.name, event_ep['type'], subset_set, healthCheck_type)
                    logger.info(ep_content)
                    is_calledsource = event_ep['object'].metadata.annotations.get('calledSource','kubectl-client-side-apply')
                    logger.info(is_calledsource)
                    if event_ep['type'] == 'MODIFIED' and is_calledsource == 'python-client':
                        logger.info('this action was started by python-client, no ngx action was done')
                        continue
                    else:
                        ops_upstream.ops_nginx_upstream(ep_content)
                subset_set = set()
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    watch_ep_status()