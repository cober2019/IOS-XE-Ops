"""Helper functions that get output via netmiko"""

import collections
import ipaddress
import string
import app.Modules.connection as ConnectWith
import app.base.routes as Credentials
import app.Database.DbOperations as DbOps
from netmiko import ConnectHandler, ssh_exception
import time

device = None
session = None


def netconf_trunk_helper(interface):
    """Get route-map names"""

    vlans = []
    try:
        for line in send_command(f'show run interface {interface} | i allowed vlan').splitlines():
            if len(line.split()) == 0:
                continue
            elif line.split()[0] == '^':
                break
            elif len(line.split()) == 5:
                vlans.append(line.split()[4])
            elif len(line.split()) == 6:
                vlans.append(line.split()[5])
    except AttributeError:
        pass

    return vlans

def get_dmvpn_interface(session, interface, device):
    """Get route-map names"""

    ip_add, tunnel_source, tunnel_mode, network_id, holdtime, profile, nhrp_shortcut, nhrp_red = None, None, None, None, \
                                                                                                 None, None, None, None

    DbOps.delete_rows('dmvpninterfaces_front_end', device)

    try:
        for line in send_command(f'show run interface {interface} | ex Current|Building|!', session).splitlines():
            if len(line.split()) == 0:
                continue
            elif '^' == line.split()[0]:
                break
            elif 'network-id' in line:
                network_id = line.split()[3]
            elif 'interface' in line:
                pass
            elif 'address' in line:
                ip_add = f'{line.split()[2]} {line.split()[3]}'
            elif 'source' in line:
                tunnel_source = line.split()[2]
            elif 'mode' in line:
                tunnel_mode = f'{line.split()[2]} {line.split()[3]}'
            elif 'protection' in line:
                profile = line.split()[4]
                DbOps.update_dmvpn_interfaces(device, interface, ip_add, tunnel_source, tunnel_mode, network_id, holdtime, profile, nhrp_shortcut, nhrp_red)
            elif 'holdtime' in line:
                holdtime = line.split()[3]

            # Check dmvpn phase commands
            if 'shortcut' in line:
                nhrp_shortcut = line.split()[2]
            if 'redirect' in line:
                nhrp_red = line.split()[2]

    except AttributeError:
        pass

def send_command(command, expect_string=None):
    """Send Netmiko commands"""

    get_response = None
    retries = 0

    while retries != 3:
        try:
            get_response = session.send_command(command)
            break
        except (OSError, TypeError, AttributeError, ssh_exception.NetmikoTimeoutException):
            retries += 1

    return get_response


def get_routing_table(vrfs=None):
    """Using the connection object created from the netmiko_login(), get routes from device"""

    routes = None

    if not vrfs:
        term_length = send_command('terminal length 0')
        send_command(term_length)
        routes = send_command('show ip route')
        get_routes = send_command(routes)
    elif vrfs:
        term_length = send_command('terminal length 0')
        send_command(term_length)
        vrf_routes = send_command(f'show ip route vrf {vrfs}')
        get_routes = send_command(vrf_routes)

    routes = routes.split("\n")

    return routes


def get_vrfs():
    """Get device model"""

    # Delete table data
    DbOps.delete_rows('vrfs_front_end', device)

    try:
        for i in send_command('show vrf').splitlines():
            try:
                if i.rfind('Name') == -1:
                    db_session = DbOps.update_vrfs_table(device, i.split()[0])
            except IndexError:
                pass
    except AttributeError:
        pass


def check_for_addr_family():
    addr_family = send_command('show ip bgp ipv4 unicast')

    return addr_family


def get_bgp_status():
    """Gets BGF neighbor statuses"""

    local_as = ['Null']

    # Delete table data
    DbOps.delete_rows('bgp_front_end', device)

    try:
        for i in send_command('show ip bgp summary').splitlines():
            if i.rfind('local AS number') != -1:
                local_as = i.split()[-1:]
            try:
                ipaddress.ip_address(i.split()[0])
                DbOps.update_bgp_table(device, i.split()[0], i.split()[2], i.split()[8], i.split()[9], local_as)
            except (IndexError, ValueError):
                pass
    except AttributeError:
        pass


