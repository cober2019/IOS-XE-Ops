"""Helper functions that get output via netmiko"""

import collections
import ipaddress
import string
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
                get_response = netmiko_connection.send_command(command)
                break
            except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                netmiko_connection = ConnectWith.creat_netmiko_connection(Credentials.username, Credentials.password,
                                                                          Credentials.device, Credentials.ssh_port)
                Credentials.netmiko_session = netmiko_connection
                retries += 1

    else:

        retries = 0
        while retries != 3:
            try:
                get_response = netmiko_connection.send_command(command, expect_string=expect_string)
                break
            except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
                netmiko_connection = ConnectWith.creat_netmiko_connection(Credentials.username, Credentials.password,
                                                                          Credentials.device, Credentials.ssh_port)
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

def check_for_addr_family(netmiko_connection):

    addr_family = send_command(netmiko_connection, 'show ip bgp ipv4 unicast')

    return addr_family

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

def more_int_details(netmiko_connection, interface):

    get_more_details = send_command(netmiko_connection, f'show interface {interface}')

    return get_more_details

def more_qos_details(netmiko_connection, interface):

    get_more_details = send_command(netmiko_connection, f'show policy-map interface {interface}')

    return get_more_details

def get_route_detials(netmiko_connection, prefix, protocol):

    get_detials = []

    get_route = send_command(netmiko_connection, f'show ip route {prefix}')

    if protocol == 'O E1':
        get_detials = send_command(netmiko_connection, f'show ip ospf database external {prefix}')
    elif protocol == 'O E2':
        get_detials = send_command(netmiko_connection, f'show ip ospf database external {prefix}')
    elif protocol == 'B':
        get_detials = send_command(netmiko_connection, f'show bgp {prefix}')

    return get_route, get_detials

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

def send_ping(netmiko_connection, destination, source, count, vrf=None):
    """Clears ARP table"""

    if vrf is None:
        pings = send_command(netmiko_connection, f'ping {destination} source {source} repeat {count}')
    else:
        pings = send_command(netmiko_connection, f'ping vrf {vrf} {destination} source {source} repeat {count}')

    return pings


def get_cpu(netmiko_session):
    """Gets mac and arp tables. Concatinates into one"""

    tables = collections.defaultdict(list)
    tables_2 = collections.defaultdict(list)
    final_table = collections.defaultdict(list)
    get_cpu = 'show processes cpu history'
    current_time = None

    # Gets and parse mac table response
    cpu_table = send_command(netmiko_session, get_cpu)
    for line in reversed(cpu_table):
        try:
            if not line:
                continue
            if line.rfind('last 72 hours') != -1:
                current_time = '72hr'
            if line.rfind('last 60 minutes') != -1:
                current_time = '60min'
            if line.rfind('last 60 seconds') != -1:
                current_time = '60sec'

            if line.split()[1][0] == '#' or line.split()[1][0] == '*':
                percent = {'percent': line.split()[0], 'time': list(line[6:])}
                tables[current_time].append(percent)

        except IndexError:
            pass

    # 72 hours CPU
    for i in tables['72hr']:
        for index, marker in enumerate(i['time']):
            if marker == '#' or marker == '*':
                tables_2[index].append(int(i['percent']))

    seven_two_hour_table = {'72hrs': tables_2}
    for k, v in seven_two_hour_table.items():
        for a, b in v.items():
            final_table['72hr'].append({str(a): list(reversed(b))[0]})

    # 60 minutes CPU
    tables_2 = collections.defaultdict(list)
    for i in tables['60min']:
        for index, marker in enumerate(i['time']):
            if marker == '#' or marker == '*':
                tables_2[index].append(int(i['percent']))

    sixty_min_table = {'60min': tables_2}
    for k, v in sixty_min_table.items():
        for a, b in v.items():
            final_table['60min'].append({str(a): list(reversed(b))[0]})

    # 60 seconds CPU
    tables_2 = collections.defaultdict(list)
    for i in tables['60sec']:
        for index, marker in enumerate(i['time']):
            if marker == '#' or marker == '*':
                tables_2[index].append(int(i['percent']))

    sixty_sec_table = {'60sec': tables_2}
    for k, v in sixty_sec_table.items():
        for a, b in v.items():
            final_table['60sec'].append({str(a): list(reversed(b))[0]})

    return final_table


