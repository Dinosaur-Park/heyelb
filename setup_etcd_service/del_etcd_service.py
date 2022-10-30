import yaml, etcd3, random, para_logger
import init_config, time

logger = para_logger.TNLog()
def del_service(svc_id):
    etcd = etcd3.client(host=init_config.init_config['etcd']['ip'], port=init_config.init_config['etcd']['port'])
    try:
        if etcd.delete('/parasaus/service/%s' %svc_id) == True:
            return {'code':200}
        else:
            return {'code':400}
    except Exception as e:
        logger.error(e)
        return {'code': 400}