def get_ospf_status():
    """Gets OSPF neighbor statuses"""

    neighbor_status = collections.defaultdict(list)

    # Delete table data
    DbOps.delete_rows('ospf_front_end', device)

    try:
        if send_command('show ip ospf neighbor').splitlines():
            for i in send_command('show ip ospf neighbor').splitlines():
                try:
                    neighbor = ipaddress.ip_address(i.split()[0])
                    neighbor_status[neighbor].append(
                        {"NeighborID": i.split()[0], 'State': i.split()[2].strip("/"), 'Address': i.split()[5],
                         'Interface': i.split()[6]})
                except (IndexError, ValueError):
                    pass
        else:
            if send_command('show ip ospf').splitlines():
                neighbor_status['neighbor'].append(
                    {"NeighborID": 'No Established Neighbors', 'State': 'None', 'Address': 'None', 'Interface': 'None'})
            else:
                neighbor_status = []

        if neighbor_status:
            for k, v in neighbor_status.items():
                for i in v:
                    db_session = DbOps.update_ospf_table(device, i['NeighborID'], i['State'], i['Address'],
                                                         i['Interface'])

    except AttributeError:
        pass


def get_ospf_processes():
    """Get OSPF processes"""

    # Delete table data
    DbOps.delete_rows('ospfProcess_front_end', device)

    try:
        if send_command('show ip ospf | i Process').splitlines():
            for process in send_command('show ip ospf | i Process').splitlines():
                try:
                    DbOps.update_ospf_process_table(device, process.split('"')[1].split()[1])
                except IndexError:
                    continue
    except AttributeError:
        pass


def get_arp():
    """Get ARP table"""

    # Delete table data
    DbOps.delete_rows('arp_front_end', device)

    try:
        for i in send_command('show ip arp').splitlines():
            try:
                if i.split()[0] != 'Protocol':
                    DbOps.update_arp_table(device, i.split()[0], i.split()[1], i.split()[2], i.split()[3],
                                           i.split()[4],
                                           i.split()[5])
            except IndexError:
                pass
    except AttributeError:
        pass


def more_int_details(session_obj, interface):
    global session
    session = session_obj

    get_more_details = send_command(f'show interface {interface}')

    return get_more_details


def current_int_config(session_obj, interface):
    global session
    session = session_obj

    get_int_config = send_command(f'show run interface {interface}')

    return get_int_config


def more_qos_details(session_obj, interface):
    global session
    session = session_obj
    get_more_details = send_command(f'show policy-map interface {interface}')

    return get_more_details


def get_route_detials(session_obj, prefix, protocol):
    global session
    session = session_obj

    get_detials = []

    get_route = send_command(f'show ip route {prefix}')

    if protocol == 'O E1':
        get_detials = send_command(f'show ip ospf database external {prefix}')
    elif protocol == 'O E2':
        get_detials = send_command(f'show ip ospf database external {prefix}')
    elif protocol == 'B':
        get_detials = send_command(f'show bgp {prefix}')

    return get_route, get_detials


def clear_counters(interface):
    """Clears interface counters"""

    send_command(f"clear counters {interface}", expect_string="[confirm]")
    send_command("\n", expect_string="#")
    refresh_interfaces = Netconf.get_ip_interfaces(netconf_session)


def clear_arp():
    """Clears ARP table"""

    send_command('clear arp')
    send_command('clear arp-cache')
    get_arp()


def send_ping(session_obj, user, pwd, host, destination, source, count, vrf=None):
    """Send ping to device"""

    global device, session, username, password

    username = user
    password = pwd
    device = host
    session = session_obj

    if vrf is None:
        pings = send_command(f'ping {destination} source {source} repeat {count}')
    else:
        pings = send_command(f'ping vrf {vrf} {destination} source {source} repeat {count}')

    return pings


