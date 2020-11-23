"""Helper funtions to view IETF interface qos and statistics"""

from ncclient import manager
import xmltodict
import collections
import app.Modules.netconfsend as NetconfBase

all_ints = f"""<filter>
           <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
           <interface>
           </interface>
           </interfaces-state>
           </filter>"""


# ------------------------ pre-deployements funtions -----------------------


def is_instance(list_or_dict) -> list:
    """convert anything not a list to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def get_interfaces(session):
    """Gets one interface with policies, queues, and stats"""

    policies = collections.defaultdict(list)

    int_stats = f"""<filter>
                  <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
                  </filter>"""

    # Create NETCONF Session, get config

    try:
        get_state = session.get(int_stats)
        int_info = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]["interfaces-state"]["interface"]

        # Check to see if value us a list or dict, makes list if not. Helps cut down on code
        make_ints_lists = is_instance(int_info)
        # Check interface for policy application, skip if not applied
        for i in make_ints_lists:
            if i.get("diffserv-target-entry", {}).get("direction", {}):
                queues = collections.defaultdict(list)
                policy_detials = {'Policy_name': i.get('diffserv-target-entry', {}).get('policy-name', {}),
                                  'Direction': i.get('diffserv-target-entry', {}).get('direction', {})}
                policies[i['name']].append(policy_detials)
                for index, stat in enumerate(i.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {})):
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

    except manager.operations.errors.TimeoutExpiredError as error:
        policies = [error, 'Connection Timeout', 'error']
    except AttributeError as error:
        policies = [error, 'Session Expired', 'error']
    except manager.transport.TransportError as error:
        policies = [error, 'Transport Error', 'error']
    except manager.operations.rpc.RPCError as error:
        policies = [error, 'Configuration Failed', 'error']

    return policies

