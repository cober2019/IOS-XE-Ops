"""Helper class which collect and call to database for writing"""

from ncclient import manager
import xmltodict
import ipaddress
import DbOperations as DbOps
import GetWithNetmiko as GetWithNetmiko
import connection as ConnectWith


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

    def __init__(self, device, username, password, netconf_port, model):

        self.device = device
        self.username = username
        self.password = password
        self.netconf_port = netconf_port
        self.model = model
        self.session = None
        self.interface_state = None
        self.config = None
        self.interface_types = ("GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "TenGigabitEthernet",
                                "Port-channel-subinterface")
        self.trunk_types = ("GigabitEthernet", "TenGigabitEthernet")
        # Calling polling method
        self.start_polling()

    def start_polling(self):

        # Creats session with DB row attributes
        self.session = ConnectWith.create_netconf_connection(self.username, self.password, self.device,
                                                             self.netconf_port)
        if self.session != 'error':
            self.interface_state = self._get_stats()
            self.config = self._get_config()

            # Check for device type. Insures polling only happens with compatable technologies
            if self.model[:3][-2:] != 'SR':
                self._get_trunk_ports()

            # Call methods which collects data from device
            self._get_port_channels()
            self._get_ip_interfaces()
            self._get_prefix_list()
            self._get_qos_interfaces()

        DbOps.copy_db_table(self.device)

    def _get_stats(self, interface=None):

        config = None

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

    def _get_prefix_config(self):

        config = None

        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <ip>
                        <prefix-list/>
                        </ip>
                        </native>
                        </filter>"""

        try:
            intf_info = self.session.get(xml_filter)
            intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
            config = is_instance(intf_dict)
        except (TypeError, AttributeError):
            pass

        return config

    def _get_config(self):
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

    def _get_interface_stats(self, select_int, ip=None):
        """Collect interface statistics"""

        interface_stats = {}
        interface = self._get_stats(select_int)

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

    def _get_ip_interfaces(self):
        """Gets interface ips addresses"""

        interface_info = []
        unassigned_interfaces = ['Tunnel', 'Loopback', 'Vlan']
        interface_num = []

        for ints in self.interface_types:
            try:
                make_ip_list = is_in_list(self.config[0]["native"]["interface"].get(ints))
                for ip in make_ip_list:
                    if ip is None:
                        continue
                    elif ip.get("ip", {}).get("address", {}):
                        address = ipaddress.ip_interface(ip.get('ip', '').get('address').get('primary').get('address') + '/' + ip.get('ip', '').get(
                                'address').get('primary').get('mask'))
                        parsed_info = self._get_interface_stats(ints + ip.get('name'), ip=address)
                        interface_info.append(parsed_info)
                    else:
                        try:
                            parsed_info = self._get_interface_stats(ints + ip.get('name'), ip='Not Assigned')
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
        DbOps.delete_rows('interfaces_back_end', self.device)
        for i in interface_info:
            for k, v in i.items():
                DbOps.update_ip_interface_table(self.device, k, str(v['IP']) + ' | ' + v['MAC'], v['Admin'],
                                                v['Operational'], v['Speed'],
                                                v['Last Change'].split('.')[0], v['In Octets'], v['Out Octets'])

        # Deletes table data
        DbOps.delete_rows('unassignedinterfaces_back_end', self.device)
        for interface in unassigned_interfaces:
            DbOps.update_unassigned_interfaces(self.device, interface)

    def _get_trunk_ports(self):
        """Get access ports"""

        trunks = []

        # Deletes table data
        DbOps.delete_rows('trunks_back_end', self.device)

        for ints in self.interface_types:
            try:
                make_list = is_in_list(self.config[0]["native"]["interface"].get(ints))
                for interface in make_list:
                    if interface is None:
                        continue

                    if interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans",
                                                                                                               {}):
                        # Use netconf interface name to get vlans using netmiko. I find netconf can be untrustworthy sometimes
                        vlans = GetWithNetmiko.netconf_trunk_helper(ints + interface.get('name'), self.username,self.password,
                                                                    self.device)
                        # Write dictionary to list and join our vlan list returned from netmiko funtion
                        trunks.append({'interface': ints + interface.get('name'), 'vlans': ', '.join(vlans),
                                       'cdp': interface.get('name')})
                    elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add",
                                                                                                               {}):
                        # Use netconf interface name to get vlans using netmiko. I find netconf can be untrustworthy sometimes
                        vlans = GetWithNetmiko.netconf_trunk_helper(ints + interface.get('name'), self.username, self.password,
                                                                    self.device)
                        # Write dictionary to list and join our vlan list returned from netmiko funtion
                        trunks.append({'interface': ints + interface.get('name'), 'vlans': ', '.join(vlans),
                                       'cdp': interface.get('name')})
            except TypeError:
                pass

        for interface in trunks:
            for port in self.interface_state:
                if interface.get('interface') == port.get('name'):
                    DbOps.update_trunks_table(self.device, interface['interface'], interface['vlans'],
                                              port.get('admin-status'), port.get('oper-status'))

    def _get_port_channels(self):
        """Get port-channels"""

        port_channels = []

        # Deletes table data
        DbOps.delete_rows('pochannels_back_end', self.device)

        for ints in self.trunk_types:
            try:
                # If data structure is a dict. This funtion with convert to a list. Dictionaries occur when there is one of something returned
                make_list = is_in_list(self._get_config()[0]["native"]["interface"].get(ints))
                for interface in make_list:
                    if interface is None:
                        continue
                    elif interface.get("channel-group", {}).get("number", {}):
                        port_channels.append({'interface': ints + interface.get("name"),
                                              'group': interface.get('channel-group').get('number'),
                                              'mode': interface.get('channel-group').get('mode')})

            except TypeError:
                pass

        for interface in port_channels:
            for port in self.interface_state:
                if interface.get('interface') == port.get('name'):
                    DbOps.update_pochannel_table(self.device, interface['interface'], interface['group'],
                                                 interface['mode'],
                                                 port.get('admin-status'), port.get('oper-status'))

    def _get_qos_interfaces(self):
        """Gets QOS configurations"""

        # Deletes table data
        DbOps.delete_rows('interfaceqos_back_end', self.device)

        for i in is_instance(self.interface_state):
            if i.get("diffserv-target-entry", {}).get("direction", {}):
                for index, stat in enumerate(
                        i.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {})):
                    DbOps.update_qos_table(self.device, i['name'],
                                           i.get('diffserv-target-entry', {}).get('policy-name', {}),
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

    def _get_prefix_list(self):
        """View current prefix-list, match statemnt combinations."""

        DbOps.delete_rows('prefixlist_back_end', self.device)

        config = self._get_prefix_config()
        if config is not None:
            for prefix_list in config:
                try:
                    lists = is_instance(prefix_list.get("seq", {}))
                    for sequence in lists:
                        DbOps.update_prefix_table(self.device, prefix_list.get("name"), sequence.get("no"),
                                                  sequence.get("action"),
                                                  sequence.get("ge", ''), sequence.get("le"))
                except AttributeError:
                    pass