def get_cdp_neighbors_detail(netmiko_session, port):
    """Gets mac and arp tables. Concatinates into one"""

    get_cdp_neigh = f'show cdp neighbors {port} detail'
    cdp_neighbors = send_command(netmiko_session, get_cdp_neigh)
   
    return cdp_neighbors


def get_span_detail(netmiko_session, vlan):
    """Gets mac and arp tables. Concatinates into one"""

    get_span_detail = f'show spanning-tree vlan {vlan} '
    span_vlan = send_command(netmiko_session, get_span_detail)

    return span_vlan


def get_cdp_neighbors(netmiko_session):
    """Gets mac and arp tables. Concatinates into one"""

    neighbors = []
    get_cdp_neigh = 'show cdp neighbors'
    name = None
    local_port = None
    remote_port = None

    # Gets and parse mac table response
    cdp_neighbors = send_command(netmiko_session, get_cdp_neigh)
    for neighbor in cdp_neighbors.splitlines():
        try:
            if not neighbor:
                continue
            elif neighbor.split()[0] == "":
                continue
            elif neighbor.split()[0] == 'Capability':
                continue
            elif neighbor.split()[0] == 'Device':
                continue
            if len(neighbor.split()) == 1:
                name = neighbor.split()[0]
            elif len(neighbor.split()) == 7:
                remote_port = neighbor.split()[5] + neighbor.split()[6]
                local_port = neighbor.split()[0] + neighbor.split()[1]
            elif len(neighbor.split()) == 8:
                remote_port = neighbor.split()[6] + neighbor.split()[7]
                local_port = neighbor.split()[0] + neighbor.split()[1]
            elif len(neighbor.split()) == 9:
                remote_port = neighbor.split()[7] + neighbor.split()[8]
                local_port = neighbor.split()[0] + neighbor.split()[1]

        except IndexError:
            continue

        if remote_port is not None:
            neighbors.append({'name': name, 'local-port': local_port, 'remote-port': remote_port})
            name = None
            local_port = None
            remote_port = None

    return neighbors

