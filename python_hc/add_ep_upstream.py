import crossplane, os
from archive_logger import TNLog

ng_main_config_file = '/export/home/yeepine-1.0/conf/nginx.conf'
ng_upstream_file = '/export/home/yeepine-1.0/conf/servers/upstream.conf'
ng_main_cmd = '/export/home/yeepine-1.0/sbin/nginx -s reload'
logger = TNLog()

def add_ep_from_upstream(args):
    payload = crossplane.parse(ng_main_config_file)
    new_ng_arg = {}
    logger.info(args)
    for each_config in payload['config']:
        if each_config['file'] == ng_upstream_file:
            new_ng_arg['args'] = []
            new_ng_arg['args'].append(args[0])
            new_ng_arg['directive'] = 'upstream'
            new_ng_arg['block'] = []

            for each_arg in args[2]:
                new_ng_arg['block'].append({'args': [each_arg], 'directive': 'server'})
            # new_ng_arg['block'].append({'args': ['127.0.0.1:80'], 'directive': 'server'})

            if args[3] == 'tcp':
                healthcheck_format = [{'args': ['interval=2000', 'rise=5', 'fall=2', 'timeout=500', 'type=tcp'],'directive': 'check'}]
            elif args[3] == 'http':
                healthcheck_format = [{'args': ['interval=2000', 'rise=5', 'fall=2', 'timeout=500', 'type=http'],'directive': 'check'},
                                      {'args': ['HEAD / HTTP/1.0\\r\\n\\r\\n'],'directive': 'check_http_send'},
                                      {'args': ['http_2xx','http_3xx'],'directive': 'check_http_expect_alive'}]
            elif args[3] == 'mysql':
                healthcheck_format = [{'args': ['interval=2000', 'rise=5', 'fall=2', 'timeout=500', 'type=mysql'],'directive': 'check'}]
            else:
                logger.info('this health check type is not supported')
                return
            for each_hc in healthcheck_format:
                new_ng_arg['block'].append(each_hc)
            logger.info(each_config['parsed'].append(new_ng_arg))
            break
    new_ng_config = crossplane.build(each_config['parsed'])
    logger.info(new_ng_config)
    try:
        with open(ng_upstream_file, 'w') as new_ng_config_upstream:
            new_ng_config_upstream.writelines(new_ng_config)
        #restart nginx
        os.system(ng_main_cmd)
    except Exception as e:
        logger.error(e)