def get_cdp_neighbors_detail(session_obj, port):
    """Gets mac and arp tables. Concatinates into one"""

    global session
    session = session_obj

    cdp_neighbors = send_command(f'show cdp neighbors {port} detail')

    return cdp_neighbors


def get_hsrp_detail(session_obj, interface):
    """Gets mac and arp tables. Concatinates into one"""

    global session
    session = session_obj

    hsrp_details = send_command(f'show standby {interface}')
    hsrp_neighbor = send_command(f'show standby neighbors {interface}')

    return hsrp_details, hsrp_neighbor


def get_span_detail(session_obj, vlan):
    """Gets mac and arp tables. Concatinates into one"""

    global session
    session = session_obj

    span_vlan = send_command(f'show spanning-tree vlan {vlan} ')

    return span_vlan

def get_router_lsas(session_obj, ip):
    """Gets mac and arp tables. Concatinates into one"""

    global session
    session = session_obj

    return send_command(f'show ip ospf database adv {ip} ')

def get_cdp_neighbors():
    """Gets mac and arp tables. Concatinates into one"""

    neighbors = []
    name = None
    local_port = None
    remote_port = None

    try:
        for neighbor in send_command('show cdp neighbors').splitlines():
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

        # Delete table data
        DbOps.delete_rows('cdp_front_end', device)
        for i in neighbors:
            db_session = DbOps.update_cdp_table(device, i['name'], i['local-port'], i['remote-port'])

    except AttributeError:
        pass


def get_hsrp_status():
    """Gets mac and arp tables. Concatinates into one"""

    # Delete table data
    DbOps.delete_rows('hsrp_front_end', device)

    try:
        for interface in send_command('show standby brief | ex Interface').splitlines():
            if len(interface.split()) == 0:
                continue
            else:
                try:
                    DbOps.update_hsrp_table(device, interface.split()[0], interface.split()[1],
                                            interface.split()[2], interface.split()[3], interface.split()[4],
                                            interface.split()[5], interface.split()[6], interface.split()[7])
                except IndexError:
                    pass
    except AttributeError:
        pass


def get_span_root():
    """Gets mac and arp tables. Concatinates into one"""

    # Delete table data
    DbOps.delete_rows('spanningtree_front_end', device)

    try:
        for vlan in send_command('show spanning-tree root | ex Vlan|-|Root').splitlines():

            if len(vlan.split()) == 0:
                continue
            elif len(vlan.split()) == 7:
                DbOps.update_spann_tree_table(device, vlan.split()[0].strip('VLAN'), vlan.split()[1],
                                              vlan.split()[2], vlan.split()[3], '')
            elif len(vlan.split()) == 8:
                DbOps.update_spann_tree_table(device, vlan.split()[0].strip('VLAN'), vlan.split()[1],
                                              vlan.split()[2], vlan.split()[3], vlan.split()[7])
    except AttributeError:
        pass


def get_mac_arp_table():
    """Gets mac and arp tables. Concatinates into one"""

    mac_table = []
    arp_table = []

    # Delete table data
    DbOps.delete_rows('arpmac_front_end', device)

    try:
        for mac in send_command('show mac address-table | ex Vlan|All|Total|%|-').splitlines():

            try:
                mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                  'interface': mac.split()[3]})
            except IndexError:
                continue

        for arp in send_command('show ip arp | ex Protocol|Total|%').splitlines():
            try:
                arp_table.append(
                    {'protocol': arp.split()[0], 'ip': arp.split()[1], 'age': arp.split()[2], 'mac': arp.split()[3],
                     'interface': arp.split()[5]})
            except IndexError:
                continue

        # Check to see if mac has an arp entry. If so, add k/v to existing dictionary
        if mac_table:
            for mac in mac_table:
                for entry in arp_table:
                    if mac.get('address') == entry.get('mac'):
                        mac['ip'] = entry.get('ip')
                        mac['ip_int'] = entry.get('interface')
                        break
                    else:
                        mac['ip'] = 'None'
                        mac['ip_int'] = 'None'

        if mac_table:
            for i in mac_table:
                DbOps.update_mac_arp_table(device, i['vlan'], i['address'], i['type'], i['interface'], i.get('ip'),
                                           i.get('ip_int'))
    except AttributeError:
        pass


