"""Helper funtion to retrieve interface statisitics/configurations"""

from ncclient import manager
import xmltodict
import ipaddress
import app.Database.DbOperations as DbOps
import app.base.routes as Credentials
import app.Modules.connection as ConnectWith
import app.Modules.GetWithNetmiko as GetWithNetmiko
import collections
import time

interface_state = None
interface_types = ("GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "TenGigabitEthernet",
                   "Port-channel-subinterface")

trunk_types = ("GigabitEthernet", "TenGigabitEthernet")

username = None
password = None
device = None
device_type = None
netconf_port = 830
session = None


# ------------------------ pre-deployements funtions -----------------------


def is_instance(list_or_dict):
    """"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_in_list(list_or_dict):
    """y"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def get_prefix_config():
    config = None
    xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    <ip>
                    <prefix-list/>
                    </ip>
                    </native>
                    </filter>"""

    try:
        get_prefix = session.get(xml_filter)
        parsed = xmltodict.parse(get_prefix.xml)["rpc-reply"]["data"]
        prefixes = parsed.get("native").get("ip").get("prefix-list").get("prefixes")
        config = is_instance(prefixes)
    except manager.operations.errors.TimeoutExpiredError as error:
        converted_config = 'error'
    except AttributeError as error:
        converted_config = 'error'
    except manager.transport.TransportError as error:
        converted_config = 'error'
    except manager.operations.rpc.RPCError as error:
        converted_config = 'error'

    return config


def get_config():
    """Gets interfaces configurations"""

    try:
        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <interface/>
                        </native>
                        </filter>"""

        intf_info = session.get(xml_filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
        converted_config = is_instance(intf_dict)

    except manager.operations.errors.TimeoutExpiredError as error:
        converted_config = 'error'
    except AttributeError as error:
        converted_config = 'error'
    except manager.transport.TransportError as error:
        converted_config = 'error'
    except manager.operations.rpc.RPCError as error:
        converted_config = 'error'

    return converted_config


def get_stats(interface=None):

    global interface_state

    if interface is not None:

        xml_filter = f"""<filter>
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                        <interface>
                        <name>{interface}</name>
                        </interface>
                        </interfaces-state>
                        </filter>"""
    else:

        xml_filter = f"""<filter>
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                        <interface>
                        </interface>
                        </interfaces-state>
                        </filter>"""

    try:
        get_state = session.get(xml_filter)
        int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
        interface_state = int_status["interfaces-state"]["interface"]
    except manager.operations.errors.TimeoutExpiredError:
        pass
    except AttributeError:
        pass
    except manager.transport.TransportError:
        pass
    except manager.operations.rpc.RPCError:
        pass

    return interface_state


def get_interface_stats(select_int, ip=None):
    """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
    Returns information to the caller"""

    interface_stats = {}

    interface = get_stats(select_int)

    speed_conversion = int(int(interface.get("speed")) / 1e+6)
    interface_stats[select_int] = {'IP': ip, "Admin": interface.get("admin-status"),
                                   "Operational": interface.get("oper-status"),
                                   "Speed": speed_conversion,
                                   "Last Change": interface.get("last-change"),
                                   "MAC": interface.get("phys-address"),
                                   "In Octets": interface.get("statistics")["in-octets"],
                                   "In Unicast": interface.get("statistics")["in-unicast-pkts"],
                                   "In Multicast": interface.get("statistics")[
                                       "in-multicast-pkts"],
                                   "In Discards": interface.get("statistics")["in-discards"],
                                   "In Errors": interface.get("statistics")["in-errors"],
                                   "Protocol Drops": interface.get("statistics")[
                                       "in-unknown-protos"],
                                   "Out Octets": interface.get("statistics")["in-octets"],
                                   "Out Unicast": interface.get("statistics")[
                                       "in-unicast-pkts"],
                                   "Out Multicast": interface.get("statistics")[
                                       "in-multicast-pkts"],
                                   "Out Discards": interface.get("statistics")["in-discards"],
                                   "Out Errors": interface.get("statistics")["in-errors"],
                                   "Out Boradcast": interface.get("statistics")[
                                       "out-broadcast-pkts"]}

    return interface_stats


def get_ip_interfaces(management_ip=None):
    """Gets interface ips addresses"""

    interface_info = []
    unassigned_interfaces = ['Tunnel', 'Loopback', 'Vlan']
    interface_num = []

    for ints in interface_types:
        try:
            current_interfaces = get_config()[0]["native"]["interface"].get(ints)
            # If data structure is a dict. This funtion with convert to a list. Dictionaries occur when there is one of something returned
            make_ip_list = is_in_list(current_interfaces)
            for ip in make_ip_list:
                if ip is None:
                    pass
                elif ip.get("ip", {}).get("address", {}):
                    address = ipaddress.ip_interface(
                        ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get(
                            'address').get('primary').get('mask'))

                    parsed_info = get_interface_stats(ints + ip.get('name'), ip=address)
                    interface_info.append(parsed_info)

                    if ip.get('ip', '').get('address').get('primary').get('address') == management_ip:
                        nuclear_int = ints + ip.get('name')
                else:
                    try:
                        parsed_info = get_interface_stats(ints + ip.get('name'), ip='Not Assigned')
                        interface_info.append(parsed_info)
                    except TypeError:
                        pass

                    try:
                        unassigned_interfaces.append(ints + ip.get('name'))
                        interface_num.append(ip.get('name'))
                    except TypeError:
                        pass
        except TypeError:
            pass

    # Deletes table data
    DbOps.delete_rows('Interfaces_front_end', device)
    for i in interface_info:
        for k, v in i.items():
            DbOps.update_ip_interface_table(device, k, str(v['IP']) + ' | ' + v['MAC'], v['Admin'], v['Operational'],
                                            v['Speed'],
                                            v['Last Change'].split('.')[0], v['In Octets'], v['Out Octets'])
    # Deletes table data
    DbOps.delete_rows('UnassignedInterfaces_front_end', device)
    # Write unassigned interfaces to the DB
    for interface in unassigned_interfaces:
        DbOps.update_unassigned_interfaces(device, interface)


def get_trunk_ports(ssh_port, username, password, device):
    """Get trunk ports. Uses NETCONF and Netmiko """

    trunks = []

    # Deletes table data
    DbOps.delete_rows('Trunks_front_end', device)

    for ints in interface_types:
        try:
            current_interfaces = get_config()[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    continue

                if interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {}):
                    # Use netconf interface name to get vlans using netmiko. I find netconf can be untrustworthy sometimes
                    vlans = GetWithNetmiko.indivisual_poll(username, password, device, ssh_port, 'trunk_helper',
                                                           interface=ints + interface.get('name'))
                    # Write dictionary to list and join our vlan list returned from netmiko funtion
                    trunks.append({'interface': ints + interface.get('name'), 'vlans': ', '.join(vlans),
                                   'cdp': interface.get('name')})

                elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
                    # Use netconf interface name to get vlans using netmiko. I find netconf can be untrustworthy sometimes
                    vlans = GetWithNetmiko.indivisual_poll(username, password, device, ssh_port, 'trunk_helper',
                                                           interface=ints + interface.get('name'))
                    # Write dictionary to list and join our vlan list returned from netmiko funtion
                    trunks.append({'interface': ints + interface.get('name'), 'vlans': ', '.join(vlans),
                                   'cdp': interface.get('name')})
        except TypeError:
            pass

    # Iterate through trunk list and interface state. Comapre interface banes and get interface state. Write to database
    for interface in trunks:
        for port in get_stats():
            if interface.get('interface') == port.get('name'):
                DbOps.update_trunks_table(device, interface['interface'], interface['vlans'],
                                          port.get('admin-status'), port.get('oper-status'))


def get_port_channels():
    """Get port-channels"""

    port_channels = []

    # Deletes table data
    DbOps.delete_rows('PoChannels_front_end', device)

    for ints in trunk_types:
        print(ints)
        try:
            # If data structure is a dict. This funtion with convert to a list. Dictionaries occur when there is one of something returned
            make_list = is_in_list(get_config()[0]["native"]["interface"].get(ints))
            print(make_list)
            for interface in make_list:
                print(interface)
                if interface is None:
                    continue
                elif interface.get("channel-group", {}).get("number", {}):
                    port_channels.append({'interface': ints + interface.get("name"),
                                          'group': interface.get('channel-group').get('number'),
                                          'mode': interface.get('channel-group').get('mode')})
        except TypeError:
            pass

    # Iterate through trunk list and interface state. Comapre interface banes and get interface state. Write to database
    for interface in port_channels:
        for port in get_stats():
            if interface.get('interface') == port.get('name'):
                DbOps.update_pochannel_table(device, interface['interface'], interface['group'],
                                             interface['mode'],
                                             port.get('admin-status'), port.get('oper-status'))


def get_qos_interfaces():
    """Gets one interface with policies, queues, and stats"""

    policies = collections.defaultdict(list)

    # Deletes table data
    DbOps.delete_rows('InterfaceQos_front_end', device)
    make_ints_lists = is_instance(get_stats())

    for i in make_ints_lists:
        if i.get("diffserv-target-entry", {}).get("direction", {}):
            queues = collections.defaultdict(list)
            policy_detials = {'Policy_name': i.get('diffserv-target-entry', {}).get('policy-name', {}),
                              'Direction': i.get('diffserv-target-entry', {}).get('direction', {})}
            policies[i['name']].append(policy_detials)
            for index, stat in enumerate(
                    i.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {})):
                # Creates list and resets at each iteration
                queue = {'queue_name': stat.get('classifier-entry-name', {}),
                         'rate': stat.get("classifier-entry-statistics", {}).get("classified-rate", {}),
                         'bytes': stat.get('classifier-entry-statistics', {}).get('classified-bytes', {}),
                         'packets': stat.get('classifier-entry-statistics', {}).get('classified-pkts', {}),
                         'out_bytes': stat.get('queuing-statistics', {}).get('output-bytes', {}),
                         'out_packets': stat.get('queuing-statistics', {}).get('output-pkts', {}),
                         'drop_packets': stat.get('queuing-statistics', {}).get('drop-pkts', {}),
                         'drop_bytes': stat.get('queuing-statistics', {}).get('drop-bytes', {}),
                         'wred_drops_pkts': stat.get('queuing-statistics', {}).get('wred-stats', {}).get(
                             'early-drop-pkts', {}),
                         'wred_drop_bytes': stat.get('queuing-statistics', {}).get('wred-stats', {}).get(
                             'early-drop-bytes', {})}
                # Write dictionary values to list, add string formatting
                # Write list as value to key which is our policy name
                queues['queues'].append(queue)
                policies[i['name']].append(queues)

    # Read policy dictionaries and write to database
    for k, v in policies.items():
        for stat in v[1]['queues']:
            DbOps.update_qos_table(device, k, v[0]['Policy_name'], v[0]['Direction'], stat['queue_name'],
                                                stat['rate'], stat['bytes'], stat['packets'], stat['out_bytes'],
                                                stat['out_packets'],
                                                stat['drop_packets'], stat['drop_bytes'], stat['wred_drops_pkts'],
                                                stat['wred_drop_bytes'])