def get_span_root(netmiko_session) -> list:
    """Gets mac and arp tables. Concatinates into one"""

    span_table = []
    get_macs = 'show spanning-tree root'

    # Gets and parse mac table response
    table = send_command(netmiko_session, get_macs)

    for vlan in table.splitlines():
        try:
            if vlan.split()[0].rfind("-") != -1:
                continue
            elif vlan.split()[0] == 'Vlan':
                continue
            else:
                if vlan.split()[0][-2] == "0":

                    if len(vlan.split()) == 8:
                        span_table.append(
                            {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                             'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                    elif len(vlan.split()) == 7:
                        span_table.append(
                            {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                             'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
                else:

                    if len(vlan.split()) == 8:
                        span_table.append(
                            {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                             'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                    elif len(vlan.split()) == 7:
                        span_table.append(
                            {'vlan': vlan.split()[0].strip('VLAN'), 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                             'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
        except IndexError:
            continue

    return span_table


def get_mac_arp_table(netmiko_session) -> list:
    """Gets mac and arp tables. Concatinates into one"""

    mac_table = []
    arp_table = []


    get_macs = 'show mac address-table'
    gets_arps = 'show ip arp'

    # Gets and parse mac table response
    table = send_command(netmiko_session, get_macs)
    for mac in table.splitlines():
        try:
            if mac.split()[0].rfind("-") != -1:
                continue
            elif mac.split()[0] == 'Vlan':
                continue
            elif mac.split()[0] == 'All':
                continue
            elif mac.split()[0] == 'Total':
                continue
            else:
                mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                       'interface': mac.split()[3]})
        except IndexError:
            continue

    # Gets and parse arp table response
    arps = send_command(netmiko_session, gets_arps)
    for arp in arps.splitlines():
        try:
            if arp.split()[0] == 'Protocol':
                continue
            elif arp.split()[0] == 'Total':
                continue
            else:
                arp_table.append(
                    {'protocol': arp.split()[0], 'ip': arp.split()[1], 'age': arp.split()[2], 'mac': arp.split()[3],
                     'interface': arp.split()[5]})
        except IndexError:
            continue

    # Check to see if mac has an arp entry. If so, add k/v to existing dictionary
    for mac in mac_table:
        for entry in arp_table:
            if mac.get('address') == entry.get('mac'):
                mac['ip'] = entry.get('ip')
                mac['ip_int'] = entry.get('interface')
                break
            else:
                mac['ip'] = 'None'

    return mac_table


def get_mac_table(netmiko_session):

    mac_table = []
    get_macs = 'show mac address-table'

    # Gets and parse mac table response
    table = send_command(netmiko_session, get_macs)
    for mac in table.splitlines():
        try:
            if mac.split()[0].rfind("-") != -1:
                continue
            elif mac.split()[0] == 'Vlan':
                continue
            elif mac.split()[0] == 'All':
                continue
            elif mac.split()[0] == 'Total':
                continue
            else:
                mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                  'interface': mac.split()[3]})
        except IndexError:
            continue

    return mac_table

def get_netmiko_vlans(netmiko_session) -> list:
    """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
    to find the routes and route types."""

    vlan_table = []
    iter_vlan = "1"
    get_vlans = 'show vlan brief'
    get_vlan_pro = 'show spanning-tree bridge priority'
    vlan_ports = None

    vlans = send_command(netmiko_session, get_vlans)
    get_prio = send_command(netmiko_session, get_vlan_pro)

    # Parse netmiko vlan reponse
    for vlan in vlans.splitlines():
        try:
            if not vlan:
                continue
            if not (enumerate(vlan.split(), 0)):
                continue
            elif vlan.split()[0] == "":
                continue
            elif vlan.split()[0].rfind("VLAN") != -1:
                continue
            elif vlan.split()[0].rfind("-") != -1:
                continue

            if iter_vlan != vlan.split()[0] or iter_vlan == "1":
                if vlan.split()[0].rfind("/") != -1:
                    vlan_ports = ' '.join(vlan.split())
                else:
                    vlan_ports = ' '.join(vlan.split()[3:])

            for prio in get_prio:
                try:
                    if list(enumerate(prio.split(), 0))[0][1][-2:] == list(enumerate(vlan.split(), 0))[0][1]:
                        vlan_table.append(
                            {'id': prio.split()[0][-2:], 'prio': prio.split()[1], 'name': vlan.split()[1],
                             'status': vlan.split()[2], 'ports': vlan_ports})
                except IndexError:
                    pass

            iter_vlan = vlan.split()[0]
            
        except IndexError:
            pass

    return vlan_table

def get_access_ports(netmiko_session) -> list:
    """Get trunks"""

    interfaces = []
    interface_command = 'show interfaces status'

    get_interfaces = send_command(netmiko_session, interface_command)

    cli_line = get_interfaces.split("\n")
    for line in cli_line:
        if not list(enumerate(line.split(), 0)):
            continue
        if line.split()[0] == "Port":
            continue
        else:
            try:
                interfaces.append({'interface': line.split()[0],'vlan': line.split()[2], 'status': line.split()[1], 'duplex': line.split()[3],
                                   'speed': line.split()[4], 'type': line.split()[5]})
            except IndexError:
                interfaces.append({'interface': line.split()[0],'vlan': line.split()[2], 'status': line.split()[1], 'duplex': line.split()[3],
                                   'speed': line.split()[4], 'type': 'None'})

    return interfaces

def mac_to_access(access_ports, mac_table):

    for mac in mac_table:
        for port in access_ports:
            if '/' not in mac["interface"]:
                pass
            elif mac["interface"] == port["interface"]:
                port['mac'] = mac['address']
                port['type'] = mac['type']
            else:
                port['mac'] = 'Unknown'
                port['type'] = 'Unknown'

    for i in access_ports:
        print(i)
    return access_ports



def appy_mac(netmiko_session, interface):

    config_portsec_commands = [f"interface {interface}", "switchport mode access",
                               "switchport access vlan 11", "switchport port-security",
                               "switchport port-security mac-address sticky"]

    for i in config_portsec_commands:
        send_command(netmiko_session)
