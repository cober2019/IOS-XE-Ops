"""Entry point for device polling"""

import XEOpsDatabase.GetInterfaces as Netconf
import XEOpsDatabase.GetWithNetmiko as Ssh
from multiprocessing import Process

if __name__ == '__main__':

    # Uses multiprocessing to collect device info using two methods. Netmiko, NETCONF
    # These are objects which will continually loop at the called class

    poll_netconf = Process(target=Netconf.PollWitNetconf)
    poll_netconf.start()

    poll_netmiko = Process(target=Ssh.PollWithNetmiko)
    poll_netmiko.start()