def get_vlans():
    """Get vlans"""

    # Deletes table data
    DbOps.delete_rows('vlans_front_end', device)

    try:
        for vlan in send_command('show vlan brief').splitlines():
            if len(vlan.split()) == 0:
                continue
            elif vlan.split()[0] == '^':
                break
            elif vlan.split()[0] == 'VLAN':
                continue
            elif vlan.split()[0] == '----':
                continue

            # Get vlan ports
            if vlan.split()[0].rfind("/") != -1:
                vlan_ports = ' '.join(vlan.split())
            else:
                vlan_ports = ' '.join(vlan.split()[3:])

            # Compare vlan id (show vlan) to vlan priority. Use indexing since vlan prio is VLAN + 4 ints, 0000
            for prio in send_command('show spanning-tree bridge priority').splitlines():
                if len(prio.split()) == 0:
                    continue
                elif vlan.split()[0] == prio.split()[0][5:]:
                    DbOps.update_vlan_table(device, vlan.split()[0], prio.split()[1],
                                            vlan.split()[1], vlan.split()[2], vlan_ports)
                    break
                elif vlan.split()[0] == prio.split()[0][6:]:
                    DbOps.update_vlan_table(device, vlan.split()[0], prio.split()[1],
                                            vlan.split()[1], vlan.split()[2], vlan_ports)
                    break
                elif vlan.split()[0] == prio.split()[0][7]:
                    DbOps.update_vlan_table(device, vlan.split()[0], prio.split()[1],
                                            vlan.split()[1], vlan.split()[2], vlan_ports)
                    break
                else:
                    DbOps.update_vlan_table(device, vlan.split()[0], 'N/A',
                                            vlan.split()[1], vlan.split()[2], vlan_ports)
                    break

    except AttributeError:
        pass


def get_access_ports():
    """Get trunks"""

    # Deletes table data
    DbOps.delete_rows('accessInterfaces_front_end', device)

    try:
        for line in send_command('show interfaces status | ex Port').splitlines():
            if len(line.split()) == 0:
                continue
            elif line.split()[0] == '^':
                break
            else:
                if len(line.split()) == 7:
                    DbOps.update_access_interfaces_table(device, line.split()[0], line.split()[1], line.split()[2],
                                                         line.split()[3],
                                                         line.split()[4], line.split()[5])
                elif len(line.split()) == 6:
                    DbOps.update_access_interfaces_table(device, line.split()[0], 'N/A', line.split()[1],
                                                         line.split()[2],
                                                         line.split()[4], line.split()[5])
                elif len(line.split()) == 5:
                    DbOps.update_access_interfaces_table(device, line.split()[0], 'N/A', line.split()[1],
                                                         line.split()[2],
                                                         line.split()[4], 'N/A')
    except AttributeError:
        pass


def get_route_maps():
    """Get route-map names"""

    map_name = None

    # Deletes table data
    DbOps.delete_rows('routeMaps_front_end', device)

    try:
        for line in send_command('show route-map | i route-map').splitlines():
            if not list(enumerate(line.split(), 0)):
                continue
            elif line.split()[0] == '^':
                break
            elif line.split()[1] != map_name:
                DbOps.update_route_maps(device, line.split()[1])

            map_name = line.split()[1]
    except AttributeError:
        pass


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

    return access_ports


