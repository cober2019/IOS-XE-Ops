"""Helper funtions for prefix list operations"""

import app.Modules.netconfsend as NetconfBase
from ncclient import manager
import xmltodict
import collections


def is_instance(list_or_dict):
    """Checks to if miltiple prefix-list are in the config. If one list is in the configuration, structure is dictionary
    If multiple list are in the config, structure will be a list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_seq_list(list_or_dict):
    """Checks to "seq" key is list or dictionary. If one seq is in the prefix-list, seq is a dictionary, if multiple seq,
    seq will be list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    elif isinstance(list_or_dict, dict):
        make_list = [list_or_dict]
    else:
        make_list = None

    return make_list


def is_permit_or_deny(sequence) -> str:
    """Gets key, permit or deny from prefix statement"""

    action = None
    if "permit" in sequence:
        action = "permit"
    elif "deny" in sequence:
        action = "deny"

    return action


def get_policies(netconf_session, policy_type) -> dict:
    """Gets current prefix-lists from device and converts from xml to dictionary"""

    if policy_type == 'route_map':
        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <route-map/>
                            </native>
                            </filter>"""

        try:
            config_info = netconf_session.get(xml_filter)
            read_response = NetconfBase.check_rpc_reply(str(config_info))

            if read_response == 'Empty Config':
                converted_config = ['No Route-maps']
            else:
                config_dict = xmltodict.parse(config_info.xml)["rpc-reply"]["data"]
                route_maps = config_dict.get("native", {}).get("route-map", {})
                converted_config = is_instance(route_maps)

        except manager.operations.errors.TimeoutExpiredError as error:
            converted_config = [error, 'Connection Timeout', 'error']
        except AttributeError as error:
            converted_config = [error, 'Session Expired', 'error']
        except manager.transport.TransportError as error:
            converted_config = [error, 'Transport Error', 'error']
        except manager.operations.rpc.RPCError as error:
            converted_config = [error, 'Configuration Failed', 'error']

    elif policy_type == 'prefix_list':

        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <ip>
                        <prefix-list/>
                        </ip>
                        </native>
                        </filter>"""

        try:
            config_info = netconf_session.get(xml_filter)
            read_response = NetconfBase.check_rpc_reply(str(config_info))

            if read_response == 'Empty Config':
                converted_config = ['No Prefix-lists']
            else:
                config_dict = xmltodict.parse(config_info.xml)["rpc-reply"]["data"]
                prefixes = config_dict.get("native").get("ip").get("prefix-list").get("prefixes")
                converted_config = is_instance(prefixes)

        except manager.operations.errors.TimeoutExpiredError as error:
            converted_config = [error, 'Connection Timeout', 'error']
        except AttributeError as error:
            converted_config = [error, 'Session Expired', 'error']
        except manager.transport.TransportError as error:
            converted_config = [error, 'Transport Error', 'error']
        except manager.operations.rpc.RPCError as error:
            converted_config = [error, 'Configuration Failed', 'error']

    elif policy_type == 'policy_map':

        xml_filter = """ <filter>
                          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                              <policy>
                                <policy-map xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-policy"/>
                              </policy>
                          </native>
                        </filter>"""

        try:
            config_info = netconf_session.get(xml_filter)
            read_response = NetconfBase.check_rpc_reply(str(config_info))

            if read_response == 'Empty Config':
                converted_config = ['No Policy-Maps']
            else:
                config_dict = xmltodict.parse(config_info.xml)["rpc-reply"]["data"]
                prefixes = config_dict.get("native").get("policy").get("policy-map")
                converted_config = is_instance(prefixes)

        except manager.operations.errors.TimeoutExpiredError as error:
            converted_config = [error, 'Connection Timeout', 'error']
        except AttributeError as error:
            converted_config = [error, 'Session Expired', 'error']
        except manager.transport.TransportError as error:
            converted_config = [error, 'Transport Error', 'error']
        except manager.operations.rpc.RPCError as error:
            converted_config = [error, 'Configuration Failed', 'error']

    return converted_config


def fetch_prefix_list(netconf_session) -> dict:
    """View current prefix-list, match statemnt combinations."""

    prefix_dict = collections.defaultdict(list)
    prefix_lists = get_policies(netconf_session, 'prefix_list')

    if prefix_lists[0] == 'No Prefix-lists':
        pass
    else:
        for prefix_list in prefix_lists:
            lists = is_instance(prefix_list.get("seq", {}))
            for sequence in lists:
                prefix_dict[prefix_list.get("name")].append({'seq': sequence.get("no"), 'action': sequence.get("action"),
                                                             'ip': sequence.get("no"), 'ge': sequence.get("ge", ''),
                                                             'le': sequence.get("le")})

    return prefix_dict


def fetch_route_maps(netconf_session):
    """View current prefix-list, match statemnt combinations."""

    route_map_dict = collections.defaultdict(list)
    route_maps = get_policies(netconf_session, 'route_map')

    if route_maps[0] == 'No Route-maps':
        pass
    else:
        for route_map in route_maps:
            lists = is_instance(route_map.get("route-map-without-order-seq"))
            for sequence in lists:
                route_map_dict[route_map.get('name')].append(
                    {'seq': sequence.get("seq_no"),
                     'Action': sequence.get("operation"),
                     'IP': sequence.get("match").get('ip', {}).get('address', {}).get('prefix-list', {}),
                     'AS_PATH': sequence.get("match").get('as-path', {}).get('access-list', {})})

    return route_map_dict


def fetch_service_policy(netconf_session):
    """View current prefix-list, match statemnt combinations."""

    policy_map_list = []
    policy_maps = get_policies(netconf_session, 'policy_map')

    if policy_maps[0] == 'No Policy-Maps':
        pass
    else:
        for policy_map in policy_maps:
            try:
                policy_map_list.append(policy_map.get("name", {}))
            except AttributeError:
                pass

    return policy_map_list
