"""Entry point for device polling"""

import GetWithNetconf as Netconf
import GetWithNetmiko as Ssh
from multiprocessing import Process
import DbOperations as DbOps
import IOSXERouting as GetRoutes
import time


def poll_device_netmiko(device, username, password, ssh_port, model, netconf_port):
    """Calls polling for netmiko"""

    Ssh.PollWithNetmiko(device, username, password, ssh_port, model, netconf_port)


def poll_device_netconf(device, username, password, netconf_port, model):
    """Calls polling netconf"""

    Netconf.PollWitNetconf(device, username, password, netconf_port, model)


def poll_routing_table(device, username, password, ssh_port):
    """Calls polling routing table"""

    GetRoutes.RoutingIos(device, username, password, ssh_port)


def start_proccess(host):
    """Initiate polling processes"""

    start_polling = Process(target=poll_device_netconf, args=(
        host.unique_id, host.username, host.password, host.netconf_port, host.model))
    start_polling.start()

    start_polling = Process(target=poll_routing_table, args=(
        host.unique_id, host.username, host.password, host.ssh_port))
    start_polling.start()

    start_polling = Process(target=poll_device_netmiko, args=(
        host.unique_id, host.username, host.password, host.ssh_port, host.model, host.netconf_port))
    start_polling.start()


if __name__ == '__main__':

    # Set polling interval
    polling_interval = int(input("Polling Interval: "))

    while True:
        for i in DbOps.session.query(DbOps.DeviceFacts).all():
            start_proccess(i)
            # Stagger polling between devices
            time.sleep(10)
        time.sleep(polling_interval)
