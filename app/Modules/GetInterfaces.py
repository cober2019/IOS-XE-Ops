"""Helper funtion to retrieve interface statisitics/configurations"""

from ncclient import manager
import xmltodict
import ipaddress

converted_config = None
interface_types = ("GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "TenGigabitEthernet",
                   "Port-channel-subinterface")


# ------------------------ pre-deployements funtions -----------------------


def is_instance(list_or_dict):
    """Checks to if miltiple prefix-list are in the config. If one list is in the configuration, structure is dictionary
    If multiple list are in the config, structure will be a list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_in_list(list_or_dict):
    """Checks to "seq" key is list or dictionary. If one seq is in the prefix-list, seq is a dictionary, if multiple seq,
    seq will be list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def get_config(netconf_session):
    """Gets interfaces configurations"""

    try:
        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <interface/>
                        </native>
                        </filter>"""

        intf_info = netconf_session.get(xml_filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
        converted_config = is_instance(intf_dict)

    except manager.operations.errors.TimeoutExpiredError as error:
        converted_config = [error, 'Connection Timeout', 'error']
    except AttributeError as error:
        converted_config = [error, 'Session Expired', 'error']
    except manager.transport.TransportError as error:
        converted_config = [error, 'Transport Error', 'error']
    except manager.operations.rpc.RPCError as error:
        converted_config = [error, 'Configuration Failed', 'error']

    return converted_config


def get_stats(netconf_session, interface=None):

    global converted_config

    try:
        int_stats = f"""<filter>
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                        <interface>"""

        if interface is not None:

            filter = int_stats + f"""<name>{interface}</name>
                            </interface>
                            </interfaces-state>
                            </filter>"""
        else:

            filter = int_stats + """ </interface>
                            </interfaces-state>
                            </filter>"""

        get_state = netconf_session.get(filter)
        int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
        converted_config = int_status["interfaces-state"]["interface"]

    except manager.operations.errors.TimeoutExpiredError as error:
        converted_config = ['error', 'Connection Timeout',error]
    except AttributeError as error:
        converted_config = ['error', 'Session Expired', error]
    except manager.transport.TransportError as error:
        converted_config = ['error', 'Transport Error', error]
    except manager.operations.rpc.RPCError as error:
        converted_config = ['error', 'Configuration Failed', error]

    return converted_config


# ^^^^^^^^^^^^^^^^^^^^ End pre-deployements funtions ^^^^^^^^^^^^^^^^^^^^

# User Funtions------------------------------------------------------------


def get_interface_stats(select_int, netconf_session, ip=None):
    """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
    Returns information to the caller"""

    interface_stats = {}

    interface = get_stats(netconf_session, select_int)

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


def get_ip_interfaces(session, management_ip=None):
    """Gets interface ips addresses"""

    interface_info = []
    unassigned_interfaces = ['Tunnel', 'Loopback', 'Vlan']
    interface_num = []
    nuclear_int = None

    ip_config = get_config(session)
    for ints in interface_types:
        current_interfaces = ip_config[0]["native"]["interface"].get(ints)
        make_ip_list = is_in_list(current_interfaces)
        for ip in make_ip_list:
            if ip is None:
                pass
            elif ip.get("ip", {}).get("address", {}):
                address = ipaddress.ip_interface(ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get('address').get('primary').get('mask'))
                parsed_info = get_interface_stats(ints + ip.get('name'), session, ip=address)
                interface_info.append(parsed_info)
                if ip.get('ip', '').get('address').get('primary').get('address') == management_ip:
                    nuclear_int = ints + ip.get('name')
            else:
                try:
                    parsed_info = get_interface_stats(ints + ip.get('name'), session)
                    interface_info.append(parsed_info)
                except TypeError:
                    pass

                try:
                    unassigned_interfaces.append(ints + ip.get('name'))
                    interface_num.append(ip.get('name'))
                except TypeError:
                    pass

    return interface_info, nuclear_int, unassigned_interfaces, interface_num


def get_single_interfaces(session, interface):
    """Gets interface ips addresses"""

    interface_info = []
    ip_config = get_config(session)

    for ints in interface_types:
        current_interfaces = ip_config[0]["native"]["interface"].get(ints)
        make_ip_list = is_in_list(current_interfaces)
        for ip in make_ip_list:
            try:
                if interface == ints + ip.get('name'):
                    if ip is None:
                        pass
                    elif ip.get("ip", {}).get("address", {}):
                        address = ipaddress.ip_interface(ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get(
                                'address').get('primary').get('mask'))
                        parsed_info = get_interface_stats(ints + ip.get('name'), session, ip=address)
                        interface_info.append(parsed_info)
                    else:
                        try:
                            parsed_info = get_interface_stats(ints + ip.get('name'), session)
                            interface_info.append(parsed_info)
                        except TypeError:
                            pass
            except (AttributeError, TypeError):
                continue

    return interface_info


def get_trunk_ports(session, interface=None) -> list:
    """Compile access ports"""

    trunks = []

    config = get_config(session)
    interface_state = get_stats(session)

    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            # Gets trunk vlans
            elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans",
                                                                                                         {}):
                trunks.append({'interface': ints + interface.get('name'),
                               'vlans': interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get(
                                   'vlan',
                                   {}).get(
                                   'vlans', {}),
                               'cdp': interface.get('name')})
            # Gets trunk vlans with add key
            elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
                trunks.append({'interface': ints + interface.get('name'),
                               'vlans': interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get(
                                   'vlan',
                                   {}).get(
                                   'add', {}),
                               'cdp': interface.get('name')})

    for int in trunks:
        for port in converted_config:
            if int.get('interface') == port.get('name'):
                int['admin'] = port.get('admin-status')
                int['oper'] = port.get('oper-status')

    return trunks


def get_port_channels(session) -> list:
    
    port_channels = []

    config = get_config(session)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get("channel-group", {}).get("number", {}):
                port_channels.append({'interface': ints + interface.get("name"),
                                      'group': interface.get('channel-group').get('number'),
                                      'mode': interface.get('channel-group').get('mode')})

    for int in port_channels:
        for port in converted_config:
            if int.get('interface') == port.get('name'):
                int['admin'] = port.get('admin-status')
                int['oper'] = port.get('oper-status')

    return port_channels


def get_int_up_down(session) -> None:
    """Get interface up/down"""

    config = get_config(session)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get('shutdown', {}) is None:
                print(f'{ints} {interface.get("name")} is down')
            else:
                print(f'{ints} {interface.get("name")} is up')


def get_access_ports(session) -> list:
    """Compile access ports"""

    access_ports = []

    config = get_config(session)
    interface_state = get_stats(session)

    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get("switchport", {}).get("access", {}).get("vlan", {}).get("vlan", {}):
                access_ports.append({'port': ints + interface.get('name'),
                                     'vlan': interface.get('switchport', {}).get('access', {}).get('vlan', {}).get(
                                         'vlan', {})})
            elif interface.get("switchport", {}).get("mode", {}).get("access", {}) is None:
                access_ports.append({'port': ints + interface.get('name'), 'vlan': 'Native'})

    for int in access_ports:
        print(int)
        for port in interface_state:
            print(port)
            try:
                if int.get('port') == port.get('name'):
                    int['admin'] = port.get('admin-status')
                    int['oper'] = port.get('oper-status')
            except AttributeError:
                pass

    print(access_ports)
    return access_ports