def get_qos_interfaces():
    """Gets QOS configurations"""

    # Deletes table data
    DbOps.delete_rows('InterfaceQos_front_end', device)
    make_ints_lists = is_instance(get_stats())

    for i in make_ints_lists:
        if i.get("diffserv-target-entry", {}).get("direction", {}):
            for index, stat in enumerate(
                    i.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {})):
                DbOps.update_qos_table(device, i['name'], i.get('diffserv-target-entry', {}).get('policy-name', {}),
                                       i.get('diffserv-target-entry', {}).get('direction', {}),
                                       stat.get('classifier-entry-name', {}),
                                       stat.get("classifier-entry-statistics", {}).get("classified-rate", {}),
                                       stat.get('classifier-entry-statistics', {}).get('classified-bytes', {}),
                                       stat.get('classifier-entry-statistics', {}).get('classified-pkts', {}),
                                       stat.get('queuing-statistics', {}).get('output-bytes', {}),
                                       stat.get('queuing-statistics', {}).get('output-pkts', {}),
                                       stat.get('queuing-statistics', {}).get('drop-pkts', {}),
                                       stat.get('queuing-statistics', {}).get('drop-bytes', {}),
                                       stat.get('queuing-statistics', {}).get('wred-stats', {}).get(
                                           'early-drop-pkts', {}),
                                       stat.get('queuing-statistics', {}).get('wred-stats', {}).get(
                                           'early-drop-bytes', {}))


