import etcd3, os
from para_logger import TNLog
from setup_lvs_config import born_lvs_config as blc
from setup_lvs_config import del_lvs_config as dlc

logger = TNLog()
class watch_svc_change():
    def __init__(self, host='127.0.0.1', port=2379):
        self.host = host
        self.port = port
        self.client = etcd3.client(host=self.host, port=self.port)

    def entry_change(self):
        try:
            events_iterator, cancel = self.client.watch_prefix("/parasaus/service/")
            for event in events_iterator:
                logger.info(event)
                if isinstance(event, etcd3.events.PutEvent):
                    lvs_content = eval(event.value.decode('utf-8'))
                    logger.info(lvs_content)
                    if lvs_content['status'] == 'put':
                        blc.born_lvs_config(lvs_content)
                        # reload keepalived
                        os.system('systemctl reload keepalived.service')
                    if lvs_content['status'] == 'modify':
                        dlc.del_lvs_config(lvs_content['id'])
                        blc.born_lvs_config(lvs_content)
                        # reload keepalived
                        os.system('systemctl reload keepalived.service')
                if isinstance(event, etcd3.events.DeleteEvent):
                    logger.info('DeleteEvent')
                    svc_id = event.key.decode('utf-8').split('/')[-1]
                    dlc.del_lvs_config(svc_id)
                    # reload keepalived
                    os.system('systemctl reload keepalived.service')

        except Exception as e:
            logger.error(e)
            cancel()

# watch_svc_change().entry_change()



