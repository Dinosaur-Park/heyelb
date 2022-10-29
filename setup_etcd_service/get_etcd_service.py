import etcd3, para_logger
import init_config

logger = para_logger.TNLog()
def get_service(svc_id='all'):
    etcd = etcd3.client(host=init_config.init_config['etcd']['ip'], port=init_config.init_config['etcd']['port'])
    if svc_id == 'all':
        svc_content = etcd.get_prefix('/parasaus/service/')

    else:
        svc_content = etcd.get('/parasaus/service/%s' %svc_id)
    logger.info(svc_content)

    if isinstance(svc_content, tuple) and svc_content[0] is None:
        return {'code':404, 'message':'no such key'}
    if isinstance(svc_content, tuple) and svc_content[0] is not None:
        return {'code':200, 'message':eval(svc_content[0])}
    else:
        all_svc_content = []
        for each_value in svc_content:
            all_svc_content.append(eval(each_value[0]))
        logger.info(all_svc_content)
        return {'code': 200, 'message': all_svc_content}