def get_prefix_lists():
    """View current prefix-list, match statemnt combinations."""

    # Deletes table data
    DbOps.delete_rows('PrefixList_front_end', device)
    prefix_lists = get_prefix_config()

    try:
        for prefix_list in prefix_lists:
            lists = is_instance(prefix_list.get("seq", {}))
            for sequence in lists:
                DbOps.update_prefix_table(device, prefix_list.get("name"), sequence.get("no"), sequence.get("action"),
                                          sequence.get("ge", ''), sequence.get("le"))
    except AttributeError:
        pass

def start_polling(username, password, host, device_type, port, ssh_port):

    global device, session, netconf_port

    username = username
    password = password
    device = host
    netconf_port = port

    session = ConnectWith.create_netconf_connection(username, password, device, netconf_port)

    # Check for device type. Insures polling only happens with compatable technologies
    if device_type[:3][-2:] != 'SR':
        get_trunk_ports(ssh_port, username, password, device)

    get_port_channels()
    get_ip_interfaces()
    get_prefix_lists()


def indivisual_poll(user, pwd, host, port, polling, ssh_port=None):

    global device, session, netconf_port

    username = user
    password = pwd
    device = host
    netconf_port = port

    session = ConnectWith.create_netconf_connection(username, password, device,
                                                    netconf_port)

    if session == 'error':
        pass
    elif polling == 'access':
        get_access_ports()
    elif polling == 'portchannel':
        get_port_channels()
    elif polling == 'trunks':
        get_trunk_ports(ssh_port, username, password, device)
    elif polling == 'interfaces':
        get_ip_interfaces()

