import yaml, etcd3, para_logger
import init_config

logger = para_logger.TNLog()
def modify_service(svc_id, newfile):
    etcd = etcd3.client(host=init_config.init_config['etcd']['ip'], port=init_config.init_config['etcd']['port'])
    if etcd.get('/parasaus/service/%s' %svc_id)[0] is None:
        return {'code':404, 'message':'no such key'}

    try:
        with open(newfile, "r") as f:
            f_content = f.read()
        f_format_yaml = yaml.load(f_content, Loader=yaml.FullLoader)
        if f_format_yaml.get('real_server', None) is None or f_format_yaml.get('virtual_server', None) is None or \
                        f_format_yaml.get('name', None) is None:
            return {'code': 400, 'message': 'wrong file format'}
        if f_format_yaml['virtual_server'].get('ip', None) is None or f_format_yaml['virtual_server'].get('port',
                                                                                                          None) is None or \
                        f_format_yaml['virtual_server'].get('protocol', None) is None or f_format_yaml[
            'real_server'][0].get('ip', None) is None or \
                        f_format_yaml['real_server'][0].get('ports', None) is None or f_format_yaml['real_server'][0].get('healthcheck', None) is None or \
                        f_format_yaml['virtual_server'].get('protocol', None) not in ('tcp', 'udp') or f_format_yaml['real_server'][0].get('healthcheck', None) not in ('tcp', 'http'):
            return {'code': 400, 'message': 'wrong file format'}
        f_format_yaml['id'] = int(svc_id)
        f_format_yaml['status'] = 'modify'
        etcd.put('/parasaus/service/%d' %int(svc_id), str(f_format_yaml))
        logger.info(str(f_format_yaml))
        return {'code': 200}
    except Exception as e:
        logger.error(e)
