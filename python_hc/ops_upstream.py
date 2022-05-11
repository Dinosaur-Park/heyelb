# import crossplane
import time
import del_ep_upstream, add_ep_upstream

def ops_nginx_upstream(args):
    ep_action = args[1]
    if ep_action == "ADDED":
        del_ep_upstream.del_ep_from_upstream(args)
        add_ep_upstream.add_ep_from_upstream(args)

    if ep_action == "MODIFIED":
        del_ep_upstream.del_ep_from_upstream(args)
        add_ep_upstream.add_ep_from_upstream(args)

    if ep_action == "DELETED":
        del_ep_upstream.del_ep_from_upstream(args)


