from kubernetes import client, config
from archive_logger import TNLog
import ops_upstream

logger = TNLog()
def ops_eps(*args):
    config.load_kube_config(config_file="/workdir/kubeconfig/kubeconfig.yaml")
    api_instance = client.CoreV1Api()
    ops_k8s_name = args[1]
    ops_k8s_ep = args[2]
    ops_k8s_ns = args[3]
    existed_ep_list = []
    #delete ep from kubectl-client
    for each_ep_name in api_instance.list_namespaced_endpoints(namespace=ops_k8s_ns).items:
        existed_ep_list.append(each_ep_name.metadata.name)
    if args[0] == 'enable' and ops_k8s_ep == 'all' and ops_k8s_name not in existed_ep_list:
        return 200

    try:
        spec_ns_eps = api_instance.read_namespaced_endpoints(name=ops_k8s_name,namespace=ops_k8s_ns)
        logger.info(spec_ns_eps)
    except Exception as e:
        logger.error(e)

    if args[0] == 'disable':
        try:
            new_disable_subsets = []
            for each_subset in spec_ns_eps.subsets:
                if each_subset.addresses is None:
                    new_disable_subsets.append(each_subset)
                    continue
                # print each_subset.addresses[0].ip+':'+str(each_subset.ports[0].port)
                if each_subset.addresses[0].ip+':'+str(each_subset.ports[0].port) == ops_k8s_ep:
                    each_subset.not_ready_addresses = each_subset.addresses
                    each_subset.addresses = None
                new_disable_subsets.append(each_subset)
            spec_ns_eps.subsets = new_disable_subsets
            spec_ns_eps.metadata.annotations['calledSource'] = 'python-client'
            logger.info(spec_ns_eps)
            # for each_ep_name in api_instance.list_namespaced_endpoints(namespace=ops_k8s_ns).items:
            #     if each_ep_name.metadata.name == ops_k8s_name:
            api_instance.replace_namespaced_endpoints(name=ops_k8s_name, namespace=ops_k8s_ns, body=spec_ns_eps)
            return 200
            logger.info('this ep has been deleted on the front side')
            return 200
        except Exception as e:
            logger.error(e)

    elif args[0] == 'enable':
        try:
            new_enable_subsets = []
            if ops_k8s_ep == 'all':
                for each_subset in spec_ns_eps.subsets:
                    if each_subset.not_ready_addresses is None:
                        new_enable_subsets.append(each_subset)
                        continue
                    # print each_subset.not_ready_addresses[0].ip+':'+str(each_subset.ports[0].port)
                    each_subset.addresses = each_subset.not_ready_addresses
                    each_subset.not_ready_addresses = None
                    new_enable_subsets.append(each_subset)
                spec_ns_eps.subsets = new_enable_subsets
            else:
                for each_subset in spec_ns_eps.subsets:
                    if each_subset.not_ready_addresses is None:
                        new_enable_subsets.append(each_subset)
                        continue
                    # print each_subset.not_ready_addresses[0].ip+':'+str(each_subset.ports[0].port)
                    if each_subset.not_ready_addresses[0].ip+':'+str(each_subset.ports[0].port) == ops_k8s_ep:
                        each_subset.addresses = each_subset.not_ready_addresses
                        each_subset.not_ready_addresses = None
                    new_enable_subsets.append(each_subset)
                spec_ns_eps.subsets = new_enable_subsets
            spec_ns_eps.metadata.annotations['calledSource'] = 'python-client'
            logger.info(spec_ns_eps)
            # for each_ep_name in api_instance.list_namespaced_endpoints(namespace=ops_k8s_ns).items:
            #     if each_ep_name.metadata.name == ops_k8s_name:
            api_instance.replace_namespaced_endpoints(name=ops_k8s_name, namespace=ops_k8s_ns, body=spec_ns_eps)
            return 200
            logger.info('this ep has been deleted on the front side')
            return 200
        except Exception as e:
            logger.error(e)
