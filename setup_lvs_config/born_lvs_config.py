from para_logger import TNLog

logger = TNLog()
def born_lvs_config(args):
    vs_ip = args['virtual_server'].get('ip', None)
    vs_port = args['virtual_server'].get('port', None)
    vs_dl = args['virtual_server'].get('delay_loop', None)
    vs_la = args['virtual_server'].get('lb_algo', None)
    vs_pt = args['virtual_server'].get('persistence_timeout', None)

    f_tcp_content = []
    f_tcp_content.insert(0, '}\n')
    f_tcp_content.insert(0, 'virtual_server %s %d {\n' %(vs_ip, vs_port))
    f_tcp_content.insert(0, '# %d\n' %args['id'])
    if vs_dl is not None:
        f_tcp_content.insert(2, '   delay_loop %d\n' %vs_dl)
    else:
        f_tcp_content.insert(2, '   delay_loop 3\n')
    if vs_la is not None:
        f_tcp_content.insert(-2, '   lb_algo %s\n' %vs_la)
    else:
        f_tcp_content.insert(-2, '   lb_algo rr\n')
    f_tcp_content.insert(-2, '   lb_kind nat\n')
    if args['virtual_server']['protocol'] == 'tcp':
        f_tcp_content.insert(-2, '   protocol TCP\n')
        if vs_pt is not None:
            f_tcp_content.insert(-2, '   persistence_timeout %d\n' %vs_pt)
        for each_rs in args['real_server']:
            rs_ip = each_rs.get('ip', None)
            rs_ports = each_rs.get('ports', None)
            rs_weight = each_rs.get('weight', None)
            rs_ngr = each_rs.get('nb_get_retry', None)
            rs_dbr = each_rs.get('delay_before_retry', None)
            rs_ct = each_rs.get('connect_timeout', None)
            rs_path = each_rs.get('url', '/')
            f_tcp_content.insert(-2, '   real_server %s %d{\n' %(rs_ip, rs_ports))
            if rs_weight is not None:
                f_tcp_content.insert(-2, '       weight %d\n' %rs_weight)

            if args['real_server'][0]['healthcheck'] == 'tcp':
                f_tcp_content.insert(-2, '       TCP_CHECK {\n')
                f_tcp_content.insert(-2, '           connect_port %d\n' % rs_ports)
            elif args['real_server'][0]['healthcheck'] == 'http':
                f_tcp_content.insert(-2, '       HTTP_GET {\n')
                f_tcp_content.insert(-2, '            url {\n')
                f_tcp_content.insert(-2, '              path %s\n' %rs_path)
                f_tcp_content.insert(-2, '              status_code 200-299 300-399\n')
                f_tcp_content.insert(-2, '            }\n')

            if rs_ngr is not None:
                f_tcp_content.insert(-2, '           nb_get_retry %d\n' %rs_ngr)
            else:
                f_tcp_content.insert(-2, '           nb_get_retry 3\n')
            if rs_dbr is not None:
                f_tcp_content.insert(-2, '           delay_before_retry %d\n' %rs_dbr)
            else:
                f_tcp_content.insert(-2, '           delay_before_retry 3\n')
            if rs_ct is not None:
                f_tcp_content.insert(-2, '           connect_timeout %d\n' %rs_ct)
            else:
                f_tcp_content.insert(-2, '           connect_timeout 2\n')
            f_tcp_content.insert(-2, '       }\n')
            f_tcp_content.insert(-2, '   }\n')
    elif args['virtual_server']['protocol'] == 'udp':
        f_tcp_content.insert(-2, '   protocol UDP\n')
        for each_rs in args['real_server']:
            rs_ip = each_rs.get('ip', None)
            rs_ports = each_rs.get('ports', None)
            rs_weight = each_rs.get('weight', None)
            f_tcp_content.insert(-2, '   real_server %s %d{\n' % (rs_ip, rs_ports))
            if rs_weight is not None:
                f_tcp_content.insert(-2, '       weight %d\n' %rs_weight)
            f_tcp_content.insert(-2, '       }\n')
    logger.info(f_tcp_content)
    logger.info(''.join(f_tcp_content))

    ka_file_path = '/etc/keepalived/keepalived.conf'
    with open(ka_file_path, 'a') as f:
        f.write(''.join(f_tcp_content))
