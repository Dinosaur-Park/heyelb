import sys, check_init_config, init_config, os, para_logger
from setup_ka_config import build_ka_config as bkc
from setup_etcd_service import create_etcd_service as ces
from setup_etcd_service import del_etcd_service as des
from setup_etcd_service import get_etcd_service as ges
from setup_etcd_service import modify_etcd_service as mes
from setup_lvs_config import create_paralet_service as cps

def first_config():
    try:
        # if sys.argv[1] == '-h':
        #     print('paractl: the next distribute loadbalancer')
        #     print(' -h')
        #     print('\t The help message of paractl.')
        #     print(' init')
        #     print('\t initial the first configuration.')
        #     print(' create dir/filename')
        #     print('\t create a service.')
        #     print(' delete id')
        #     print('\t delete a service.')
        #     print(' get id')
        #     print('\t get all service or one service information.')
        #     print(' modify id dir/filename')
        #     print('\t modify a service.')
        if sys.argv[1] == 'init':
            if check_init_config.check_format().get('code', 'null') != 200:
                print(check_init_config.check_format().get('error_msg', 'initial configuration is wrong, please correct it.'))
                return
            else:
                # install some rpm, include keepalived, ipvsadm and conntrack
                for each_install_server in init_config.init_config['servers'].keys():
                    os.system('ssh %s mkdir -p %s' %(each_install_server, para_logger.dir))
                    excute_result = os.system('ssh %s yum install -y keepalived.x86_64 ipvsadm.x86_64  conntrack-tools.x86_64' %each_install_server)
                    assert excute_result == 0, print('something is wrong with install parasaus packages on remote-host, '
                                                     'please check yum repo or password-less login.')
                    os.system('ssh %s systemctl start keepalived.service&systemctl enable keepalived.service&modprobe ip_vs' %each_install_server)
                    print('host %s basic packages installed successfully' %each_install_server)
                bkc_instance = bkc.build_ka_config()
                bkc_instance.assemble_config()
                cps.create_paralet()
                for each_deploy_server in init_config.init_config['servers'].keys():
                    deploy_result = os.system('scp new_ka_config_files/%s/keepalived.conf %s:/etc/keepalived/' %(each_deploy_server, each_deploy_server))
                    assert deploy_result == 0, print('something is wrong with host configuration, please check '
                                                     'password-less login.')
                    dsb_file_path = 'new_ka_config_files/dis-split-brain.sh'
                    os.system('scp %s %s:/etc/keepalived' %(dsb_file_path, each_deploy_server))
                    os.system('ssh %s systemctl restart keepalived.service' %each_deploy_server)
                    print('host %s para-proxy deployed successfully' %each_deploy_server)
                    # create paralet service file, start and enable paralet
                    paralet_file_path = 'dist/paralet'
                    paralet_systemctl_path = 'dist/paralet.service'
                    os.system('scp %s %s:/usr/bin' %(paralet_file_path, each_deploy_server))
                    os.system('scp %s %s:/usr/lib/systemd/system' %(paralet_systemctl_path, each_deploy_server))
                    os.system('ssh %s systemctl daemon-reload&systemctl start paralet.service&systemctl enable paralet.service' %each_deploy_server)
                    print('host %s paralet deployed successfully' %each_deploy_server)

        if sys.argv[1] == 'create':
            print(ces.create_service(sys.argv[2]))
        if sys.argv[1] == 'delete':
            print(des.del_service(sys.argv[2]))
        if sys.argv[1] == 'get':
            print(ges.get_service(sys.argv[2]))
        if sys.argv[1] == 'modify':
            print(mes.modify_service(sys.argv[2], sys.argv[3]))
        # add vip&node&tunning through paractl

    except Exception as e:
        print(e)

if __name__ == '__main__':
    first_config()