def get_ospf_routers():
    """Gets mac and arp tables. Concatinates into one"""

    process, router_id = None, None

    # Delete table data
    DbOps.delete_rows('ospfrouters_front_end', device)

    try:
        for line in send_command('show ip ospf border-routers | ex Codes|Internal|Base').splitlines():
            if len(line.split()) == 0:
                continue
            elif line.split()[0] == 'OSPF':
                router_id = line.split()[4].strip(')').strip('(')
                process = line.split()[7].strip(')')
            elif len(line.split()) == 11:
                DbOps.update_ospf_router_table(device, process, router_id, line.split()[1], line.split()[0],
                                               line.split()[2].strip(']').strip('['), line.split()[4].strip(','),
                                               line.split()[5].strip(','),
                                               line.split()[6].strip(','),
                                               f'{line.split()[7]} {line.split()[8].strip(",")}', line.split()[10])
    except AttributeError:
        pass


def get_dmvpn():
    """Gets dmvpn peers, attributes, status, writes to DB"""

    interface, router_type = None, None

    # Delete table data
    DbOps.delete_rows('dmvpn_front_end', device)

    for line in send_command('show dmvpn | b Interface').splitlines():
        if len(line.split()) == 0 or '-' in line or '#' in line:
            continue
        elif len(line.split()) == 6:
            DbOps.update_dmvpn_table(device, line.split()[1], line.split()[2],
                                     line.split()[3], line.split()[4], line.split()[5])


def get_dmvpn_info():
    """Gets dmvpn peers, attributes, status, writes to DB"""

    interface = None
    # Delete table data
    DbOps.delete_rows('dmvpncount_front_end', device)

    for line in send_command('show dmvpn | i Interface|Type').splitlines():
        if len(line.split()) == 0:
            continue
        elif len(line.split()) == 5:
            interface = line.split()[1].strip(',')
            get_dmvpn_interface(session, interface, device)
        elif len(line.split()) == 3:
            router_type = line.split(':')[1].split(',')[0]
            peer_count = line.split()[2].strip('Peers:').strip(',')
            DbOps.update_dmvpn_count(device, interface, router_type, peer_count)


def start_polling(username, pwd, host, device_type, port):
    global device, session, password, ssh_port

    username = username
    password = pwd
    device = host
    ssh_port = port

    session = ConnectWith.creat_netmiko_connection(username, password, device, ssh_port)

    if device_type[:3][-2:] != 'SR':
        get_mac_arp_table()
        get_span_root()
        get_access_ports()
        get_vlans()

    elif device_type[:3][-2:] == 'SR':
        get_dmvpn()
        get_dmvpn_info()

    get_arp()
    get_cdp_neighbors()
    get_ospf_status()
    get_bgp_status()
    get_vrfs()
    get_ospf_processes()
    get_route_maps()
    get_hsrp_status()
    get_ospf_routers()

def indivisual_poll(user, pwd, host, port, polling, interface=None):
    global session, device

    username = user
    password = pwd
    device = host
    ssh_port = port
    session = ConnectWith.creat_netmiko_connection(username, password, device, ssh_port)

    if polling == 'arp':
        get_arp()
    elif polling == 'bgp':
        get_bgp_status()
    elif polling == 'ospf':
        get_ospf_status()
    elif polling == 'mac':
        get_mac_arp_table()
    elif polling == 'cdp':
        get_cdp_neighbors()
    elif polling == 'span':
        get_span_root()
    elif polling == 'access':
        get_access_ports()
    elif polling == 'clearInt':
        clear_counters(interface)
    elif polling == 'clearArp':
        clear_arp()
    elif polling == 'refreshArp':
        get_arp()
    elif polling == 'vlans':
        get_vlans()
    elif polling == 'trunk_helper':
        trunks = netconf_trunk_helper(interface)
        return trunks
    elif polling == 'hsrp':
        get_hsrp_status()
    elif polling == 'peer_count':
        get_dmvpn()
    elif polling == 'borderRouters':
        get_ospf_routers()