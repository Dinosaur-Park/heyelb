from para_logger import TNLog

logger = TNLog()
def del_lvs_config(svc_id):
    ka_file_path = '/etc/keepalived/keepalived.conf'
    with open(ka_file_path, 'r') as f:
        f_content = f.readlines()
    try:
        if '# %s\n' %svc_id in f_content:
            entry_start_index = f_content.index('# %s\n' %svc_id)
            entry_end_index = f_content[entry_start_index:].index('}\n')
            f_content = f_content[0:entry_start_index] + f_content[entry_start_index+entry_end_index+1:]
            logger.info(''.join(f_content))
        else:
            logger.info({"message": "no this virtual server.", "code": 400})
    except Exception as e:
        logger.error(e)

    with open(ka_file_path, 'w') as f:
        f.write(''.join(f_content))
