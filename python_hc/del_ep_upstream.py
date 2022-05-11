import crossplane, os
from archive_logger import TNLog

ng_main_config_file = '/export/home/yeepine-1.0/conf/nginx.conf'
ng_upstream_file = '/export/home/yeepine-1.0/conf/servers/upstream.conf'
ng_main_cmd = '/export/home/yeepine-1.0/sbin/nginx -s reload'
logger = TNLog()

def del_ep_from_upstream(args):
    try:
        payload = crossplane.parse(ng_main_config_file)
        for each_config in payload['config']:
            if each_config['file'] == ng_upstream_file:
                for index_value, each_config_parsed in enumerate(each_config['parsed']):
                    if each_config_parsed['args'][0] == args[0]:
                        each_config['parsed'].pop(index_value)
        new_ng_config = crossplane.build(each_config['parsed'])
        logger.info(new_ng_config)
        with open(ng_upstream_file, 'w') as new_ng_config_upstream:
            new_ng_config_upstream.writelines(new_ng_config)
        #restart nginx
        os.system(ng_main_cmd)
    except Exception as e:
        logger.error(e)

