"""Helper functions that get output via netmiko"""

import collections
import ipaddress
import app.Modules.GetInterfaces as GetInterfacesInfo
import app.Modules.connection as ConnectWith
import app.base.routes as Credentials
from netmiko import ConnectHandler, ssh_exception


def send_command(netmiko_connection, command, expect_string=None):
    """Send Netmiko commands"""

    netmiko_connection = netmiko_connection
    get_response = None

    if expect_string is None:

        retries = 0
        while retries != 3:
            try:
                get_response = netmiko_connection.send_command(command_string=command)
                break
            except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                netmiko_connection = ConnectWith.creat_netmiko_connection(Credentials.username, Credentials.password,
                                                                          Credentials.device)
                Credentials.netmiko_session = netmiko_connection
                retries += 1

    else:

        retries = 0
        while retries != 3:
            try:
                get_response = netmiko_connection.send_command(command_string=command, expect_string=expect_string)
                break
            except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                netmiko_connection = ConnectWith.creat_netmiko_connection(Credentials.username, Credentials.password,
                                                                          Credentials.device)
                retries += 1

    if retries == 3:
        get_response = 'Error Connecting'

    return get_response


def get_device_model(netmiko_connection):
    """Get device model"""

    model = None
    show_inventory = send_command(netmiko_connection, 'show inventory')

    for i in show_inventory.splitlines():
        if i.rfind('Chassis') != -1:
            model = i.split("\"")[3].split()[1][0:3]

    return model


def get_vrfs(netmiko_connection):
    """Get device model"""

    vrfs = []
    get_vrf = send_command(netmiko_connection, 'show vrf')

    for i in get_vrf.splitlines():
        try:
            if i.rfind('Name') == -1:
                vrfs.append(i.split()[0])
        except IndexError:
            pass

    return vrfs


def get_bgp_status(netmiko_connection):
    """Gets BGF neighbor statuses"""

    local_as = ['Null']
    neighbor_status = collections.defaultdict(list)
    bgp_summary = send_command(netmiko_connection, 'show ip bgp summary')

    for i in bgp_summary.splitlines():
        if i.rfind('local AS number') != -1:
            local_as = i.split()[-1:]
        try:
            neighbor = ipaddress.ip_address(i.split()[0])
            neighbor_status[neighbor].append(
                {"Neighbor": i.split()[0], 'AS': i.split()[2], 'Uptime': i.split()[8],
                 'Prefixes': i.split()[9]})
        except (ValueError, IndexError):
            pass

    return neighbor_status, local_as


def get_ospf_status(netmiko_connection):
    """Gets OSPF neighbor statuses"""

    neighbor_status = collections.defaultdict(list)
    ospf_summary = send_command(netmiko_connection, 'show ip ospf neighbor')

    if ospf_summary:
        for i in ospf_summary.splitlines():
            try:
                neighbor = ipaddress.ip_address(i.split()[0])
                neighbor_status[neighbor].append(
                    {"NeighborID": i.split()[0], 'State': i.split()[2].strip("/"), 'Address': i.split()[5],
                     'Interface': i.split()[6]})
            except (ValueError, IndexError):
                pass
    else:
        ip_ospf = send_command(netmiko_connection, 'show ip ospf')
        if ip_ospf:
            neighbor_status['neighbor'].append(
                {"NeighborID": 'No Established Neighbors', 'State': '', 'Address': '',
                 'Interface': ''})
        else:
            neighbor_status = {}

    return neighbor_status


def get_ospf_processes(netmiko_connection):
    """Get OSPF processes"""

    processes = []
    ospf_process = send_command(netmiko_connection, 'show ip ospf | i Process')

    if ospf_process:
        for process in ospf_process.splitlines():
            try:
                processes.append(process.split('"')[1].split()[1])
            except IndexError:
                continue

    return processes


def get_arp(netmiko_connection):
    """Get ARP table"""

    arps = []
    get_arps = send_command(netmiko_connection, 'show ip arp')

    if get_arps:
        for i in get_arps.splitlines():
            try:
                if i.split()[0] != 'Protocol':
                    arps.append(
                        {"Protocol": i.split()[0], 'Address': i.split()[1], 'Age': i.split()[2],
                         'MAC': i.split()[3], 'Type': i.split()[4], 'Interfaces': i.split()[5]})
            except IndexError:
                pass
    else:
        return 'An Error Occured'

    return arps


def clear_counters(netmiko_connection, interface, netconf_session):
    """Clears interface counters"""

    send_command(netmiko_connection, f"clear counters {interface}", expect_string="[confirm]")
    send_command(netmiko_connection, "\n", expect_string="#")
    refresh_interfaces = GetInterfacesInfo.get_ip_interfaces(netconf_session)

    return refresh_interfaces[0]


def clear_arp(netmiko_connection):
    """Clears ARP table"""

    send_command(netmiko_connection, 'clear arp')
    send_command(netmiko_connection, 'clear arp-cache')
    refreshed_arp = get_arp(netmiko_connection)

    return refreshed_arp
