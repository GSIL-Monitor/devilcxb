# -*- coding:utf-8 -*-
import sys
import os

if os.environ.get("WORKSPACE"):
    sys.path.append(os.path.join(os.environ.get("WORKSPACE"), "AutoTest"))
import compareXconf
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


if __name__ == '__main__':
    if os.environ.get("env"):
        env = os.environ.get("env")
        cmp_name = os.environ.get("cmp_name")
        app_name = os.environ.get("app_name")
    else:
        env = "BetaC"
        cmp_name = "zhenliang"
        app_name = "loan-betac"
    Xconf_obj= compareXconf.GetXconf(env)
    for service_name in Xconf_obj.get_service_dict(app_name="loan-betac", cmp_name="zhenliang").keys():
        Xconf_obj.sync_zk(app_name=app_name, cmp_name=cmp_name, service_name=service_name)