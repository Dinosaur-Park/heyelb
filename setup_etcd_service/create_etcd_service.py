import yaml, etcd3, random, para_logger
import init_config, time

logger = para_logger.TNLog()
def create_service(newfile):

    with open(newfile, "r") as f:
        f_content = f.read()
    f_format_yaml = yaml.load(f_content, Loader=yaml.FullLoader)
    logger.info(f_format_yaml)
    service_id = random.randint(0,10000) + int(round(time.time()*1000))
    f_format_yaml['id'] = service_id
    f_format_yaml['status'] = 'put'
    if f_format_yaml.get('real_server', None) is None or f_format_yaml.get('virtual_server', None) is None or f_format_yaml.get('name', None) is None:
        return {'code': 400, 'message': 'wrong file format'}
    if f_format_yaml['virtual_server'].get('ip', None) is None or f_format_yaml['virtual_server'].get('port', None) is None or \
                    f_format_yaml['virtual_server'].get('protocol', None) is None or f_format_yaml['real_server'][0].get('ip', None) is None or \
                    f_format_yaml['real_server'][0].get('ports', None) is None or f_format_yaml['real_server'][0].get('healthcheck', None) is None or \
            f_format_yaml['virtual_server'].get('protocol', None) not in ('tcp', 'udp') or f_format_yaml['real_server'][0].get('healthcheck', None) not in ('tcp', 'http'):
        return {'code': 400, 'message': 'wrong file format'}
    try:
        etcd = etcd3.client(host=init_config.init_config['etcd']['ip'], port=init_config.init_config['etcd']['port'])
        etcd.put('/parasaus/service/%d' %service_id, str(f_format_yaml))
        return {'code':200}
    except Exception as e:
        logger.error(e)
