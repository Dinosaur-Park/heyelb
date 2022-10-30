import os
from para_logger import TNLog

logger = TNLog()
def set_ipvs_snat():
    try:
        os.system('echo 1 > /proc/sys/net/ipv4/conf/all/forwarding')
        os.system('echo 1 > /proc/sys/net/ipv4/vs/conntrack')
        if os.popen('iptables -t nat -L|grep MASQUERADE|grep anywhere|grep all') == 0:
            logger.info('rules existed and excuted succesfully')
            return {'code':200,'message':'rules existed'}
        else:
            os.system('iptables -t nat -A POSTROUTING -j MASQUERADE')
            logger.info('excuted succesfully')
            return {'code':200}
    except Exception as e:
        logger.error(e)