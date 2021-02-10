"""Helper class which collect and call to database for writing"""

from ncclient import manager
import xmltodict
import ipaddress
import XEOpsDatabase.DbOperations as DbOps
import XEOpsDatabase.connection as ConnectWith
import time
import collections


def is_instance(list_or_dict):
    """"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_in_list(list_or_dict):
    """"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


class PollWitNetconf:
    """Collect device data using NETCONF"""

    def __init__(self):

        self.device = None
        self.username = None
        self.password = None
        self.netconf_port = 830
        self.session = None
        self.interface_types = ("GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "TenGigabitEthernet",
                                "Port-channel-subinterface")
        # Calling polling method
        self.start_polling()

    def start_polling(self):

        while True:
            # Query facts table in DB and get host IP
            for i in DbOps.session.query(DbOps.DeviceFacts).all():
                # Gets host credentials and IP
                self.username = i.username
                self.password = i.password
                self.device = i.unique_id
                # Creats session with DB row attributes
                self.session = ConnectWith.create_netconf_connection(self.username, self.password, self.device,
                                                                     self.netconf_port)
                # Call methods which collects data from device
                self.get_trunk_ports()
                self.get_port_channels()
                self.get_access_ports()
                self.get_ip_interfaces()

                # Sleep before next poll
                time.sleep(10)

    def get_stats(self, interface=None):

        config = None

        try:
            int_stats = f"""<filter>
                            <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                            <interface>"""

            if interface is not None:

                xml_filter = int_stats + f"""<name>{interface}</name>
                                </interface>
                                </interfaces-state>
                                </filter>"""
            else:

                xml_filter = int_stats + """ </interface>
                                </interfaces-state>
                                </filter>"""

            get_state = self.session.get(xml_filter)
            int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
            config = int_status["interfaces-state"]["interface"]

        except manager.operations.errors.TimeoutExpiredError:
            pass
        except AttributeError:
            pass
        except manager.transport.TransportError:
            pass
        except manager.operations.rpc.RPCError:
            pass

        return config

    def get_config(self):
        """Get interface config using NCClient"""

        config = None

        try:
            xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <interface/>
                            </native>
                            </filter>"""

            intf_info = self.session.get(xml_filter)
            intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
            config = is_instance(intf_dict)

        except manager.operations.errors.TimeoutExpiredError:
            pass
        except AttributeError:
            pass
        except manager.transport.TransportError:
            pass
        except manager.operations.rpc.RPCError:
            pass

        return config

    def get_interface_stats(self, select_int, ip=None):
        """Collect interface statistics"""

        interface_stats = {}
        interface = self.get_stats(select_int)

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

    def get_ip_interfaces(self):
        """Gets interface ips addresses"""

        interface_info = []
        unassigned_interfaces = ['Tunnel', 'Loopback', 'Vlan']
        interface_num = []

        ip_config = self.get_config()

        for ints in self.interface_types:
            current_interfaces = ip_config[0]["native"]["interface"].get(ints)
            make_ip_list = is_in_list(current_interfaces)
            for ip in make_ip_list:
                if ip is None:
                    pass
                elif ip.get("ip", {}).get("address", {}):
                    address = ipaddress.ip_interface(
                        ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get(
                            'address').get('primary').get('mask'))
                    parsed_info = self.get_interface_stats(ints + ip.get('name'), ip=address)
                    interface_info.append(parsed_info)
                else:
                    try:
                        parsed_info = self.get_interface_stats(ints + ip.get('name'), ip='Not Assigned')
                        interface_info.append(parsed_info)
                    except TypeError:
                        pass

                    try:
                        unassigned_interfaces.append(ints + ip.get('name'))
                        interface_num.append(ip.get('name'))
                    except TypeError:
                        pass

        for i in interface_info:
            for k, v in i.items():
                DbOps.update_ip_interface_table(self.device, k, str(v['IP']) + ' | ' + v['MAC'], v['Admin'],
                                                v['Operational'], v['Speed'],
                                                v['Last Change'].split('.')[0], v['In Octets'], v['Out Octets'])

        for interface in unassigned_interfaces:
            DbOps.update_unassigned_interfaces(self.device, interface)

    def get_trunk_ports(self):
        """Get access ports"""

        trunks = []
        config = self.get_config()
        interface_state = self.get_stats()

        for ints in self.interface_types:
            current_interfaces = config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans",
                                                                                                             {}):
                    trunks.append({'interface': ints + interface.get('name'), 'vlans': interface.get('switchport',
                                                                                                     {}).get('trunk',
                                                                                                             {}).get(
                        'allowed', {}).get('vlan', {}).get('vlans', {}),
                                   'cdp': interface.get('name')})

                elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
                    trunks.append({'interface': ints + interface.get('name'),
                                   'vlans': interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get(
                                       'vlan', {}).get('add', {}), 'cdp': interface.get('name')})
        for interface in trunks:
            for port in interface_state:
                if interface.get('interface') == port.get('name'):
                    DbOps.update_trunks_table(self.device, interface['interface'], interface['vlans'],
                                              port.get('admin-status'), port.get('oper-status'))

    def get_port_channels(self):
        """Get port-channels"""

        port_channels = []
        config = self.get_config()
        interface_state = self.get_stats()

        for ints in self.interface_types:
            current_interfaces = config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get("channel-group", {}).get("number", {}):
                    port_channels.append({'interface': ints + interface.get("name"),
                                          'group': interface.get('channel-group').get('number'),
                                          'mode': interface.get('channel-group').get('mode')})

        for interface in port_channels:
            for port in interface_state:
                if interface.get('interface') == port.get('name'):
                    DbOps.update_pochannel_table(self.device, interface['interface'], interface['group'],
                                                 interface['mode'],
                                                 port.get('admin-status'), port.get('oper-status'))

    def get_access_ports(self):
        """Get access ports"""

        access_ports = []

        config = self.get_config()
        interface_state = self.get_stats()

        for ints in self.interface_types:
            current_interfaces = config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get("switchport", {}).get("access", {}).get("vlan", {}).get("vlan", {}):
                    access_ports.append({'port': ints + interface.get('name'),
                                         'vlan': interface.get('switchport', {}).get('access', {}).get('vlan',
                                                                                                       {}).get(
                                             'vlan', {})})
                elif interface.get("switchport", {}).get("mode", {}).get("access", {}) is None:
                    access_ports.append({'port': ints + interface.get('name'), 'vlan': 'Native'})

        for interface in access_ports:
            for port in interface_state:
                try:
                    if interface.get('port') == port.get('name'):
                        DbOps.update_access_interfaces_table(self.device, interface['port'], interface['vlan'],
                                                             port.get('admin-status'),
                                                             port.get('oper-status'))
                except AttributeError:
                    pass

    def get_qos_interfaces(self):
        """Gets QOS configurations"""

        interface_state = self.get_stats()
        make_ints_lists = is_instance(interface_state)

        for i in make_ints_lists:
            if i.get("diffserv-target-entry", {}).get("direction", {}):
                for index, stat in enumerate(i.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {})):
                    DbOps.update_qos_table(self.device, i['name'], i.get('diffserv-target-entry', {}).get('policy-name', {}),
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
