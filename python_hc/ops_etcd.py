import etcd
from archive_logger import TNLog

logger = TNLog()
class set_etcd_down_ep():
    def __init__(self, host='127.0.0.1', port=2379):
        self.host = host
        self.port = port
        self.client = etcd.Client(host=self.host, port=self.port)

    def write_etcd_down_ep(self, arg):
        try:
            self.client.write('/heye/down_ep_key', arg)
            return {'code':200}
        except Exception as e:
            logger.error(e)
            return {'code':500}

    def read_etcd_down_ep(self):
        try:
            ep_directory = self.client.get('/heye/down_ep_key').value
            return ep_directory
        except Exception as e:
            logger.error(e)
