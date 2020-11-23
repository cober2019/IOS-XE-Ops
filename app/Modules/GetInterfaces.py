"""Helper funtion to retrieve interface statisitics/configurations"""

from ncclient import manager
import xmltodict
import ipaddress

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


def get_stats(netconf_session):

    print(netconf_session)
    try:
        int_stats = f"""<filter>
                   <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
                   </filter>"""

        get_state = netconf_session.get(int_stats)
        int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
        int_info = int_status["interfaces-state"]["interface"]
        converted_config = is_instance(int_info)

    except manager.operations.errors.TimeoutExpiredError as error:
        converted_config = [error, 'Connection Timeout', 'error']
    except AttributeError as error:
        converted_config = [error, 'Session Expired', 'error']
    except manager.transport.TransportError as error:
        converted_config = [error, 'Transport Error', 'error']
    except manager.operations.rpc.RPCError as error:
        converted_config = [error, 'Configuration Failed', 'error']

    return converted_config


# ^^^^^^^^^^^^^^^^^^^^ End pre-deployements funtions ^^^^^^^^^^^^^^^^^^^^

# User Funtions------------------------------------------------------------


def get_interface_stats(select_int, ip, netconf_session):
    """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
    Returns information to the caller"""

    interface_stats = {}

    print(netconf_session)
    config = get_stats(netconf_session)
    make_list = is_in_list(config)

    try:
        for interface in make_list:
            if interface.get("name") == select_int:
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
    except manager.operations.errors.TimeoutExpiredError as error:
        interface_stats = [error, 'Connection Timeout', 'error']
    except AttributeError as error:
        interface_stats = [error, 'Session Expired', 'error']
    except manager.transport.TransportError as error:
        interface_stats = [error, 'Transport Error', 'error']
    except manager.operations.rpc.RPCError as error:
        interface_stats = [error, 'Configuration Failed', 'error']

    return interface_stats


def get_ip_interfaces(session) -> list:
    """Gets interface ips addresses"""

    interface_info = []

    ip_config = get_config(session)
    for ints in interface_types:
        current_interfaces = ip_config[0]["native"]["interface"].get(ints)
        make_ip_list = is_in_list(current_interfaces)
        for ip in make_ip_list:
            if ip is None:
                pass
            elif ip.get("ip", {}).get("address", {}):
                address = ipaddress.ip_interface(ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get('address').get('primary').get('mask'))
                parsed_info = get_interface_stats(ints + ip.get('name'), address, session)
                interface_info.append(parsed_info)

    return interface_info

